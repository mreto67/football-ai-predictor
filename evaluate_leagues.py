import json
import glob
import os

from dataset_builder import build_dataset
from match_features import build_match_features
from temporal_split import chronological_split
from baseline_model import train_baseline, evaluate_predictions
from form_model import train_form_model, evaluate_form_predictions
from goal_model import predict_match

DATA_DIR = "data/raw"
LEAGUES = {
    "england": "İngiltere",
    "spain": "İspanya",
    "italy": "İtalya",
    "germany": "Almanya",
    "france": "Fransa",
}


def evaluate(rows):
    if len(rows) < 10:
        return None

    train, test = chronological_split(rows, test_ratio=0.2)
    if not train or not test:
        return None

    baseline = train_baseline(train)
    form = train_form_model(train)

    baseline_metrics = evaluate_predictions(baseline, test)
    form_metrics = evaluate_form_predictions(form, test)

    goal_correct = 0
    totals_correct = 0
    exact_correct = 0
    goal_errors = []

    for row in test:
        prediction = predict_match(row)
        hg = row["home_goals"]
        ag = row["away_goals"]

        goal_errors.extend([
            abs(prediction["expected_home_goals"] - hg),
            abs(prediction["expected_away_goals"] - ag),
        ])

        probabilities = prediction["outcome_probabilities"]
        if max(probabilities, key=probabilities.get) == row["outcome"]:
            goal_correct += 1

        actual_over = hg + ag >= 3
        predicted_over = prediction["over_2_5_probability"] >= 0.5
        if predicted_over == actual_over:
            totals_correct += 1

        if prediction["predicted_score"] == f"{hg}-{ag}":
            exact_correct += 1

    n = len(test)
    return {
        "train": len(train),
        "test": n,
        "start": test[0]["date"],
        "end": test[-1]["date"],
        "baseline": baseline_metrics,
        "form": form_metrics,
        "goal_result": 100 * goal_correct / n,
        "mae": sum(goal_errors) / len(goal_errors),
        "over_under": 100 * totals_correct / n,
        "exact": 100 * exact_correct / n,
    }


def main():
    files = sorted(
        glob.glob(os.path.join(DATA_DIR, "*_2024_25.json"))
    )

    for path in files:
        filename = os.path.basename(path)
        key = filename.split("_")[0]
        league = LEAGUES.get(key, key)

        with open(path, encoding="utf-8") as file:
            source = json.load(file)

        dataset = build_dataset(source.get("matches", []))
        if not dataset:
            print(f"\n{league}: geçerli maç bulunamadı.")
            continue

        featured = build_match_features(dataset)
        result = evaluate(featured)

        print(f"\n=== {league} ===")
        print("Geçerli maç:", len(featured))

        if result is None:
            print("Değerlendirme için yeterli maç yok.")
            continue

        print("Eğitim / test:", result["train"], "/", result["test"])
        print("Test tarihleri:", result["start"], "-", result["end"])
        print("Model                 1X2 doğruluğu   Log loss   Brier")
        print(
            f"Başlangıç modeli      "
            f"{result['baseline']['accuracy'] * 100:6.2f}%"
            f"       {result['baseline']['log_loss']:.4f}"
            f"     {result['baseline']['brier_score']:.4f}"
        )
        print(
            f"Form modeli           "
            f"{result['form']['accuracy'] * 100:6.2f}%"
            f"       {result['form']['log_loss']:.4f}"
            f"     {result['form']['brier_score']:.4f}"
        )
        print(f"Gol modeli            {result['goal_result']:6.2f}%")
        print("Gol MAE:", round(result["mae"], 4))
        print("2.5 üst/alt doğruluğu:", f"{result['over_under']:.2f}%")
        print("Tam skor doğruluğu:", f"{result['exact']:.2f}%")


if __name__ == "__main__":
    main()
