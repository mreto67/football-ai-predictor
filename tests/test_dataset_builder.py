import unittest
from copy import deepcopy

from dataset_builder import build_dataset


class DatasetBuilderTests(unittest.TestCase):
    def test_home_win_draw_and_away_win(self):
        matches = [
            {
                "date": "2024-08-16",
                "team1": "Arsenal FC",
                "team2": "Chelsea FC",
                "score": {"ft": [2, 0]},
            },
            {
                "date": "2024-08-17",
                "team1": "Liverpool FC",
                "team2": "Everton FC",
                "score": {"ft": [1, 1]},
            },
            {
                "date": "2024-08-18",
                "team1": "Brighton",
                "team2": "Manchester City",
                "score": {"ft": [0, 3]},
            },
        ]

        rows = build_dataset(matches)

        self.assertEqual(
            [row["outcome"] for row in rows],
            ["1", "X", "2"],
        )

    def test_missing_and_invalid_scores_are_excluded(self):
        matches = [
            {
                "date": "2024-08-16",
                "team1": "Arsenal FC",
                "team2": "Chelsea FC",
                "score": {},
            },
            {
                "date": "2024-08-17",
                "team1": "Liverpool FC",
                "team2": "Everton FC",
                "score": {"ft": [1, -1]},
            },
        ]

        self.assertEqual(build_dataset(matches), [])

    def test_alias_duplicates_are_removed(self):
        matches = [
            {
                "date": "2024-08-16",
                "team1": "Man United",
                "team2": "Arsenal FC",
                "score": {"ft": [2, 1]},
            },
            {
                "date": "2024-08-16",
                "team1": "Manchester United FC",
                "team2": "Arsenal FC",
                "score": {"ft": [2, 1]},
            },
        ]

        rows = build_dataset(matches)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["outcome"], "1")

    def test_invalid_dates_and_team_names_are_excluded(self):
        matches = [
            {
                "date": "not-a-date",
                "team1": "Arsenal FC",
                "team2": "Chelsea FC",
                "score": {"ft": [2, 0]},
            },
            {
                "date": "2024-08-16",
                "team1": "",
                "team2": "Chelsea FC",
                "score": {"ft": [2, 0]},
            },
            {
                "date": "2024-08-16",
                "team1": "Arsenal FC",
                "team2": "Arsenal FC",
                "score": {"ft": [2, 0]},
            },
        ]

        self.assertEqual(build_dataset(matches), [])

    def test_source_records_are_not_modified(self):
        matches = [
            {
                "date": "2024-08-16",
                "team1": "  Man United  ",
                "team2": "Arsenal FC",
                "score": {"ft": [2, 1]},
            }
        ]
        original = deepcopy(matches)

        build_dataset(matches)

        self.assertEqual(matches, original)

    def test_rows_are_sorted_chronologically(self):
        matches = [
            {
                "date": "2024-08-18",
                "team1": "Brighton",
                "team2": "Manchester City",
                "score": {"ft": [0, 3]},
            },
            {
                "date": "2024-08-16",
                "team1": "Arsenal FC",
                "team2": "Chelsea FC",
                "score": {"ft": [2, 0]},
            },
        ]

        rows = build_dataset(matches)

        self.assertEqual(
            [row["date"] for row in rows],
            ["2024-08-16", "2024-08-18"],
        )


if __name__ == "__main__":
    unittest.main()
