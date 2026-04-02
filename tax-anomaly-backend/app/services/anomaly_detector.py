"""Main anomaly detection orchestrator combining ML and rule-based approaches."""

import uuid
from datetime import datetime, timezone

from app.models.schemas import AnalysisResult, FinancialRecord, SeverityLevel
from app.ml.rule_engine import run_rule_engine
from app.ml.isolation_forest import detect_statistical_outliers


def analyze_record(record: FinancialRecord) -> AnalysisResult:
    """Run full anomaly detection pipeline on a financial record."""
    rule_anomalies = run_rule_engine(record)
    ml_anomalies = detect_statistical_outliers(record)

    seen_fields: set[str] = set()
    all_anomalies = []

    for anomaly in sorted(
        rule_anomalies + ml_anomalies,
        key=lambda a: a.severity_score,
        reverse=True,
    ):
        key = (anomaly.field, anomaly.anomaly_type)
        if key not in seen_fields:
            seen_fields.add(key)
            all_anomalies.append(anomaly)

    if all_anomalies:
        risk_score = min(
            100.0,
            sum(a.severity_score for a in all_anomalies) / len(all_anomalies)
            + len(all_anomalies) * 5,
        )
    else:
        risk_score = 0.0

    severity_counts = {level: 0 for level in SeverityLevel}
    for a in all_anomalies:
        severity_counts[a.severity] += 1

    summary_parts = []
    if severity_counts[SeverityLevel.CRITICAL] > 0:
        summary_parts.append(
            f"{severity_counts[SeverityLevel.CRITICAL]} critical"
        )
    if severity_counts[SeverityLevel.HIGH] > 0:
        summary_parts.append(f"{severity_counts[SeverityLevel.HIGH]} high")
    if severity_counts[SeverityLevel.MEDIUM] > 0:
        summary_parts.append(f"{severity_counts[SeverityLevel.MEDIUM]} medium")
    if severity_counts[SeverityLevel.LOW] > 0:
        summary_parts.append(f"{severity_counts[SeverityLevel.LOW]} low")

    if summary_parts:
        summary = (
            f"Found {len(all_anomalies)} anomalies "
            f"({', '.join(summary_parts)}) with overall risk score {risk_score:.0f}/100."
        )
    else:
        summary = "No anomalies detected. Tax return appears normal."

    return AnalysisResult(
        analysis_id=str(uuid.uuid4()),
        client_id=record.client_id,
        tax_year=record.tax_year,
        created_at=datetime.now(timezone.utc),
        anomalies=all_anomalies,
        total_anomalies=len(all_anomalies),
        risk_score=risk_score,
        summary=summary,
    )
