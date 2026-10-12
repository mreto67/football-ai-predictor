# P1 — Historical Data Validation Results

Date: 2026-10-12
Status: Initial validation passed with known missing scores.

## Scope

Source: https://github.com/openfootball/football.json
Season: 2024-25

| League | Records | Missing dates | Missing team fields | Duplicate keys | Missing scores | Invalid scores |
|---|---:|---:|---:|---:|---:|---:|
| England Premier League | 380 | 0 | 0 | 0 | 0 | 0 |
| Spain Primera División | 380 | 0 | 0 | 0 | 10 | 0 |
| Türkiye Süper Lig | 342 | 0 | 0 | 0 | 4 | 0 |

## Historical coverage

England and Spain each have 380 records per season for the tested seasons 2015-16 through 2024-25.

- England: 3,800 records, 3,800 scored.
- Spain: 3,800 records, 3,790 scored.
- Türkiye: 2024-25 file found with 342 records, 338 scored.
- Türkiye 2022-23 and 2023-24 were not found at the tested paths (HTTP 404); other filenames/sources remain to be investigated.

## Rules

- Never fabricate missing scores.
- Exclude records with unknown outcomes from supervised training.
- Keep source identifiers and ingestion timestamps.
- Before model training, validate team aliases and chronological train/test boundaries.
- Confirm licensing and attribution requirements before public or commercial release.

## Next

Design a repeatable, non-destructive historical importer with a dry-run mode and tests. Start with England and Spain; keep Türkiye optional until coverage is resolved.
