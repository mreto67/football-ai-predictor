import json
from pathlib import Path

leagues = {
    "england": 320,
    "spain": 301,
    "italy": 320,
    "germany": 261,
    "france": 252,
}

output = Path("data/predictions/all_leagues_2026_27_predictions.json")

if output.exists():
    raise SystemExit(
        f"Mevcut dosya korunuyor, üzerine yazılmadı: {output}"
    )

combined = []
counts = {}

for league, expected in leagues.items():
    path = Path("data/predictions") / (
        f"{league}_2026_27_predictions.json"
    )
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("predictions")

    if not isinstance(rows, list) or len(rows) != expected:
        raise SystemExit(f"Doğrulama başarısız: {path}")

    if any(row.get("league") != league for row in rows):
        raise SystemExit(f"Lig bilgisi tutarsız: {path}")

    counts[league] = len(rows)
    combined.extend(rows)

payload = {
    "schema_version": 1,
    "fixture_season": "2026-27",
    "history_season": "2024-25",
    "league_counts": counts,
    "total_predictions": len(combined),
    "predictions": combined,
}

output.parent.mkdir(parents=True, exist_ok=True)
temp = output.with_suffix(".json.tmp")

try:
    temp.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    temp.replace(output)
except Exception:
    temp.unlink(missing_ok=True)
    raise

print("Ortak katalog oluşturuldu:", output)
print("Toplam tahmin:", len(combined))
for league, count in counts.items():
    print(f"{league}: {count}")
