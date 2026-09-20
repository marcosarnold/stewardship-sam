"""Evidence-text formatting shared by signal detectors."""

from datetime import date


def format_amount(amount: float) -> str:
    if float(amount).is_integer():
        return f"${amount:,.0f}"
    return f"${amount:,.2f}"


def format_date(value: date) -> str:
    return f"{value:%b} {value.day}, {value:%Y}"
