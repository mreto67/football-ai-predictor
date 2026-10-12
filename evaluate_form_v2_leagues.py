import json
from pathlib import Path

from dataset_builder import build_dataset
from match_features import build_match_features
from temporal_split import chronological_split
from form_model import train_form_model as train_old
from form_model import evaluate_form_predictions as evaluate_old
from form_model_v2 import train_form_model as train_v2
from form_model_v2 import evaluate_form_predictions as evaluate_v2

FILES = {
    "England": "data/raw/england_2024_25.json",
    "Spain": "data/raw/spain_2024_25.json",
    "Italy": "data/raw/italy_2024_25.json",
    "Germany": "data/raw/germany_2024_25.json",
    "France": "data/raw/france_2024_25.json",
}


def load_rows(path):
    with open(path, encoding="utf-8") as file:
        raw = json.load(file)

    matches = raw["matches"] if isinstance(raw, dict) else raw
    rows = build_dataset(matches)
    return build_match_features(rows)


def main():
    for league, path in FILES.items():
        if not Path(path).exists():
            print(f"\n{league}: veri dosyası bulunamadı: {path}")
            continue

        rows = load_rows(path)
        train_rows, test_rows = chronological_split(rows)

        old_model = train_old(train_rows)
        new_model = train_v2(train_rows)

        old_metrics = evaluate_old(old_model, test_rows)
        new_metrics = evaluate_v2(new_model, test_rows)

        print(f"\n{league} — test maçları: {len(test_rows)}")
        print(
            f"Eski model: doğruluk %{old_metrics['accuracy'] * 100:.2f} | "
            f"log loss {old_metrics['log_loss']:.4f} | "
            f"Brier {old_metrics['brier_score']:.4f}"
        )
        print(
            f"Yeni model: doğruluk %{new_metrics['accuracy'] * 100:.2f} | "
            f"log loss {new_metrics['log_loss']:.4f} | "
            f"Brier {new_metrics['brier_score']:.4f}"
        )


if __name__ == "__main__":
    main()
