import unittest

from historical_importer import audit_matches, dry_run


class HistoricalImporterTests(unittest.TestCase):
    def test_counts_valid_and_missing_scores(self):
        matches = [
            {
                "date": "2024-08-16",
                "team1": "Team A",
                "team2": "Team B",
                "score": {"ft": [2, 1]},
            },
            {
                "date": "2024-08-17",
                "team1": "Team C",
                "team2": "Team D",
                "score": {},
            },
        ]

        report = audit_matches(matches)

        self.assertEqual(report["total"], 2)
        self.assertEqual(report["scored"], 1)
        self.assertEqual(report["missing_scores"], 1)
        self.assertEqual(report["invalid_dates"], 0)
        self.assertEqual(report["eligible"], 1)

    def test_dry_run_never_writes_data(self):
        matches = [
            {
                "date": "2024-08-16",
                "team1": "Team A",
                "team2": "Team B",
                "score": {"ft": [2, 1]},
            }
        ]

        result = dry_run(matches)

        self.assertTrue(result["dry_run"])
        self.assertEqual(result["would_process"], 1)
        self.assertFalse(result["written"])

    def test_duplicate_match_is_detected(self):
        match = {
            "date": "2024-08-16",
            "team1": "Team A",
            "team2": "Team B",
            "score": {"ft": [2, 1]},
        }

        report = audit_matches([match, match])

        self.assertEqual(report["duplicates"], 1)
        self.assertEqual(report["eligible"], 1)

    def test_invalid_score_is_not_counted_as_scored(self):
        matches = [
            {
                "date": "2024-08-16",
                "team1": "Team A",
                "team2": "Team B",
                "score": {"ft": [-1, 2]},
            }
        ]

        report = audit_matches(matches)

        self.assertEqual(report["scored"], 0)
        self.assertEqual(report["invalid_scores"], 1)


    def test_invalid_date_is_not_eligible(self):
        match = {
            "date": "not-a-date",
            "team1": "Team A",
            "team2": "Team B",
            "score": {"ft": [1, 0]},
        }
        report = audit_matches([match])
        self.assertEqual(report["invalid_dates"], 1)
        self.assertEqual(report["eligible"], 0)

    def test_missing_team_is_not_eligible(self):
        match = {
            "date": "2024-08-16",
            "team1": "",
            "team2": "Team B",
            "score": {"ft": [1, 0]},
        }
        report = audit_matches([match])
        self.assertEqual(report["eligible"], 0)



    def test_cli_rejects_invalid_league(self):
        import subprocess
        import sys

        result = subprocess.run(
            [
                sys.executable,
                "historical_importer.py",
                "--league",
                "turkey",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("invalid choice", result.stderr)


    def test_network_error_is_reported(self):
        from unittest.mock import patch
        import io
        import contextlib
        import urllib.error
        from historical_importer import main

        output = io.StringIO()
        with patch(
            "urllib.request.urlopen",
            side_effect=urllib.error.URLError("offline"),
        ):
            with patch("sys.argv", ["historical_importer.py", "--league", "england"]):
                with contextlib.redirect_stdout(output):
                    main()

        self.assertIn("HATA: URLError", output.getvalue())
        self.assertIn("offline", output.getvalue())


    def test_missing_season_file_is_reported(self):
        from unittest.mock import patch
        import io
        import contextlib
        import urllib.error
        from historical_importer import main

        output = io.StringIO()
        error = urllib.error.HTTPError(
            "https://example.com/missing.json",
            404,
            "Not Found",
            {},
            None,
        )
        with patch("urllib.request.urlopen", side_effect=error):
            with patch(
                "sys.argv",
                ["historical_importer.py", "--league", "england"],
            ):
                with contextlib.redirect_stdout(output):
                    main()

        self.assertIn("HATA: HTTPError", output.getvalue())
        self.assertIn("404", output.getvalue())

if __name__ == "__main__":
    unittest.main()
