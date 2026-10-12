import math

FEATURES = (
    "home_goals_scored_avg",
    "away_goals_scored_avg",
    "home_goals_conceded_avg",
    "away_goals_conceded_avg",
)
OUTCOMES = ("1", "X", "2")
VARIANCE_FLOOR = 0.05


def _validate_row(row):
    if not isinstance(row, dict):
        raise ValueError("Each row must be a dictionary")

    values = []
    for feature in FEATURES:
        value = row.get(feature)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"Invalid numeric feature: {feature}")
        value = float(value)
        if not math.isfinite(value) or value < 0:
            raise ValueError(f"Invalid feature value: {feature}")
        values.append(value)

    outcome = row.get("outcome")
    if outcome not in OUTCOMES:
        raise ValueError("Outcome must be 1, X, or 2")

    return values, outcome


def train_form_model(rows):
    if not isinstance(rows, (list, tuple)) or not rows:
        raise ValueError("Training rows must be a non-empty list")

    grouped = {outcome: [] for outcome in OUTCOMES}

    for row in rows:
        values, outcome = _validate_row(row)
        grouped[outcome].append(values)

    if any(not grouped[outcome] for outcome in OUTCOMES):
        raise ValueError("Training data must contain outcomes 1, X, and 2")

    total = len(rows)
    model = {"classes": {}}

    for outcome in OUTCOMES:
        samples = grouped[outcome]
        count = len(samples)
        means = [
            sum(sample[i] for sample in samples) / count
            for i in range(len(FEATURES))
        ]

        variances = []
        for i, mean in enumerate(means):
            variance = sum(
                (sample[i] - mean) ** 2 for sample in samples
            ) / count
            variances.append(max(variance, VARIANCE_FLOOR))

        model["classes"][outcome] = {
            "prior": (count + 1) / (total + len(OUTCOMES)),
            "means": means,
            "variances": variances,
        }

    return model


def predict_form_probabilities(model, row):
    values, _ = _validate_row(row)
    log_scores = {}

    for outcome in OUTCOMES:
        stats = model["classes"][outcome]
        score = math.log(stats["prior"])

        for value, mean, variance in zip(
            values, stats["means"], stats["variances"]
        ):
            score -= 0.5 * (
                math.log(2 * math.pi * variance)
                + ((value - mean) ** 2) / variance
            )

        log_scores[outcome] = score

    maximum = max(log_scores.values())
    weights = {
        outcome: math.exp(score - maximum)
        for outcome, score in log_scores.items()
    }
    total = sum(weights.values())

    return {
        outcome: weights[outcome] / total
        for outcome in OUTCOMES
    }


def evaluate_form_predictions(model, rows):
    if not rows:
        raise ValueError("Evaluation rows must be non-empty")

    correct = 0
    log_loss = 0.0
    brier_sum = 0.0

    for row in rows:
        _, actual = _validate_row(row)
        probabilities = predict_form_probabilities(model, row)
        predicted = max(OUTCOMES, key=lambda outcome: probabilities[outcome])

        if predicted == actual:
            correct += 1

        log_loss -= math.log(max(probabilities[actual], 1e-15))
        brier_sum += sum(
            (probabilities[outcome] - (1.0 if outcome == actual else 0.0)) ** 2
            for outcome in OUTCOMES
        )

    count = len(rows)
    return {
        "accuracy": correct / count,
        "log_loss": log_loss / count,
        "brier_score": brier_sum / count,
        "samples": count,
    }
