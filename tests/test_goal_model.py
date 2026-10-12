import unittest

from goal_model import predict_match


class GoalModelTests(unittest.TestCase):
    def setUp(self):
        self.home = {
            "home_goals_scored_avg": 1.8,
            "home_goals_conceded_avg": 0.9,
            "away_goals_scored_avg": 1.1,
            "away_goals_conceded_avg": 1.4,
        }

    def test_returns_required_prediction_fields(self):
        result = predict_match(self.home)

        self.assertIn("expected_home_goals", result)
        self.assertIn("expected_away_goals", result)
        self.assertIn("predicted_score", result)
        self.assertIn("outcome_probabilities", result)
        self.assertIn("over_2_5_probability", result)
        self.assertIn("under_2_5_probability", result)

    def test_probabilities_are_valid(self):
        result = predict_match(self.home)
        outcomes = result["outcome_probabilities"]

        self.assertEqual(set(outcomes), {"1", "X", "2"})
        self.assertTrue(all(0 <= p <= 1 for p in outcomes.values()))
        self.assertAlmostEqual(sum(outcomes.values()), 1.0, places=8)
        self.assertAlmostEqual(
            result["over_2_5_probability"]
            + result["under_2_5_probability"],
            1.0,
            places=8,
        )

    def test_expected_goals_are_positive(self):
        result = predict_match(self.home)

        self.assertGreater(result["expected_home_goals"], 0)
        self.assertGreater(result["expected_away_goals"], 0)

    def test_invalid_input_is_rejected(self):
        with self.assertRaises(ValueError):
            predict_match({"home_goals_scored_avg": -1})


if __name__ == "__main__":
    unittest.main()
