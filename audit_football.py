import json
import urllib.request

BASE = "https://raw.githubusercontent.com/openfootball/football.json/master/2025-26/"
LEAGUES = {
    "İngiltere": "en.1.json",
    "Türkiye": "tr.1.json",
    "İspanya": "es.1.json",
    "Almanya": "de.1.json",
    "İtalya": "it.1.json",
    "Fransa": "fr.1.json",
}

def has_final_score(match):
    score = match.get("score")
    if isinstance(score, dict):
        score = score.get("ft")
    elif isinstance(score, list):
        pass
    else:
        return False

    return (
        isinstance(score, list)
        and len(score) == 2
        and all(isinstance(x, (int, float)) for x in score)
    )

for league, filename in LEAGUES.items():
    url = BASE + filename
    print(f"\n--- {league} ({filename}) ---")

    try:
        request = urllib.request.Request(
            url, headers={"User-Agent": "FootballAI-DataAudit/1.0"}
        )
        with urllib.request.urlopen(request, timeout=25) as response:
            data = json.load(response)

        matches = data.get("matches", [])
        valid = [
            m for m in matches
            if m.get("date") and m.get("team1") and m.get("team2")
        ]
        scored = sum(has_final_score(m) for m in matches)

        keys = set()
        duplicates = 0
        for m in matches:
            key = (
                m.get("date"),
                m.get("team1"),
                m.get("team2"),
            )
            if key in keys:
                duplicates += 1
            keys.add(key)

        print("Kaynak adı:", data.get("name", "bilinmiyor"))
        print("Toplam maç kaydı:", len(matches))
        print("Tarih ve takım adları mevcut:", len(valid))
        print("Skor alanı bulunan:", scored)
        print("Skoru eksik:", len(matches) - scored)
        print("Tekrarlanan tarih/ev/deplasman:", duplicates)

    except Exception as exc:
        print("HATA:", type(exc).__name__, str(exc))
