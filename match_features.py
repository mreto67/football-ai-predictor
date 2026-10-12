"""Yalnızca geçmiş maçlardan takım performans özellikleri üretir."""

from collections import defaultdict, deque
from datetime import date


def build_match_features(matches):
    """Her maç için maç öncesi sezon ve son 5 maç istatistiklerini hesaplar."""
    ordered = []

    for match in matches:
        if not isinstance(match, dict):
            raise ValueError("Her maç kaydı bir sözlük olmalı.")

        match_date = match.get("date")
        try:
            date.fromisoformat(match_date)
        except (ValueError, TypeError):
            raise ValueError(f"Geçersiz maç tarihi: {match_date!r}") from None

        home = match.get("home_team")
        away = match.get("away_team")
        hg = match.get("home_goals")
        ag = match.get("away_goals")

        if not isinstance(home, str) or not home.strip():
            raise ValueError("Geçersiz ev sahibi takım.")
        if not isinstance(away, str) or not away.strip():
            raise ValueError("Geçersiz deplasman takımı.")
        if (
            not isinstance(hg, int) or isinstance(hg, bool) or hg < 0
            or not isinstance(ag, int) or isinstance(ag, bool) or ag < 0
        ):
            raise ValueError("Geçersiz maç skoru.")

        ordered.append((match_date, home, away, hg, ag))

    ordered.sort(key=lambda item: item[0])

    history = defaultdict(lambda: {
        "matches": 0,
        "scored": 0,
        "conceded": 0,
    })
    recent = defaultdict(lambda: deque(maxlen=5))

    features = []
    index = 0

    while index < len(ordered):
        match_date = ordered[index][0]
        end = index

        while end < len(ordered) and ordered[end][0] == match_date:
            end += 1

        # Günün bütün maçlarının özellikleri sonuçlar eklenmeden hesaplanır.
        for _, home, away, hg, ag in ordered[index:end]:
            home_stats = history[home]
            away_stats = history[away]
            home_recent = list(recent[home])
            away_recent = list(recent[away])

            features.append({
                "date": match_date,
                "home_team": home,
                "away_team": away,
                "home_matches_before": home_stats["matches"],
                "away_matches_before": away_stats["matches"],
                "home_goals_scored_avg": (
                    home_stats["scored"] / home_stats["matches"]
                    if home_stats["matches"] else 0.0
                ),
                "away_goals_scored_avg": (
                    away_stats["scored"] / away_stats["matches"]
                    if away_stats["matches"] else 0.0
                ),
                "home_goals_conceded_avg": (
                    home_stats["conceded"] / home_stats["matches"]
                    if home_stats["matches"] else 0.0
                ),
                "away_goals_conceded_avg": (
                    away_stats["conceded"] / away_stats["matches"]
                    if away_stats["matches"] else 0.0
                ),
                "home_last5_goals_scored_avg": (
                    sum(item[0] for item in home_recent) / len(home_recent)
                    if home_recent else 0.0
                ),
                "home_last5_goals_conceded_avg": (
                    sum(item[1] for item in home_recent) / len(home_recent)
                    if home_recent else 0.0
                ),
                "away_last5_goals_scored_avg": (
                    sum(item[0] for item in away_recent) / len(away_recent)
                    if away_recent else 0.0
                ),
                "away_last5_goals_conceded_avg": (
                    sum(item[1] for item in away_recent) / len(away_recent)
                    if away_recent else 0.0
                ),
                "home_goals": hg,
                "away_goals": ag,
                "outcome": "1" if hg > ag else "X" if hg == ag else "2",
            })

        # Günün tüm maçları özellikler oluşturulduktan sonra geçmişe eklenir.
        for _, home, away, hg, ag in ordered[index:end]:
            history[home]["matches"] += 1
            history[home]["scored"] += hg
            history[home]["conceded"] += ag

            history[away]["matches"] += 1
            history[away]["scored"] += ag
            history[away]["conceded"] += hg

            recent[home].append((hg, ag))
            recent[away].append((ag, hg))

        index = end

    return features
