P1 — Historical Data Audit

Date: 2026-10-12
Status: Preliminary coverage checks completed; full data validation pending.

Scope

Primary candidate: "openfootball/football.json" (https://github.com/openfootball/football.json)

England Premier League

Period: 2015–16 through 2024–25.

- Season files checked: 10
- Total records: 3,800
- Records with a valid full-time score: 3,800
- Missing scores: 0

Spain Primera División

Period: 2015–16 through 2024–25.

- Season files checked: 10
- Total records: 3,800
- Records with a valid full-time score: 3,790
- Missing scores: 10

The ten records without scores are dated 23–25 May 2025. The source contains empty score objects ("score: {}"). Their actual match outcomes have not yet been independently verified. Exclude these records from supervised training until their outcomes are confirmed.

Türkiye Süper Lig

- The "tr.1.json" file was found for 2024–25.
- That file contained 342 records, 338 with scores and 4 without scores.
- The tested paths for 2022–23 and 2023–24 returned HTTP 404. This does not prove that the data is unavailable under another filename or source.

Data integrity rules

- Never infer or fabricate missing scores.
- Preserve source URLs and ingestion timestamps.
- Validate dates, team identities, duplicates and score formats before importing.
- Use chronological train/validation/test splits.
- Keep pre-match features free of information that became available after kickoff or full-time.
- Confirm source licensing and attribution requirements before public or commercial release.

Next actions

1. Investigate alternative filenames/sources for missing Türkiye seasons.
2. Validate all missing-score records before deciding whether to exclude them permanently.
3. Extend the audit to team names, dates, duplicate matches and season coverage.
4. Approve the reusable importer only after the validation results are reviewed.

No Android UI or machine-learning model has been implemented at this stage.
