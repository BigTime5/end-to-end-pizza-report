"""Rule-based anomaly detection for tax returns."""

from app.models.schemas import Anomaly, AnomalyType, SeverityLevel, FinancialRecord
from app.ml.benchmarks import get_benchmarks, IRS_SCHEDULE_C_THRESHOLDS


def _severity_from_deviation(deviation: float) -> tuple[SeverityLevel, float]:
    """Convert a deviation magnitude to severity level and score (0-100)."""
    score = min(100.0, deviation * 25)
    if score >= 75:
        return SeverityLevel.CRITICAL, score
    elif score >= 50:
        return SeverityLevel.HIGH, score
    elif score >= 25:
        return SeverityLevel.MEDIUM, score
    return SeverityLevel.LOW, score


def check_deduction_ratios(record: FinancialRecord) -> list[Anomaly]:
    """Check if deduction ratios are unusual compared to industry benchmarks."""
    anomalies: list[Anomaly] = []
    benchmarks = get_benchmarks(record.industry)

    if record.gross_income <= 0:
        return anomalies

    total_deduction_ratio = record.total_deductions / record.gross_income
    bench = benchmarks["deduction_to_income_ratio"]

    if total_deduction_ratio > bench["max_reasonable"]:
        deviation = (total_deduction_ratio - bench["mean"]) / max(bench["std"], 0.01)
        severity, score = _severity_from_deviation(abs(deviation))
        anomalies.append(Anomaly(
            anomaly_type=AnomalyType.DEDUCTION_RATIO,
            severity=severity,
            severity_score=score,
            field="total_deductions",
            description=(
                f"Total deduction ratio ({total_deduction_ratio:.1%}) exceeds "
                f"industry benchmark ({bench['mean']:.1%} +/- {bench['std']:.1%})"
            ),
            actual_value=total_deduction_ratio,
            expected_range=f"{bench['mean']:.1%} - {bench['max_reasonable']:.1%}",
            recommendation="Review all deduction categories for documentation and validity.",
        ))

    if record.business_expenses > 0:
        ratio_checks = [
            ("home_office_deduction", "home_office_to_expenses", "Home office"),
            ("meal_deduction", "meal_to_expenses", "Meal & entertainment"),
            ("vehicle_deduction", "vehicle_to_expenses", "Vehicle"),
            ("travel_deduction", "travel_to_expenses", "Travel"),
        ]
        for field, bench_key, label in ratio_checks:
            value = getattr(record, field, 0.0)
            ratio = value / record.business_expenses
            bench = benchmarks.get(bench_key)
            if bench and ratio > bench["max_reasonable"]:
                deviation = (ratio - bench["mean"]) / max(bench["std"], 0.01)
                severity, score = _severity_from_deviation(abs(deviation))
                anomalies.append(Anomaly(
                    anomaly_type=AnomalyType.DEDUCTION_RATIO,
                    severity=severity,
                    severity_score=score,
                    field=field,
                    description=(
                        f"{label} deduction ratio ({ratio:.1%}) exceeds "
                        f"industry benchmark ({bench['mean']:.1%} +/- {bench['std']:.1%})"
                    ),
                    actual_value=ratio,
                    expected_range=f"{bench['mean']:.1%} - {bench['max_reasonable']:.1%}",
                    recommendation=f"Verify {label.lower()} deduction records and receipts.",
                ))

    return anomalies


def check_income_mismatch(record: FinancialRecord) -> list[Anomaly]:
    """Check for mismatches between income sources and reported figures."""
    anomalies: list[Anomaly] = []

    if not record.income_sources:
        return anomalies

    total_from_sources = sum(s.reported_amount for s in record.income_sources)
    if record.gross_income > 0 and abs(total_from_sources - record.gross_income) > 100:
        diff = abs(total_from_sources - record.gross_income)
        pct_diff = diff / record.gross_income
        severity, score = _severity_from_deviation(pct_diff * 10)
        anomalies.append(Anomaly(
            anomaly_type=AnomalyType.INCOME_MISMATCH,
            severity=severity,
            severity_score=score,
            field="gross_income",
            description=(
                f"Total income from sources (${total_from_sources:,.2f}) doesn't match "
                f"reported gross income (${record.gross_income:,.2f}). "
                f"Difference: ${diff:,.2f}"
            ),
            actual_value=diff,
            expected_range="$0 - $100",
            recommendation="Reconcile income sources with reported gross income.",
        ))

    for source in record.income_sources:
        if source.w2_amount is not None:
            diff = abs(source.reported_amount - source.w2_amount)
            if diff > 100:
                pct_diff = diff / max(source.w2_amount, 1)
                severity, score = _severity_from_deviation(pct_diff * 10)
                anomalies.append(Anomaly(
                    anomaly_type=AnomalyType.INCOME_MISMATCH,
                    severity=severity,
                    severity_score=score,
                    field=f"income_source_{source.source}",
                    description=(
                        f"W-2 amount (${source.w2_amount:,.2f}) from {source.source} "
                        f"doesn't match reported (${source.reported_amount:,.2f})"
                    ),
                    actual_value=diff,
                    expected_range="$0 - $100",
                    recommendation=f"Verify W-2 from {source.source} matches reported income.",
                ))

        if source.ten99_amount is not None:
            diff = abs(source.reported_amount - source.ten99_amount)
            if diff > 100:
                pct_diff = diff / max(source.ten99_amount, 1)
                severity, score = _severity_from_deviation(pct_diff * 10)
                anomalies.append(Anomaly(
                    anomaly_type=AnomalyType.INCOME_MISMATCH,
                    severity=severity,
                    severity_score=score,
                    field=f"income_source_{source.source}",
                    description=(
                        f"1099 amount (${source.ten99_amount:,.2f}) from {source.source} "
                        f"doesn't match reported (${source.reported_amount:,.2f})"
                    ),
                    actual_value=diff,
                    expected_range="$0 - $100",
                    recommendation=f"Verify 1099 from {source.source} matches reported income.",
                ))

    return anomalies


