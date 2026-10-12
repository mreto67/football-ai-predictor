"""Poisson-based football match goal and outcome predictions."""

import math


_REQUIRED_FIELDS = (
    "home_goals_scored_avg",
    "home_goals_conceded_avg",
    "away_goals_scored_avg",
    "away_goals_conceded_avg",
)


def _validate_input(features):
    if not isinstance(features, dict):
        raise ValueError("features bir sozluk olmali")

    for field in _REQUIRED_FIELDS:
        value = features.get(field)

        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"Gecersiz veya eksik alan: {field}")

        if not math.isfinite(value) or value < 0:
            raise ValueError(f"Negatif veya gecersiz deger: {field}")


def _poisson_distribution(lam, max_goals=12):
    probabilities = [
        math.exp(-lam) * (lam ** goals) / math.factorial(goals)
        for goals in range(max_goals + 1)
    ]

    total = sum(probabilities)
    return [p / total for p in probabilities]


def predict_match(features):
    """Predict expected goals, score, 1X2 and over/under 2.5."""

    _validate_input(features)

    # Simple baseline: attack average blended with opponent concession average.
    expected_home = (
        features["home_goals_scored_avg"]
        + features["away_goals_conceded_avg"]
    ) / 2

    expected_away = (
        features["away_goals_scored_avg"]
        + features["home_goals_conceded_avg"]
    ) / 2

    # Avoid unrealistic values and numerical overflow.
    expected_home = min(6.0, max(0.1, expected_home))
    expected_away = min(6.0, max(0.1, expected_away))

    home_dist = _poisson_distribution(expected_home)
    away_dist = _poisson_distribution(expected_away)

    outcomes = {"1": 0.0, "X": 0.0, "2": 0.0}
    over_2_5 = 0.0
    best_score = (0, 0)
    best_probability = -1.0

    for home_goals, p_home in enumerate(home_dist):
        for away_goals, p_away in enumerate(away_dist):
            probability = p_home * p_away

            if home_goals > away_goals:
                outcomes["1"] += probability
            elif home_goals == away_goals:
                outcomes["X"] += probability
            else:
                outcomes["2"] += probability

            if home_goals + away_goals >= 3:
                over_2_5 += probability

            if probability > best_probability:
                best_probability = probability
                best_score = (home_goals, away_goals)

    total_outcomes = sum(outcomes.values())
    outcomes = {
        key: value / total_outcomes
        for key, value in outcomes.items()
    }

    over_2_5 = min(1.0, max(0.0, over_2_5))
    under_2_5 = 1.0 - over_2_5

    return {
        "expected_home_goals": round(expected_home, 2),
        "expected_away_goals": round(expected_away, 2),
        "predicted_score": f"{best_score[0]}-{best_score[1]}",
        "outcome_probabilities": outcomes,
        "over_2_5_probability": over_2_5,
        "under_2_5_probability": under_2_5,
    }
