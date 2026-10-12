"""Maçları tarih sırasını koruyarak eğitim ve test kümelerine ayırır."""

from datetime import date
from math import ceil


def chronological_split(rows, test_ratio=0.2):
    """Satırları tarihe göre sıralar; aynı tarihin maçlarını birlikte tutar."""
    if not isinstance(test_ratio, (int, float)) or isinstance(test_ratio, bool):
        raise ValueError("test_ratio 0 ile 1 arasında bir sayı olmalı.")
    if not 0 < test_ratio < 1:
        raise ValueError("test_ratio 0 ile 1 arasında olmalı.")

    if not isinstance(rows, (list, tuple)) or len(rows) < 2:
        raise ValueError("En az iki maç kaydı gerekli.")

    ordered = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Her maç kaydı bir sözlük olmalı.")

        match_date = row.get("date")
        try:
            date.fromisoformat(match_date)
        except (ValueError, TypeError):
            raise ValueError(f"Geçersiz maç tarihi: {match_date!r}") from None

        ordered.append(row)

    ordered.sort(key=lambda row: row["date"])

    # Test kümesi en yeni tarihlerden başlar; aynı gün bölünmez.
    target_test_rows = max(1, ceil(len(ordered) * test_ratio))
    split_index = len(ordered) - target_test_rows

    while (
        split_index > 0
        and ordered[split_index - 1]["date"] == ordered[split_index]["date"]
    ):
        split_index -= 1

    if split_index == 0:
        raise ValueError(
            "Aynı tarihleri bölmeden eğitim ve test kümeleri oluşturulamıyor."
        )

    train = ordered[:split_index]
    test = ordered[split_index:]

    if train[-1]["date"] >= test[0]["date"]:
        raise ValueError("Eğitim ve test tarihleri çakışıyor.")

    return train, test
