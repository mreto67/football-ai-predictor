import unittest

from temporal_split import chronological_split


def make_rows(dates):
    return [
        {
            "date": match_date,
            "home_team": f"home-{i}",
            "away_team": f"away-{i}",
            "home_goals": 1,
            "away_goals": 0,
            "outcome": "1",
        }
        for i, match_date in enumerate(dates)
    ]


class ChronologicalSplitTests(unittest.TestCase):
    def test_splits_in_date_order(self):
        rows = make_rows([
            "2024-08-05",
            "2024-08-01",
            "2024-08-04",
            "2024-08-02",
            "2024-08-03",
        ])

        train, test = chronological_split(rows, test_ratio=0.2)

        self.assertEqual([r["date"] for r in train], [
            "2024-08-01",
            "2024-08-02",
            "2024-08-03",
            "2024-08-04",
        ])
        self.assertEqual([r["date"] for r in test], ["2024-08-05"])

    def test_same_date_is_never_split_between_sets(self):
        rows = make_rows([
            "2024-08-01",
            "2024-08-02",
            "2024-08-03",
            "2024-08-03",
            "2024-08-04",
        ])

        train, test = chronological_split(rows, test_ratio=0.4)

        train_dates = {r["date"] for r in train}
        test_dates = {r["date"] for r in test}

        self.assertFalse(train_dates & test_dates)
        self.assertLess(max(train_dates), min(test_dates))

    def test_invalid_test_ratio_is_rejected(self):
        rows = make_rows(["2024-08-01", "2024-08-02"])

        for ratio in (0, 1, -0.1, 1.1):
            with self.subTest(ratio=ratio):
                with self.assertRaises(ValueError):
                    chronological_split(rows, test_ratio=ratio)

    def test_too_few_rows_is_rejected(self):
        with self.assertRaises(ValueError):
            chronological_split(make_rows(["2024-08-01"]), test_ratio=0.2)

    def test_input_rows_are_not_modified(self):
        rows = make_rows([
            "2024-08-02",
            "2024-08-01",
            "2024-08-03",
        ])
        original = [row.copy() for row in rows]

        chronological_split(rows, test_ratio=1 / 3)

        self.assertEqual(rows, original)


if __name__ == "__main__":
    unittest.main()
