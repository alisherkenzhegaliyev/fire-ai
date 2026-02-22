from __future__ import annotations

from typing import Dict


# Base score calibrated so that sentiment + segment adjustments
# keep each type within its intended range without any squashing.
BASE_SCORE: Dict[str, int] = {
    "Мошеннические действия":        9,  # → [9, 10] after clamp + hard floor
    "Неработоспособность приложения": 7,  # → [7, 10]
    "Жалоба":                         6,  # → [5, 8]
    "Претензия":                      4,  # → [3, 6]
    "Смена данных":                   5,  # → [2, 5]
    "Консультация":                   4,  # → [1, 4]
    "Спам":                           1,  # hard override below
}

# Sentiment shifts: ±1, neutral is baseline 0
SENTIMENT_ADJ: Dict[str, int] = {
    "Негативная":    2,
    "Нейтральная":   0,
    "Положительная": -1,
}

# Segment bonus: VIP clients always get +1 urgency
SEGMENT_BONUS: Dict[str, int] = {
    "VIP":      2,
    "Priority": 1,
    "Mass":     0,
}


def score_priority(request_type: str, sentiment: str, segment: str) -> int:
    """
    Return integer priority in [1, 10].

    Formula: BASE_SCORE[request_type] + SENTIMENT_ADJ[sentiment] + SEGMENT_BONUS[segment]
    Result is clamped to [1, 10].

    Hard rules applied after clamping:
    - Spam  → always 1
    - Fraud → minimum 9
    """
    if request_type == "Спам":
        return 1

    raw = (
        BASE_SCORE.get(request_type, 4)
        + SENTIMENT_ADJ.get(sentiment, 0)
        + SEGMENT_BONUS.get(segment, 0)
    )

    priority = max(1, min(10, raw))

    if request_type == "Мошеннические действия":
        priority = max(priority, 9)

    return priority
