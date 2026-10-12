"""OpenFootball kaynağından gelecek fikstürleri güvenli şekilde içe aktarır."""

import json
import urllib.request
from datetime import date
from pathlib import Path

BASE_URL = (
    "https://raw.githubusercontent.com/openfootball/"
    "football.json/master/2026-27/"
)

LEAGUES = {
    "england": "en.1.json",
    "spain": "es.1.json",
    "italy": "it.1.json",
    "germany": "de.1.json",
    "france": "fr.1.json",
}

OUTPUT_DIR = Path("data/fixtures")


def fetch_league_fixtures(league, today=None):
    """Bir ligden tarihi bugünden sonraki, skoru olmayan maçları alır."""
    if league not in LEAGUES:
        raise ValueError(f"Desteklenmeyen lig: {league}")

    today = today or date.today()
    url = BASE_URL + LEAGUES[league]
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "FootballAI-FixtureImporter/1.0"},
    )

    with urllib.request.urlopen(request, timeout=25) as response:
        data = json.load(response)

    matches = data.get("matches")
    if not isinstance(matches, list):
        raise ValueError(f"{league}: Kaynakta maç listesi bulunamadı")

    fixtures = []
    seen = set()

    for match in matches:
        if not isinstance(match, dict):
            continue

        match_date = match.get("date")
        home = match.get("team1")
        away = match.get("team2")
        score = match.get("score")

        try:
            parsed_date = date.fromisoformat(match_date)
        except (ValueError, TypeError):
            continue

        if parsed_date <= today:
            continue

        if not isinstance(home, str) or not home.strip():
            continue
        if not isinstance(away, str) or not away.strip():
            continue
        if home.strip().casefold() == away.strip().casefold():
            continue

        if score is not None:
            if not isinstance(score, dict) or score.get("ft") is not None:
                continue

        key = (match_date, home.strip().casefold(), away.strip().casefold())
        if key in seen:
            continue
        seen.add(key)

        fixtures.append({
            "league": league,
            "date": match_date,
            "time": match.get("time"),
            "home_team": home.strip(),
            "away_team": away.strip(),
            "source": "openfootball",
        })

    fixtures.sort(key=lambda row: (
        row["date"], row["time"] or "", row["home_team"], row["away_team"]
    ))
    return fixtures


def import_fixtures(today=None):
    """Beş ligin fikstürlerini ayrı JSON dosyalarına kaydeder."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    summary = {}

    for league in LEAGUES:
        fixtures = fetch_league_fixtures(league, today=today)
        output_path = OUTPUT_DIR / f"{league}_2026_27.json"
        temporary_path = output_path.with_suffix(".json.tmp")

        payload = {
            "league": league,
            "season": "2026-27",
            "retrieved_on": (today or date.today()).isoformat(),
            "source": "openfootball",
            "count": len(fixtures),
            "fixtures": fixtures,
        }

        temporary_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temporary_path.replace(output_path)
        summary[league] = len(fixtures)

    return summary


if __name__ == "__main__":
    try:
        results = import_fixtures()
        print("Gelecek fikstürleri başarıyla kaydedildi:")
        for league, count in results.items():
            print(f"  {league}: {count} maç")
        print(f"Klasör: {OUTPUT_DIR}")
    except Exception as exc:
        raise SystemExit(f"Fikstür içe aktarma başarısız: {exc}")