def check_schedule_c_red_flags(record: FinancialRecord) -> list[Anomaly]:
    """Check IRS Schedule C red flags."""
    anomalies: list[Anomaly] = []
    thresholds = IRS_SCHEDULE_C_THRESHOLDS

    if record.business_expenses <= 0:
        return anomalies

    checks = [
        (
            record.home_office_deduction / record.business_expenses,
            thresholds["home_office_deduction_pct_of_expenses"],
            "home_office_deduction",
            "Home office deduction",
            "IRS closely scrutinizes home office deductions exceeding 50% of total expenses.",
        ),
        (
            record.meal_deduction / record.business_expenses,
            thresholds["meal_deduction_pct_of_expenses"],
            "meal_deduction",
            "Meal deduction",
            "Excessive meal deductions relative to business expenses flag IRS review.",
        ),
        (
            record.vehicle_deduction / record.business_expenses,
            thresholds["vehicle_deduction_pct_of_expenses"],
            "vehicle_deduction",
            "Vehicle deduction",
            "High vehicle deductions may require detailed mileage logs.",
        ),
    ]

    for ratio, threshold, field, label, recommendation in checks:
        if ratio > threshold:
            deviation = (ratio - threshold) / max(threshold, 0.01) * 3
            severity, score = _severity_from_deviation(deviation)
            anomalies.append(Anomaly(
                anomaly_type=AnomalyType.SCHEDULE_C_RED_FLAG,
                severity=severity,
                severity_score=score,
                field=field,
                description=(
                    f"{label} is {ratio:.1%} of total business expenses, "
                    f"exceeding IRS threshold of {threshold:.0%}"
                ),
                actual_value=ratio,
                expected_range=f"< {threshold:.0%}",
                recommendation=recommendation,
            ))

    if record.gross_income > 0:
        overall_ratio = record.total_deductions / record.gross_income
        if overall_ratio > thresholds["total_deduction_pct_of_income"]:
            deviation = (overall_ratio - thresholds["total_deduction_pct_of_income"]) * 10
            severity, score = _severity_from_deviation(deviation)
            anomalies.append(Anomaly(
                anomaly_type=AnomalyType.SCHEDULE_C_RED_FLAG,
                severity=severity,
                severity_score=score,
                field="total_deductions",
                description=(
                    f"Total deductions ({overall_ratio:.1%} of income) exceed "
                    f"IRS threshold of {thresholds['total_deduction_pct_of_income']:.0%}"
                ),
                actual_value=overall_ratio,
                expected_range=f"< {thresholds['total_deduction_pct_of_income']:.0%}",
                recommendation="Ensure all deductions have proper documentation.",
            ))

    net_income = record.business_income - record.business_expenses
    if net_income < thresholds["business_loss_threshold"]:
        severity, score = _severity_from_deviation(
            abs(net_income / thresholds["business_loss_threshold"])
        )
        anomalies.append(Anomaly(
            anomaly_type=AnomalyType.SCHEDULE_C_RED_FLAG,
            severity=severity,
            severity_score=score,
            field="business_income",
            description=(
                f"Business shows a large loss (${net_income:,.2f}). "
                f"IRS scrutinizes businesses with repeated large losses."
            ),
            actual_value=net_income,
            expected_range=f"> ${thresholds['business_loss_threshold']:,.0f}",
            recommendation="Document business intent to generate profit. "
                           "Repeated losses may trigger hobby-loss rules.",
        ))

    return anomalies


def run_rule_engine(record: FinancialRecord) -> list[Anomaly]:
    """Run all rule-based checks on a financial record."""
    anomalies: list[Anomaly] = []
    anomalies.extend(check_deduction_ratios(record))
    anomalies.extend(check_income_mismatch(record))
    anomalies.extend(check_schedule_c_red_flags(record))
    return anomalies
