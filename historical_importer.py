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


def main():
    import argparse
    import json
    import urllib.request

    parser = argparse.ArgumentParser(
        description="Güvenli tarihsel futbol verisi denetimi (yalnızca dry-run)."
    )
    parser.add_argument(
        "--season",
        default="2024-25",
        help="Sezon klasörü; varsayılan: 2024-25",
    )
    parser.add_argument(
        "--league",
        choices=["england", "spain", "both"],
        default="both",
        help="Denetlenecek lig",
    )
    args = parser.parse_args()

    base = (
        "https://raw.githubusercontent.com/openfootball/"
        f"football.json/master/{args.season}/"
    )
    leagues = {
        "england": ("İngiltere", "en.1.json"),
        "spain": ("İspanya", "es.1.json"),
    }
    selected = (
        leagues.items()
        if args.league == "both"
        else [(args.league, leagues[args.league])]
    )

    for _, (name, filename) in selected:
        url = base + filename
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "FootballAI-DataAudit/1.0"},
        )
        print(f"\n--- {name} / {args.season} ---")
        try:
            with urllib.request.urlopen(request, timeout=25) as response:
                data = json.load(response)

            result = dry_run(data.get("matches", []))
            report = result["report"]

            print("Toplam maç:", report["total"])
            print("Skorlu maç:", report["scored"])
            print("Eksik skor:", report["missing_scores"])
            print("Geçersiz skor:", report["invalid_scores"])
            print("Geçersiz tarih:", report["invalid_dates"])
            print("Tekrar:", report["duplicates"])
            print("İşlenmeye uygun:", result["would_process"])
            print("Veri yazıldı mı?:", result["written"])
        except Exception as exc:
            print("HATA:", type(exc).__name__, str(exc))


if __name__ == "__main__":
    main()
