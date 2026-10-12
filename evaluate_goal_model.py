import json
from goal_model import predict_match
from temporal_split import chronological_split


DATA_PATH = "data/processed/matches_5_leagues_2024_25.json"


def main():
    with open(DATA_PATH, encoding="utf-8") as file:
        rows = json.load(file)

    train_rows, test_rows = chronological_split(rows, test_ratio=0.2)

    goal_errors = []
    outcome_correct = 0
    over_under_correct = 0
    exact_score_correct = 0
    evaluated = 0

    for row in test_rows:
        prediction = predict_match(row)

        actual_home = row["home_goals"]
        actual_away = row["away_goals"]

        predicted_home = prediction["expected_home_goals"]
        predicted_away = prediction["expected_away_goals"]

        goal_errors.append(abs(predicted_home - actual_home))
        goal_errors.append(abs(predicted_away - actual_away))

        probabilities = prediction["outcome_probabilities"]
        predicted_outcome = max(probabilities, key=probabilities.get)

        if predicted_outcome == row["outcome"]:
            outcome_correct += 1

        actual_over = actual_home + actual_away >= 3
        predicted_over = prediction["over_2_5_probability"] >= 0.5

        if predicted_over == actual_over:
            over_under_correct += 1

        actual_score = f"{actual_home}-{actual_away}"

        if prediction["predicted_score"] == actual_score:
            exact_score_correct += 1

        evaluated += 1

    print("=== GOL MODELİ DEĞERLENDİRMESİ ===")
    print("Eğitim maçları:", len(train_rows))
    print("Test maçları:", evaluated)
    print("Test dönemi:", test_rows[0]["date"], "-", test_rows[-1]["date"])
    print("Gol başına ortalama mutlak hata (MAE):",
          round(sum(goal_errors) / len(goal_errors), 4))
    print("1X2 doğruluğu:",
          f"{outcome_correct / evaluated * 100:.2f}%")
    print("2.5 üst/alt doğruluğu:",
          f"{over_under_correct / evaluated * 100:.2f}%")
    print("Tam skor doğruluğu:",
          f"{exact_score_correct / evaluated * 100:.2f}%")


if __name__ == "__main__":
    main()
