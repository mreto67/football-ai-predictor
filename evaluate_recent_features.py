from pathlib import Path

from evaluate_form_v2_leagues import FILES, load_rows
from temporal_split import chronological_split
from form_model_v2 import train_form_model as train_v2, evaluate_form_predictions

FEATURES = (
    "home_goals_scored_avg",
    "away_goals_scored_avg",
    "home_goals_conceded_avg",
    "away_goals_conceded_avg",
    "home_last5_goals_scored_avg",
    "home_last5_goals_conceded_avg",
    "away_last5_goals_scored_avg",
    "away_last5_goals_conceded_avg",
)

RECENT_FEATURES = FEATURES[4:]


def select_features(rows, features):
    selected = []
    for row in rows:
        item = {feature: row[feature] for feature in features}
        item["outcome"] = row["outcome"]
        selected.append(item)
    return selected


def main():
    for league, path in FILES.items():
        if not Path(path).exists():
            continue

        rows = load_rows(path)
        train_rows, test_rows = chronological_split(rows)

        print(f"\n{league} — test maçları: {len(test_rows)}")

        experiments = [
            ("Sezon özellikleri", FEATURES[:4]),
        ]

        for feature in RECENT_FEATURES:
            experiments.append((f"+ {feature}", FEATURES[:4] + (feature,)))

        for name, features in experiments:
            train = select_features(train_rows, features)
            test = select_features(test_rows, features)

            # Model sekiz özelliği beklediğinden, seçilmeyen özellikleri
            # sabit 0.0 yaparak her deneyi aynı model arayüzünde çalıştır.
            all_train = []
            all_test = []
            for row in train:
                item = {feature: 0.0 for feature in FEATURES}
                item.update(row)
                all_train.append(item)
            for row in test:
                item = {feature: 0.0 for feature in FEATURES}
                item.update(row)
                all_test.append(item)

            model = train_v2(all_train)
            metrics = evaluate_form_predictions(model, all_test)

            print(
                f"{name}: doğruluk %{metrics['accuracy'] * 100:.2f} | "
                f"log loss {metrics['log_loss']:.4f} | "
                f"Brier {metrics['brier_score']:.4f}"
            )


if __name__ == "__main__":
    main()
