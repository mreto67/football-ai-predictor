import json
from pathlib import Path
from dataset_builder import build_dataset
from match_features import build_match_features
from temporal_split import chronological_split
from baseline_model import train_baseline, evaluate_predictions
from form_model import train_form_model, evaluate_form_predictions
from goal_model import predict_match

old_dir = Path("data/raw/2023_24_openfootball")
new_dir = Path("data/raw")

for league in ("england", "spain"):
    def load(path):
        with path.open(encoding="utf-8") as f:
            return build_dataset(json.load(f).get("matches", []))

    old = load(old_dir / f"{league}_2023_24.json")
    new = load(new_dir / f"{league}_2024_25.json")
    train = build_match_features(old)
    test = build_match_features(new)

    baseline = train_baseline(train)
    form = train_form_model(train)
    bm = evaluate_predictions(baseline, test)
    fm = evaluate_form_predictions(form, test)

    correct = over = exact = 0
    errors = []

    for r in test:
        p = predict_match(r)
        hg, ag = r["home_goals"], r["away_goals"]
        correct += max(p["outcome_probabilities"],
                       key=p["outcome_probabilities"].get) == r["outcome"]
        over += (p["over_2_5_probability"] >= 0.5) == (hg + ag >= 3)
        exact += p["predicted_score"] == f"{hg}-{ag}"
        errors.extend([abs(p["expected_home_goals"] - hg),
                       abs(p["expected_away_goals"] - ag)])

    n = len(test)
    print(f"\n=== {league.upper()} ===")
    print("Eğitim:", len(train), "| Test:", n)
    print(f"Başlangıç: %{bm['accuracy']*100:.2f} | Log loss {bm['log_loss']:.4f}")
    print(f"Form:      %{fm['accuracy']*100:.2f} | Log loss {fm['log_loss']:.4f}")
    print(f"Gol 1X2:   %{100*correct/n:.2f}")
    print(f"Gol MAE:   {sum(errors)/len(errors):.4f}")
    print(f"Üst/alt:   %{100*over/n:.2f}")
    print(f"Tam skor:  %{100*exact/n:.2f}")
