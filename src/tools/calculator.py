from __future__ import annotations


def total_with_contingency(amount: float, contingency_percent: float) -> float:
    """
    Calculate total spend with contingency.

    Example:
        amount=12000, contingency_percent=10 -> 13200.00
    """
    if amount < 0:
        raise ValueError("amount must be >= 0")
    if contingency_percent < 0:
        raise ValueError("contingency_percent must be >= 0")

    total = amount * (1 + contingency_percent / 100)
    return round(total, 2)
