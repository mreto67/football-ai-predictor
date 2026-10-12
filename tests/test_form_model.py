import unittest

from form_model import train_form_model, predict_form_probabilities


def row(home_avg, away_avg, home_conceded, away_conceded, outcome):
    return {
        "home_goals_scored_avg": home_avg,
        "away_goals_scored_avg": away_avg,
        "home_goals_conceded_avg": home_conceded,
        "away_goals_conceded_avg": away_conceded,
        "outcome": outcome,
    }


class FormModelTests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            row(2.2, 0.7, 0.8, 1.8, "1"),
            row(2.0, 0.9, 0.7, 1.7, "1"),
            row(0.8, 2.1, 1.8, 0.8, "2"),
            row(0.9, 2.0, 1.7, 0.7, "2"),
            row(1.2, 1.1, 1.1, 1.2, "X"),
            row(1.3, 1.2, 1.0, 1.1, "X"),
        ]

    def test_training_requires_all_outcomes(self):
        with self.assertRaises(ValueError):
            train_form_model(self.rows[:2])

    def test_probabilities_are_valid(self):
        model = train_form_model(self.rows)
        probabilities = predict_form_probabilities(
            model,
            row(2.0, 0.8, 0.7, 1.8, "1"),
        )

        self.assertEqual(set(probabilities), {"1", "X", "2"})
        self.assertTrue(all(0 <= p <= 1 for p in probabilities.values()))
        self.assertAlmostEqual(sum(probabilities.values()), 1.0, places=8)

    def test_input_rows_are_not_modified(self):
        original = [item.copy() for item in self.rows]
        train_form_model(self.rows)
        self.assertEqual(self.rows, original)


if __name__ == "__main__":
    unittest.main()
