"""Tarihsel maç kayıtlarından güvenli 1/X/2 eğitim satırları üretir."""

from datetime import date

from historical_importer import _score_value
from team_aliases import canonical_team_name


def build_dataset(matches):
    """Geçerli ve benzersiz maçlardan bellek içi 1/X/2 veri kümesi üretir."""
    rows = []
    seen = set()

    for match in matches:
        if not isinstance(match, dict):
            continue

        match_date = match.get("date")
        home = match.get("team1")
        away = match.get("team2")

        try:
            date.fromisoformat(match_date)
        except (ValueError, TypeError):
            continue

        if not isinstance(home, str) or not home.strip():
            continue
        if not isinstance(away, str) or not away.strip():
            continue

        home_name = canonical_team_name(home)
        away_name = canonical_team_name(away)

        if not home_name or not away_name or home_name == away_name:
            continue

        score = _score_value(match)
        if not isinstance(score, list):
            continue

        key = (match_date, home_name, away_name)
        if key in seen:
            continue
        seen.add(key)

        home_goals, away_goals = score
        if home_goals > away_goals:
            outcome = "1"
        elif home_goals == away_goals:
            outcome = "X"
        else:
            outcome = "2"

        rows.append({
            "date": match_date,
            "home_team": home_name,
            "away_team": away_name,
            "home_goals": home_goals,
            "away_goals": away_goals,
            "outcome": outcome,
        })

    rows.sort(key=lambda row: (
        row["date"], row["home_team"], row["away_team"]
    ))
    return rows
