import unittest

from team_aliases import canonical_team_name, resolve_team_name


class TeamAliasesTests(unittest.TestCase):
    def test_known_aliases_resolve_to_same_canonical_name(self):
        self.assertEqual(
            canonical_team_name("Man United"),
            canonical_team_name("Manchester United"),
        )

    def test_alias_matching_ignores_case_and_outer_spaces(self):
        self.assertEqual(
            canonical_team_name("  MAN UNITED "),
            canonical_team_name("Manchester United"),
        )

    def test_unknown_team_name_is_preserved_after_normalization(self):
        self.assertEqual(resolve_team_name("Unknown FC"), "unknown fc")

    def test_empty_or_non_string_name_returns_empty_string(self):
        self.assertEqual(resolve_team_name("   "), "")
        self.assertEqual(resolve_team_name(None), "")

    def test_source_alias_table_does_not_change_input(self):
        source_name = "  Man United "
        resolve_team_name(source_name)
        self.assertEqual(source_name, "  Man United ")


if __name__ == "__main__":
    unittest.main()
