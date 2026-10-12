import json
from baseline_model import train_baseline, evaluate_predictions
from form_model import train_form_model, evaluate_form_predictions
from goal_model import predict_match
from temporal_split import chronological_split
from match_features import build_match_features

DATA_PATH = "data/processed/matches_5_leagues_2024_25.json"


def main():
    with open(DATA_PATH, encoding="utf-8") as file:
        rows = json.load(file)

    rows = build_match_features(rows)
    train_rows, test_rows = chronological_split(rows, test_ratio=0.2)

    baseline = train_baseline(train_rows)
    form = train_form_model(train_rows)

    baseline_metrics = evaluate_predictions(baseline, test_rows)
    form_metrics = evaluate_form_predictions(form, test_rows)

    goal_correct = 0
    over_under_correct = 0
    exact_score_correct = 0
    goal_errors = []

    for row in test_rows:
        prediction = predict_match(row)
        actual_home = row["home_goals"]
        actual_away = row["away_goals"]

        goal_errors.extend([
            abs(prediction["expected_home_goals"] - actual_home),
            abs(prediction["expected_away_goals"] - actual_away),
        ])

        probabilities = prediction["outcome_probabilities"]
        if max(probabilities, key=probabilities.get) == row["outcome"]:
            goal_correct += 1

        actual_over = actual_home + actual_away >= 3
        predicted_over = prediction["over_2_5_probability"] >= 0.5
        if predicted_over == actual_over:
            over_under_correct += 1

        if prediction["predicted_score"] == f"{actual_home}-{actual_away}":
            exact_score_correct += 1

    count = len(test_rows)

    print("=== AYNI TEST KÜMESİNDE MODEL KARŞILAŞTIRMASI ===")
    print("Eğitim maçı:", len(train_rows))
    print("Test maçı:", count)
    print("Test dönemi:", test_rows[0]["date"], "-", test_rows[-1]["date"])
    print()
    print("Model                 1X2 doğruluğu   Log loss   Brier skoru")
    print(
        f"Başlangıç modeli      {baseline_metrics['accuracy'] * 100:6.2f}%"
        f"       {baseline_metrics['log_loss']:.4f}"
        f"     {baseline_metrics['brier_score']:.4f}"
    )
    print(
        f"Form modeli           {form_metrics['accuracy'] * 100:6.2f}%"
        f"       {form_metrics['log_loss']:.4f}"
        f"     {form_metrics['brier_score']:.4f}"
    )
    print(f"Gol modeli            {goal_correct / count * 100:6.2f}%")
    print()
    print("Gol modeli MAE:", round(sum(goal_errors) / len(goal_errors), 4))
    print("Gol modeli 2.5 üst/alt doğruluğu:",
          f"{over_under_correct / count * 100:.2f}%")
    print("Gol modeli tam skor doğruluğu:",
          f"{exact_score_correct / count * 100:.2f}%")


if __name__ == "__main__":
    main()
