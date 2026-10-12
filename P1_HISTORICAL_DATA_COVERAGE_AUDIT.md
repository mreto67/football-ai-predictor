# P1 — Historical Data Coverage Audit (Preliminary)

**Date:** 2026-10-12  
**Status:** Preliminary read-only audit; no importer or application code has been written.  
**Primary candidate:** `openfootball/football.json`  
**Repository:** https://github.com/openfootball/football.json

## 1. What the source provides

The repository describes itself as a public-domain JSON dataset of football fixtures and results. The documented match shape includes:
- competition/season name (`name`)
- match list (`matches`)
- round (`round`)
- match date (`date`)
- home/team 1 and away/team 2 names (`team1`, `team2`)
- full-time score array (`score.ft`) when known

Example source file pattern: `2025-26/en.1.json`. Exact field presence must be checked for each file; this is not a guarantee that every match has a final score.

The repository README states that the latest-season datasets are automatically updated daily from upstream Football.TXT data, while the upstream source datasets themselves are not necessarily updated daily. Therefore, a daily repository update must not be interpreted as guaranteed live or current match statistics.

## 2. Observed sample inventory

The repository's visible `2025-26` directory includes the following file codes. These are **observed entries in one season directory**, not a complete count of every supported league or every historical season.

| File code | Likely competition family | Audit status |
|---|---|---|
| `at.1.json` | Austria, top division | File listed; record counts not yet measured |
| `be.1.json` | Belgium, top division | File listed; record counts not yet measured |
| `de.1.json` | Germany, top division | File listed; record counts not yet measured |
| `de.1-full.json` | Germany, extended/detail variant | File listed; schema differences need inspection |
| `de.2.json` | Germany, second division | File listed; record counts not yet measured |
| `en.1.json` | England, Premier League | File listed; record counts not yet measured |
| `en.1-full.json` | England, extended/detail variant | File listed; schema differences need inspection |
| `en.2.json` | England, Championship | File listed; record counts not yet measured |
| `en.3.json` | England, League One | File listed; record counts not yet measured |
| `en.4.json` | England, League Two | File listed; record counts not yet measured |
| `es.1.json` | Spain, top division | File listed; record counts not yet measured |
| `es.2.json` | Spain, second division | File listed; record counts not yet measured |
| `fr.1.json` | France, top division | File listed; record counts not yet measured |
| `fr.2.json` | France, second division | File listed; record counts not yet measured |
| `gr.1.json` | Greece, top division | File listed; record counts not yet measured |
| `it.1.json` | Italy, top division | File listed; record counts not yet measured |
| `it.2.json` | Italy, second division | File listed; record counts not yet measured |
| `nl.1.json` | Netherlands, top division | File listed; record counts not yet measured |
| `pt.1.json` | Portugal, top division | File listed; record counts not yet measured |
| `sco.1.json` | Scotland, top division | File listed; record counts not yet measured |
| `tr.1.json` | Türkiye, top division | File listed; record counts not yet measured |

**Important:** This list is a repository-directory observation, not yet a validated match dataset. Before production ingestion, we must fetch and parse each candidate file and confirm its actual contents.

## 3. Coverage and quality still to measure

The following have **not** been verified yet:
- total matches per competition and season;
- number of completed matches versus fixtures without scores;
- missing dates, team names, rounds and scores;
- duplicate fixtures and inconsistent team aliases;
- whether postponed/cancelled matches are represented consistently;
- the exact schema differences between standard and `-full` files;
- coverage across all year/season directories;
- whether the desired competitions have enough historical seasons for a useful model.

Do not report “all leagues supported” until this inventory has been measured.

## 4. Source license and freshness notes

The repository identifies the schema, data and scripts as public domain and exposes a CC0-1.0 license link. Re-check the license at the time data is ingested and keep the source URL and retrieval timestamp in project metadata.

The repository README says current-season datasets are automatically updated once per day from upstream Football.TXT datasets. It also warns that upstream data is not necessarily updated automatically every day. This dataset is suitable as a historical fixtures/results candidate, not a real-time live-statistics feed.

## 5. P1 implementation gate

Before writing a reusable importer, perform a small read-only sample audit:
1. Inspect at least one file from England, Spain, Germany, Italy, Türkiye and one additional league.
2. Count total matches, scored matches, and matches missing dates or scores.
3. Verify the score array structure and date parsing.
4. Compare standard and `-full` variants where both exist.
5. Save a reproducible coverage table.
6. Only then approve the importer design.

## 6. Next action

The next step is to inspect and parse representative raw JSON files and generate measured counts. Keep the audit script temporary or isolated until its output is reviewed. No Android UI, API server, database migration or ML training should begin before this data gate passes.

## Source references

- Repository: https://github.com/openfootball/football.json
- README: https://github.com/openfootball/football.json/blob/master/README.md
- Example detailed file: https://github.com/openfootball/football.json/blob/master/2025-26/en.1-full.json
- Raw JSON files can be retrieved from `https://raw.githubusercontent.com/openfootball/football.json/master/<season>/<file>.json`.
