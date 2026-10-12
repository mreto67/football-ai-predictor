import unittest

from baseline_model import (
    evaluate_predictions,
    predict_probabilities,
    train_baseline,
)


def make_row(date, home, away, home_avg, away_avg, outcome):
    return {
        "date": date,
        "home_team": home,
        "away_team": away,
        "home_matches_before": 5,
        "away_matches_before": 5,
        "home_goals_scored_avg": home_avg,
        "away_goals_scored_avg": away_avg,
        "home_goals_conceded_avg": 1.0,
        "away_goals_conceded_avg": 1.0,
        "outcome": outcome,
    }


class BaselineModelTests(unittest.TestCase):
    def setUp(self):
        self.train = [
            make_row("2024-08-01", "A", "B", 2.0, 0.8, "1"),
            make_row("2024-08-02", "C", "D", 0.7, 1.8, "2"),
            make_row("2024-08-03", "E", "F", 1.2, 1.2, "X"),
            make_row("2024-08-04", "G", "H", 2.1, 0.9, "1"),
            make_row("2024-08-05", "I", "J", 0.8, 1.9, "2"),
            make_row("2024-08-06", "K", "L", 1.1, 1.0, "X"),
        ]

    def test_training_requires_all_three_outcomes(self):
        with self.assertRaises(ValueError):
            train_baseline(self.train[:2])

    def test_prediction_probabilities_are_valid(self):
        model = train_baseline(self.train)
        probabilities = predict_probabilities(
            model,
            make_row("2024-08-10", "A", "B", 1.8, 0.9, "1"),
        )

        self.assertEqual(set(probabilities), {"1", "X", "2"})
        self.assertTrue(all(0 <= p <= 1 for p in probabilities.values()))
        self.assertAlmostEqual(sum(probabilities.values()), 1.0, places=8)

    def test_evaluation_returns_metrics(self):
        model = train_baseline(self.train)
        results = evaluate_predictions(model, self.train)

        self.assertIn("accuracy", results)
        self.assertIn("log_loss", results)
        self.assertIn("brier_score", results)
        self.assertGreaterEqual(results["accuracy"], 0)
        self.assertLessEqual(results["accuracy"], 1)
        self.assertGreaterEqual(results["log_loss"], 0)
        self.assertGreaterEqual(results["brier_score"], 0)

    def test_training_does_not_modify_input(self):
        original = [row.copy() for row in self.train]

        train_baseline(self.train)

        self.assertEqual(self.train, original)


if __name__ == "__main__":
    unittest.main()
