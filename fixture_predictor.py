"""2026-27 fiksturleri icin guvenli temel tahmin uretimi."""

import argparse
import json
from collections import defaultdict
from pathlib import Path

from goal_model import predict_match
from team_aliases import canonical_team_name

LEAGUES = ("england", "spain", "italy", "germany", "france")
HISTORY_SEASON = "2024_25"
FIXTURE_SEASON = "2026_27"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_team_stats(league):
    path = Path("data/raw") / f"{league}_{HISTORY_SEASON}.json"
    data = read_json(path)
    stats = defaultdict(
        lambda: {"matches": 0, "scored": 0, "conceded": 0}
    )
    total_goals = 0
    total_appearances = 0

    for match in data.get("matches", []):
        score = match.get("score")
        score = score.get("ft") if isinstance(score, dict) else None

        if (
            not isinstance(score, list)
            or len(score) != 2
            or any(
                not isinstance(g, int) or isinstance(g, bool) or g < 0
                for g in score
            )
        ):
            continue

        home = canonical_team_name(match.get("team1"))
        away = canonical_team_name(match.get("team2"))
        if not home or not away:
            continue

        hg, ag = score
        stats[home]["matches"] += 1
        stats[home]["scored"] += hg
        stats[home]["conceded"] += ag
        stats[away]["matches"] += 1
        stats[away]["scored"] += ag
        stats[away]["conceded"] += hg
        total_goals += hg + ag
        total_appearances += 2

    if not total_appearances:
        raise ValueError(f"{league}: gecerli gecmis mac bulunamadi")

    league_average = total_goals / total_appearances
    return stats, league_average


def team_averages(name, stats, league_average):
    key = canonical_team_name(name)
    team = stats.get(key)

    if not team or not team["matches"]:
        return {
            "goals_scored_avg": league_average,
            "goals_conceded_avg": league_average,
            "history_known": False,
            "historical_matches": 0,
        }

    count = team["matches"]
    return {
        "goals_scored_avg": team["scored"] / count,
        "goals_conceded_avg": team["conceded"] / count,
        "history_known": True,
        "historical_matches": count,
    }


def predict_fixture(fixture, stats, league_average):
    home = team_averages(
        fixture["home_team"], stats, league_average
    )
    away = team_averages(
        fixture["away_team"], stats, league_average
    )

    features = {
        "home_goals_scored_avg": home["goals_scored_avg"],
        "home_goals_conceded_avg": home["goals_conceded_avg"],
        "away_goals_scored_avg": away["goals_scored_avg"],
        "away_goals_conceded_avg": away["goals_conceded_avg"],
    }
    prediction = predict_match(features)

    if home["history_known"] and away["history_known"]:
        status = "historical_team_data_available"
    elif not home["history_known"] and not away["history_known"]:
        status = "both_teams_use_league_average"
    elif not home["history_known"]:
        status = "home_team_uses_league_average"
    else:
        status = "away_team_uses_league_average"

    return {
        "league": fixture.get("league"),
        "date": fixture["date"],
        "time": fixture.get("time"),
        "home_team": fixture["home_team"],
        "away_team": fixture["away_team"],
        "history_season": "2024-25",
        "history_status": status,
        "home_historical_matches": home["historical_matches"],
        "away_historical_matches": away["historical_matches"],
        **prediction,
    }


def generate_predictions(league):
    fixture_path = (
        Path("data/fixtures") / f"{league}_{FIXTURE_SEASON}.json"
    )
    output_path = (
        Path("data/predictions")
        / f"{league}_{FIXTURE_SEASON}_predictions.json"
    )

    if output_path.exists():
        raise FileExistsError(
            f"{output_path} zaten var; uzerine yazilmadi"
        )

    fixture_data = read_json(fixture_path)
    fixtures = fixture_data.get("fixtures")
    if not isinstance(fixtures, list):
        raise ValueError(f"Gecersiz fikstur dosyasi: {fixture_path}")

    stats, league_average = load_team_stats(league)
    predictions = [
        predict_fixture(fixture, stats, league_average)
        for fixture in fixtures
    ]

    return output_path, {
        "league": league,
        "fixture_season": "2026-27",
        "history_season": "2024-25",
        "source_fixture_count": len(fixtures),
        "prediction_count": len(predictions),
        "league_average_goals_per_team": round(league_average, 4),
        "predictions": predictions,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--league", choices=LEAGUES)
    args = parser.parse_args()
    leagues = [args.league] if args.league else list(LEAGUES)

    # Once tum girdileri hesapla; mevcut ciktilarin uzerine yazma.
    results = [generate_predictions(league) for league in leagues]
    existing = [str(path) for path, _ in results if path.exists()]
    if existing:
        raise FileExistsError(
            "Mevcut ciktilar korunuyor: " + ", ".join(existing)
        )

    output_dir = Path("data/predictions")
    output_dir.mkdir(parents=True, exist_ok=True)

    for path, payload in results:
        temp_path = path.with_suffix(".json.tmp")
        temp_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temp_path.replace(path)
        print(
            f"{payload['league']}: "
            f"{payload['prediction_count']} tahmin -> {path}"
        )


if __name__ == "__main__":
    main()
