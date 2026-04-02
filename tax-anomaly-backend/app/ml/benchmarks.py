"""Industry benchmark data for deduction ratios and IRS thresholds."""

INDUSTRY_BENCHMARKS: dict[str, dict[str, dict[str, float]]] = {
    "general": {
        "deduction_to_income_ratio": {"mean": 0.35, "std": 0.15, "max_reasonable": 0.65},
        "home_office_to_expenses": {"mean": 0.05, "std": 0.03, "max_reasonable": 0.15},
        "meal_to_expenses": {"mean": 0.08, "std": 0.05, "max_reasonable": 0.25},
        "vehicle_to_expenses": {"mean": 0.10, "std": 0.06, "max_reasonable": 0.30},
        "travel_to_expenses": {"mean": 0.06, "std": 0.04, "max_reasonable": 0.20},
    },
    "consulting": {
        "deduction_to_income_ratio": {"mean": 0.40, "std": 0.12, "max_reasonable": 0.65},
        "home_office_to_expenses": {"mean": 0.08, "std": 0.04, "max_reasonable": 0.20},
        "meal_to_expenses": {"mean": 0.10, "std": 0.05, "max_reasonable": 0.25},
        "vehicle_to_expenses": {"mean": 0.08, "std": 0.05, "max_reasonable": 0.25},
        "travel_to_expenses": {"mean": 0.12, "std": 0.06, "max_reasonable": 0.30},
    },
    "retail": {
        "deduction_to_income_ratio": {"mean": 0.55, "std": 0.15, "max_reasonable": 0.80},
        "home_office_to_expenses": {"mean": 0.03, "std": 0.02, "max_reasonable": 0.10},
        "meal_to_expenses": {"mean": 0.04, "std": 0.03, "max_reasonable": 0.15},
        "vehicle_to_expenses": {"mean": 0.12, "std": 0.06, "max_reasonable": 0.30},
        "travel_to_expenses": {"mean": 0.04, "std": 0.03, "max_reasonable": 0.15},
    },
    "construction": {
        "deduction_to_income_ratio": {"mean": 0.60, "std": 0.12, "max_reasonable": 0.80},
        "home_office_to_expenses": {"mean": 0.02, "std": 0.01, "max_reasonable": 0.08},
        "meal_to_expenses": {"mean": 0.05, "std": 0.03, "max_reasonable": 0.15},
        "vehicle_to_expenses": {"mean": 0.15, "std": 0.08, "max_reasonable": 0.35},
        "travel_to_expenses": {"mean": 0.08, "std": 0.04, "max_reasonable": 0.20},
    },
    "healthcare": {
        "deduction_to_income_ratio": {"mean": 0.45, "std": 0.12, "max_reasonable": 0.70},
        "home_office_to_expenses": {"mean": 0.04, "std": 0.03, "max_reasonable": 0.12},
        "meal_to_expenses": {"mean": 0.06, "std": 0.04, "max_reasonable": 0.20},
        "vehicle_to_expenses": {"mean": 0.10, "std": 0.05, "max_reasonable": 0.25},
        "travel_to_expenses": {"mean": 0.08, "std": 0.04, "max_reasonable": 0.20},
    },
    "technology": {
        "deduction_to_income_ratio": {"mean": 0.30, "std": 0.10, "max_reasonable": 0.55},
        "home_office_to_expenses": {"mean": 0.10, "std": 0.05, "max_reasonable": 0.25},
        "meal_to_expenses": {"mean": 0.08, "std": 0.04, "max_reasonable": 0.20},
        "vehicle_to_expenses": {"mean": 0.05, "std": 0.03, "max_reasonable": 0.15},
        "travel_to_expenses": {"mean": 0.10, "std": 0.05, "max_reasonable": 0.25},
    },
    "real_estate": {
        "deduction_to_income_ratio": {"mean": 0.50, "std": 0.15, "max_reasonable": 0.75},
        "home_office_to_expenses": {"mean": 0.06, "std": 0.03, "max_reasonable": 0.15},
        "meal_to_expenses": {"mean": 0.08, "std": 0.05, "max_reasonable": 0.25},
        "vehicle_to_expenses": {"mean": 0.15, "std": 0.07, "max_reasonable": 0.35},
        "travel_to_expenses": {"mean": 0.06, "std": 0.04, "max_reasonable": 0.20},
    },
}


IRS_SCHEDULE_C_THRESHOLDS = {
    "home_office_deduction_pct_of_expenses": 0.50,
    "meal_deduction_pct_of_expenses": 0.50,
    "vehicle_deduction_pct_of_expenses": 0.50,
    "total_deduction_pct_of_income": 0.80,
    "business_loss_threshold": -50000,
    "cash_business_extra_scrutiny_income": 100000,
}


def get_benchmarks(industry: str) -> dict[str, dict[str, float]]:
    """Get benchmarks for a given industry, falling back to general."""
    return INDUSTRY_BENCHMARKS.get(industry, INDUSTRY_BENCHMARKS["general"])
