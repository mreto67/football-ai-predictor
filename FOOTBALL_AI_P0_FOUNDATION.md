# Football AI Predictor — P0 Project Foundation

**Status:** Planning only; application code has not started.
**Date:** 2026-10-12

## 1. Product goal

Android application for football match analysis and probabilistic predictions:
- 1/X/2 match outcome probabilities
- Expected home and away goals
- Total goals and Over/Under 2.5 probability
- Team history and recent form
- Prediction history and model performance tracking
- Live match information only where a source provides sufficiently timely, permitted data

Predictions are estimates, not guarantees.

## 2. Locked decisions

- League scope: as many leagues as can be supported by verified usable data.
- Data budget: free sources first; no paid subscription without explicit approval.
- Initial prediction targets: 1/X/2, expected goals, total goals, Over/Under 2.5.
- Android: Kotlin + Jetpack Compose.
- Backend: Python + FastAPI.
- Database: PostgreSQL.
- Modeling: start with simple baselines; compare more complex models only through chronological tests.
- API secrets must never be embedded in the APK or committed to a public repository.
- Work incrementally, with a checkpoint and tests after each phase.

## 3. Candidate data-source inventory

| Source | Intended role | Important limitations | P0 decision |
|---|---|---|---|
| [openfootball/football.json](https://github.com/openfootball/football.json) | Broad historical fixtures/results | Verify each repository's license and actual league/season coverage during ingestion. Results do not imply live statistics. | First candidate for historical coverage audit |
| [StatsBomb Open Data](https://github.com/hudl/open-data) | Detailed events and lineups for selected competitions/seasons | Attribution/logo requirements apply to published/shared analysis; review commercial suitability before production use. | Optional research source, not a default production dependency |
| [football-data.org](https://www.football-data.org/) | API fixtures, results, tables and possible current data | Free-plan scope/rate limits and update delays apply; live scores may require paid access. Re-check current terms before integration. | Evaluate free plan only; do not promise real-time coverage |
| [Football-Data.co.uk](https://www.football-data.co.uk/) | Historical CSVs and potential cross-checking | Download availability alone does not prove commercial redistribution rights. Confirm license/terms first. | Do not ship its data until terms are confirmed |

**Policy:** “Free to download” does not automatically mean permission to redistribute or use commercially. Store provenance, retrieval date, license URL, attribution text and review status for each source. This is an engineering inventory, not legal advice.

## 4. Proposed architecture

1. Source ingestion jobs download data into an immutable/raw layer.
2. Validation checks schemas, dates, scores, duplicates and team identity.
3. Normalization maps records into the common database schema.
4. FastAPI serves match data, team form and predictions.
5. A separate model pipeline trains and evaluates models.
6. Android consumes the API; it does not hold provider API keys.
7. Live observations are timestamped and kept separate from pre-match features.

## 5. Initial data schema

### competitions
`id`, `source_id`, `source_competition_id`, `name`, `country`, `created_at`, `updated_at`

### seasons
`id`, `competition_id`, `source_season_id`, `name`, `start_date`, `end_date`

### teams
`id`, `canonical_name`, `country`, `created_at`, `updated_at`

### team_source_ids
`source_id`, `source_team_id`, `team_id`; unique on (`source_id`, `source_team_id`).

### matches
`id`, `source_id`, `source_match_id`, `season_id`, `kickoff_at` (timezone-aware), `home_team_id`, `away_team_id`, `status`, `home_goals`, `away_goals`, `round_name`, `last_source_update_at`, `ingested_at`; unique on (`source_id`, `source_match_id`).

### team_match_stats
`match_id`, `team_id`, `observed_at`, `source_id`, `period`, `shots`, `shots_on_target`, `possession_pct`, `corners`, `yellow_cards`, `red_cards`. Fields remain nullable if a source does not provide them.

### data_sources
`id`, `name`, `source_url`, `license_name`, `license_url`, `usage_notes`, `attribution_text`, `commercial_use_review_status`, `checked_at`.

### model_versions
`id`, `version`, `model_family`, `feature_schema_version`, `trained_at`, `training_start`, `training_end`, `code_revision`, `artifact_uri`, `metrics_json`, `promotion_status`.

### predictions
`id`, `match_id`, `model_version_id`, `prediction_type`, `made_at`, `prediction_cutoff_at`, `p_home`, `p_draw`, `p_away`, `expected_home_goals`, `expected_away_goals`, `expected_total_goals`, `p_over_2_5`, `feature_snapshot_version`, `data_freshness_at`.

### prediction_evaluations
`id`, `prediction_id`, `evaluated_at`, `actual_home_goals`, `actual_away_goals`, `actual_result`, `log_loss`, `brier_score`, `calibration_bucket`.

## 6. Data and model integrity rules

1. Preserve source identifiers and ingestion timestamps.
2. Team aliases are reviewed explicitly; similar names alone are not enough to merge teams.
3. Missing values remain null; never fabricate statistics.
4. Pre-match features may use only information available at the prediction cutoff.
5. In-play data must be timestamped and evaluated in a separate pipeline.
6. Split train/validation/test chronologically.
7. Track log loss, Brier score, calibration and accuracy; accuracy alone is insufficient.
8. Retain prior model versions and predictions for auditability.
9. Promote a model only after it passes leakage checks and improves on a future holdout.
10. Verify license and attribution before public/commercial release.

## 7. Phases and acceptance criteria

### P0 — Foundation
Document decisions, candidate sources, schema, security rules and validation plan.

### P1 — Historical ingestion
- Enumerate competitions and seasons in openfootball.
- Inspect a small sample across several leagues before bulk ingestion.
- Validate dates, scores, duplicates, team identity and missing values.
- Produce coverage report by competition and season.
- Record source URLs, retrieval time and license metadata.
- Do not build Android UI yet.

### P2 — Baseline ML
- Establish simple baselines.
- Use chronological holdout testing.
- Store predictions and evaluate log loss, Brier score, calibration and Over/Under 2.5.

### P3 — Android MVP
Competition/match list, match detail, team form, prediction probabilities, explanations and model performance.

### P4 — Live data
Measure source delay and rate limits. If no suitable free feed exists, show freshness labels and defer paid integration pending approval.

### P5 — Model improvements
Compare algorithms/features, calibrate per competition and promote only validated models.

### P6 — Release hardening
Security, attribution, error/offline states, tests and APK validation.

## 8. P1 acceptance checklist

- [ ] Reproducible competition/season inventory
- [ ] Small sample downloaded and parsed
- [ ] Malformed records fail with clear errors
- [ ] Duplicate source IDs handled deterministically
- [ ] Dates and scores validated
- [ ] Team alias conflicts reported for review
- [ ] Missingness and coverage report generated
- [ ] Source/license metadata recorded
- [ ] No paid source required for initial historical audit
- [ ] User reviews audit results before importer implementation

## 9. Immediate next action

Run a read-only coverage audit of openfootball/football.json: list available competitions/seasons, inspect representative files from several leagues, and report fields and gaps. Do not start application or model code before the audit is reviewed.
