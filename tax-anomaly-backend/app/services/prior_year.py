"""Prior-year comparison service."""

from app.models.schemas import (
    FinancialRecord,
    PriorYearComparison,
    ComparisonResult,
)

COMPARISON_FIELDS = [
    ("gross_income", "Gross Income"),
    ("total_deductions", "Total Deductions"),
    ("business_income", "Business Income"),
    ("business_expenses", "Business Expenses"),
    ("home_office_deduction", "Home Office Deduction"),
    ("vehicle_deduction", "Vehicle Deduction"),
    ("meal_deduction", "Meal Deduction"),
    ("travel_deduction", "Travel Deduction"),
    ("charitable_contributions", "Charitable Contributions"),
    ("mortgage_interest", "Mortgage Interest"),
    ("medical_expenses", "Medical Expenses"),
    ("advertising_deduction", "Advertising"),
    ("insurance_deduction", "Insurance"),
    ("supplies_deduction", "Supplies"),
    ("utilities_deduction", "Utilities"),
]

SIGNIFICANT_CHANGE_THRESHOLD = 0.25


def compare_years(
    current: FinancialRecord, prior: FinancialRecord
) -> ComparisonResult:
    """Compare two financial records from different tax years."""
    comparisons: list[PriorYearComparison] = []

    for field, label in COMPARISON_FIELDS:
        current_val = getattr(current, field, 0.0)
        prior_val = getattr(prior, field, 0.0)
        change = current_val - prior_val

        if prior_val != 0:
            pct_change = change / abs(prior_val)
        elif current_val != 0:
            pct_change = 1.0
        else:
            pct_change = 0.0

        is_significant = abs(pct_change) > SIGNIFICANT_CHANGE_THRESHOLD

        if is_significant:
            direction = "increased" if change > 0 else "decreased"
            note = (
                f"{label} {direction} by {abs(pct_change):.0%} "
                f"(${abs(change):,.2f}) year-over-year."
            )
        else:
            note = f"{label} is within normal year-over-year range."

        comparisons.append(PriorYearComparison(
            field=label,
            current_year=current_val,
            prior_year=prior_val,
            change_amount=change,
            change_percent=pct_change * 100,
            is_significant=is_significant,
            note=note,
        ))

    significant_count = sum(1 for c in comparisons if c.is_significant)

    return ComparisonResult(
        client_id=current.client_id,
        current_year=current.tax_year,
        prior_year=prior.tax_year,
        comparisons=comparisons,
        significant_changes=significant_count,
    )
