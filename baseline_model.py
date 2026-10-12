"""Basit, tekrarlanabilir 1/X/2 başlangıç modeli ve değerlendirme metrikleri."""

import math
from collections import Counter

OUTCOMES = ("1", "X", "2")
FEATURES = (
    "home_goals_scored_avg",
    "away_goals_scored_avg",
    "home_goals_conceded_avg",
    "away_goals_conceded_avg",
)


def _validate_row(row, require_outcome=True):
    if not isinstance(row, dict):
        raise ValueError("Her kayıt bir sözlük olmalı.")

    if require_outcome and row.get("outcome") not in OUTCOMES:
        raise ValueError("Maç sonucu 1, X veya 2 olmalı.")

    for name in FEATURES:
        value = row.get(name)
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(value)
            or value < 0
        ):
            raise ValueError(f"Geçersiz özellik: {name}")


def train_baseline(rows):
    """Eğitim kümesindeki sonuç sıklıklarından yumuşatılmış olasılıklar öğrenir."""
    if not isinstance(rows, (list, tuple)) or not rows:
        raise ValueError("Eğitim kümesi boş olamaz.")

    counts = Counter()
    for row in rows:
        _validate_row(row)
        counts[row["outcome"]] += 1

    if any(counts[outcome] == 0 for outcome in OUTCOMES):
        raise ValueError("Eğitim verisinde 1, X ve 2 sonuçlarının tümü bulunmalı.")

    total = len(rows)
    # Laplace düzeltmesi, sıfır olasılığı önler.
    probabilities = {
        outcome: (counts[outcome] + 1) / (total + len(OUTCOMES))
        for outcome in OUTCOMES
    }
    return {"probabilities": probabilities, "training_rows": total}


def predict_probabilities(model, row):
    """Başlangıç modeli, eğitim kümesindeki temel sonuç oranlarını döndürür."""
    _validate_row(row, require_outcome=False)

    probabilities = model.get("probabilities")
    if not isinstance(probabilities, dict) or set(probabilities) != set(OUTCOMES):
        raise ValueError("Geçersiz model.")

    return {outcome: probabilities[outcome] for outcome in OUTCOMES}


def evaluate_predictions(model, rows):
    """Verilen kayıtlar üzerinde Accuracy, Log Loss ve çok sınıflı Brier skoru."""
    if not isinstance(rows, (list, tuple)) or not rows:
        raise ValueError("Değerlendirme kümesi boş olamaz.")

    correct = 0
    total_log_loss = 0.0
    total_brier = 0.0

    for row in rows:
        _validate_row(row)
        probabilities = predict_probabilities(model, row)
        actual = row["outcome"]
        predicted = max(OUTCOMES, key=lambda outcome: probabilities[outcome])

        if predicted == actual:
            correct += 1

        total_log_loss -= math.log(max(probabilities[actual], 1e-15))

        total_brier += sum(
            (probabilities[outcome] - (1.0 if outcome == actual else 0.0)) ** 2
            for outcome in OUTCOMES
        )

    count = len(rows)
    return {
        "accuracy": correct / count,
        "log_loss": total_log_loss / count,
        "brier_score": total_brier / count,
        "samples": count,
    }
