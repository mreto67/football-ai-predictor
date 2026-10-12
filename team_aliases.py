from historical_importer import normalize_team_name


TEAM_ALIASES = {
    "man united": "manchester united",
    "manchester united": "manchester united",
}


def canonical_team_name(name):
    normalized = normalize_team_name(name)
    if not normalized:
        return ""
    return TEAM_ALIASES.get(normalized, normalized)


def resolve_team_name(name):
    return canonical_team_name(name)
