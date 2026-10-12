from datetime import date


def _score_value(match):
    score = match.get("score")

    if isinstance(score, dict):
        score = score.get("ft")

    if score is None or score == {}:
        return None

    if (
        isinstance(score, list)
        and len(score) == 2
        and all(
            isinstance(value, int)
            and not isinstance(value, bool)
            and value >= 0
            for value in score
        )
    ):
        return score

    return "INVALID"


def audit_matches(matches):
    report = {
        "total": len(matches),
        "scored": 0,
        "missing_scores": 0,
        "invalid_scores": 0,
        "invalid_dates": 0,
        "duplicates": 0,
        "eligible": 0,
    }
    seen = set()

    for match in matches:
        match_date = match.get("date")
        home = match.get("team1")
        away = match.get("team2")

        try:
            date.fromisoformat(match_date)
            valid_date = True
        except (ValueError, TypeError):
            valid_date = False

        valid_teams = (
            isinstance(home, str)
            and bool(home.strip())
            and isinstance(away, str)
            and bool(away.strip())
            and home.strip().casefold() != away.strip().casefold()
        )

        if not valid_date:
            report["invalid_dates"] += 1

        score = _score_value(match)

        if score is None:
            report["missing_scores"] += 1
        elif score == "INVALID":
            report["invalid_scores"] += 1
        else:
            report["scored"] += 1

        if not valid_date or not valid_teams:
            continue

        key = (
            match_date,
            home.strip().casefold(),
            away.strip().casefold(),
        )

        if key in seen:
            report["duplicates"] += 1
            continue

        seen.add(key)

        if score is not None and score != "INVALID":
            report["eligible"] += 1

    return report


def dry_run(matches):
    report = audit_matches(matches)
    return {
        "dry_run": True,
        "would_process": report["eligible"],
        "written": False,
        "report": report,
    }
