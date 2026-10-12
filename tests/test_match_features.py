import unittest

from match_features import build_match_features


def make_match(date, home, away, hg, ag):
    return {
        "date": date,
        "home_team": home,
        "away_team": away,
        "home_goals": hg,
        "away_goals": ag,
        "outcome": (
            "1" if hg > ag else "X" if hg == ag else "2"
        ),
    }


class MatchFeatureTests(unittest.TestCase):
    def test_first_match_has_no_prior_history(self):
        matches = [
            make_match("2024-08-01", "Arsenal", "Chelsea", 2, 1),
        ]

        rows = build_match_features(matches)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["home_matches_before"], 0)
        self.assertEqual(rows[0]["away_matches_before"], 0)
        self.assertEqual(rows[0]["home_goals_scored_avg"], 0.0)
        self.assertEqual(rows[0]["away_goals_scored_avg"], 0.0)

    def test_features_use_only_earlier_matches(self):
        matches = [
            make_match("2024-08-01", "Arsenal", "Chelsea", 2, 1),
            make_match("2024-08-08", "Arsenal", "Liverpool", 1, 0),
            make_match("2024-08-15", "Chelsea", "Arsenal", 3, 0),
        ]

        rows = build_match_features(matches)
        last = rows[-1]

        self.assertEqual(last["date"], "2024-08-15")
        self.assertEqual(last["home_matches_before"], 1)
        self.assertEqual(last["away_matches_before"], 2)
        self.assertEqual(last["home_goals_scored_avg"], 1.0)
        self.assertEqual(last["away_goals_scored_avg"], 1.5)

    def test_matches_on_same_date_do_not_leak_into_each_other(self):
        matches = [
            make_match("2024-08-01", "Arsenal", "Chelsea", 2, 1),
            make_match("2024-08-08", "Arsenal", "Liverpool", 4, 0),
            make_match("2024-08-08", "Chelsea", "Everton", 3, 0),
        ]

        rows = build_match_features(matches)
        same_day = [r for r in rows if r["date"] == "2024-08-08"]

        arsenal_match = next(
            r for r in same_day if r["away_team"] == "Liverpool"
        )
        chelsea_match = next(
            r for r in same_day if r["home_team"] == "Chelsea"
        )

        self.assertEqual(arsenal_match["home_matches_before"], 1)
        self.assertEqual(chelsea_match["home_matches_before"], 1)

    def test_output_preserves_match_scores_and_outcome(self):
        matches = [make_match("2024-08-01", "Arsenal", "Chelsea", 2, 1)]
        row = build_match_features(matches)[0]
        self.assertEqual(row["home_goals"], 2)
        self.assertEqual(row["away_goals"], 1)
        self.assertEqual(row["outcome"], "1")

    def test_input_matches_are_not_modified(self):
        matches = [
            make_match("2024-08-02", "Arsenal", "Chelsea", 2, 1),
            make_match("2024-08-01", "Liverpool", "Everton", 1, 1),
        ]
        original = [row.copy() for row in matches]

        build_match_features(matches)

        self.assertEqual(matches, original)


if __name__ == "__main__":
    unittest.main()

    def test_last_five_features_use_only_previous_matches(self):
        matches = [
            make_match("2024-08-01", "Arsenal", "Chelsea", 2, 1),
            make_match("2024-08-02", "Arsenal", "Everton", 4, 0),
            make_match("2024-08-03", "Arsenal", "Brighton", 1, 1),
            make_match("2024-08-04", "Arsenal", "West Ham", 3, 2),
            make_match("2024-08-05", "Arsenal", "Newcastle", 0, 1),
            make_match("2024-08-06", "Arsenal", "Liverpool", 5, 0),
        ]

        rows = build_match_features(matches)
        last = rows[-1]

        self.assertIn("home_last5_goals_scored_avg", last)
        self.assertIn("home_last5_goals_conceded_avg", last)
        self.assertAlmostEqual(last["home_last5_goals_scored_avg"], 2.0)
        self.assertAlmostEqual(last["home_last5_goals_conceded_avg"], 1.0)

    def test_last_five_features_are_zero_without_history(self):
        matches = [
            make_match("2024-08-01", "Arsenal", "Chelsea", 2, 1),
        ]

        row = build_match_features(matches)[0]

        self.assertEqual(row["home_last5_goals_scored_avg"], 0.0)
        self.assertEqual(row["home_last5_goals_conceded_avg"], 0.0)
        self.assertEqual(row["away_last5_goals_scored_avg"], 0.0)
        self.assertEqual(row["away_last5_goals_conceded_avg"], 0.0)
