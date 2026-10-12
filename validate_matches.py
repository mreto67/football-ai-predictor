import json
import urllib.request
from collections import Counter
from datetime import date

URL = (
    "https://raw.githubusercontent.com/openfootball/"
    "football.json/master/2024-25/en.1.json"
)

req = urllib.request.Request(
    URL, headers={"User-Agent": "FootballAI-DataAudit/1.0"}
)

with urllib.request.urlopen(req, timeout=25) as response:
    data = json.load(response)

matches = data.get("matches", [])
issues = Counter()
seen = set()
duplicates = []
bad_dates = []
bad_teams = []
bad_scores = []

for m in matches:
    match_date = m.get("date")
    home = m.get("team1")
    away = m.get("team2")

    if not match_date:
        issues["missing_date"] += 1
    else:
        try:
            date.fromisoformat(match_date)
        except (ValueError, TypeError):
            issues["invalid_date"] += 1
            bad_dates.append(match_date)

    if not isinstance(home, str) or not home.strip():
        issues["missing_home_team"] += 1
    if not isinstance(away, str) or not away.strip():
        issues["missing_away_team"] += 1

    if isinstance(home, str) and isinstance(away, str):
        if home.strip().casefold() == away.strip().casefold():
            issues["same_home_away_name"] += 1
            bad_teams.append((match_date, home, away))

    key = (
        match_date,
        str(home).strip().casefold(),
        str(away).strip().casefold(),
    )
    if key in seen:
        issues["duplicate_match_key"] += 1
        duplicates.append(key)
    seen.add(key)

    score = m.get("score")
    if isinstance(score, dict):
        score = score.get("ft")

    if score is not None and score != {}:
        valid = (
            isinstance(score, list)
            and len(score) == 2
            and all(
                isinstance(x, int) and not isinstance(x, bool) and x >= 0
                for x in score
            )
        )
        if not valid:
            issues["invalid_score_format"] += 1
            bad_scores.append((match_date, home, away, score))

print("Kaynak:", data.get("name"))
print("Toplam maç:", len(matches))
print("\nSorun sayıları:")
for name in [
    "missing_date", "invalid_date",
    "missing_home_team", "missing_away_team",
    "same_home_away_name", "duplicate_match_key",
    "invalid_score_format",
]:
    print(f"{name}: {issues[name]}")

print("\nÖrnek sorunlar (varsa):")
print("Geçersiz tarihler:", bad_dates[:5])
print("Takım sorunları:", bad_teams[:5])
print("Tekrarlanan maçlar:", duplicates[:5])
print("Hatalı skor biçimleri:", bad_scores[:5])
