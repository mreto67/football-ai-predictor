import unittest

from form_model_v2 import (
    train_form_model,
    predict_form_probabilities,
)


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


def make_row(values, outcome):
    row = dict(zip(FEATURES, values))
    row["outcome"] = outcome
    return row


class FormModelV2Tests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            make_row([2.2, 0.7, 0.8, 1.8, 2.4, 0.8, 0.6, 1.8], "1"),
            make_row([2.0, 0.9, 0.7, 1.7, 2.2, 0.6, 0.8, 1.6], "1"),
            make_row([0.8, 2.1, 1.8, 0.8, 0.8, 1.8, 2.2, 0.8], "2"),
            make_row([0.9, 2.0, 1.7, 0.7, 0.7, 1.6, 2.0, 0.7], "2"),
            make_row([1.2, 1.1, 1.1, 1.2, 1.2, 1.1, 1.1, 1.2], "X"),
            make_row([1.3, 1.2, 1.0, 1.1, 1.3, 1.0, 1.2, 1.1], "X"),
        ]

    def test_training_requires_all_outcomes(self):
        with self.assertRaises(ValueError):
            train_form_model(self.rows[:2])

    def test_probabilities_are_valid(self):
        model = train_form_model(self.rows)
        probabilities = predict_form_probabilities(
            model,
            self.rows[0],
        )
        self.assertEqual(set(probabilities), {"1", "X", "2"})
        self.assertTrue(all(0 <= p <= 1 for p in probabilities.values()))
        self.assertAlmostEqual(sum(probabilities.values()), 1.0, places=8)

    def test_input_rows_are_not_modified(self):
        original = [item.copy() for item in self.rows]
        train_form_model(self.rows)
        self.assertEqual(self.rows, original)

    def test_missing_recent_form_feature_is_rejected(self):
        model = train_form_model(self.rows)
        incomplete = self.rows[0].copy()
        del incomplete["home_last5_goals_scored_avg"]
        with self.assertRaises(ValueError):
            predict_form_probabilities(model, incomplete)


if __name__ == "__main__":
    unittest.main()
