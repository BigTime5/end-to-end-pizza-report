"""Isolation Forest-based statistical anomaly detection for tax data."""

import numpy as np
from sklearn.ensemble import IsolationForest

from app.models.schemas import Anomaly, AnomalyType, SeverityLevel, FinancialRecord


FEATURE_LABELS = [
    ("deduction_to_income", "Total Deductions / Income ratio"),
    ("business_expense_to_income", "Business Expenses / Income ratio"),
    ("home_office_ratio", "Home Office / Business Expenses ratio"),
    ("meal_ratio", "Meal / Business Expenses ratio"),
    ("vehicle_ratio", "Vehicle / Business Expenses ratio"),
    ("travel_ratio", "Travel / Business Expenses ratio"),
    ("charitable_to_income", "Charitable Contributions / Income ratio"),
    ("mortgage_to_income", "Mortgage Interest / Income ratio"),
    ("medical_to_income", "Medical Expenses / Income ratio"),
]


def extract_features(record: FinancialRecord) -> np.ndarray:
    """Extract numerical feature vector from a financial record."""
    income = max(record.gross_income, 1.0)
    expenses = max(record.business_expenses, 1.0)

    features = [
        record.total_deductions / income,
        record.business_expenses / income,
        record.home_office_deduction / expenses,
        record.meal_deduction / expenses,
        record.vehicle_deduction / expenses,
        record.travel_deduction / expenses,
        record.charitable_contributions / income,
        record.mortgage_interest / income,
        record.medical_expenses / income,
    ]
    return np.array(features, dtype=np.float64)


def _generate_synthetic_training_data(n_samples: int = 500) -> np.ndarray:
    """Generate synthetic normal tax data for training."""
    rng = np.random.RandomState(42)
    data = np.column_stack([
        rng.beta(2, 5, n_samples) * 0.8,       # deduction_to_income
        rng.beta(2, 5, n_samples) * 0.6,       # business_expense_to_income
        rng.beta(1.5, 20, n_samples) * 0.3,    # home_office_ratio
        rng.beta(1.5, 15, n_samples) * 0.3,    # meal_ratio
        rng.beta(2, 12, n_samples) * 0.4,      # vehicle_ratio
        rng.beta(1.5, 18, n_samples) * 0.3,    # travel_ratio
        rng.beta(1, 10, n_samples) * 0.2,      # charitable_to_income
        rng.beta(2, 8, n_samples) * 0.3,       # mortgage_to_income
        rng.beta(1, 20, n_samples) * 0.15,     # medical_to_income
    ])
    return data


_model: IsolationForest | None = None
_training_data: np.ndarray | None = None


def _get_model() -> tuple[IsolationForest, np.ndarray]:
    """Get or create the Isolation Forest model (lazy init)."""
    global _model, _training_data
    if _model is None:
        _training_data = _generate_synthetic_training_data()
        _model = IsolationForest(
            n_estimators=200,
            contamination=0.05,
            random_state=42,
            max_samples="auto",
        )
        _model.fit(_training_data)
    return _model, _training_data


def detect_statistical_outliers(record: FinancialRecord) -> list[Anomaly]:
    """Use Isolation Forest to detect statistical outliers in a tax record."""
    anomalies: list[Anomaly] = []
    model, training_data = _get_model()
    features = extract_features(record)

    prediction = model.predict(features.reshape(1, -1))[0]
    anomaly_score = -model.score_samples(features.reshape(1, -1))[0]

    if prediction == -1:
        severity_score = min(100.0, anomaly_score * 100)
        if severity_score >= 75:
            severity = SeverityLevel.CRITICAL
        elif severity_score >= 50:
            severity = SeverityLevel.HIGH
        elif severity_score >= 25:
            severity = SeverityLevel.MEDIUM
        else:
            severity = SeverityLevel.LOW

        means = training_data.mean(axis=0)
        stds = training_data.std(axis=0)
        deviations = np.abs(features - means) / np.maximum(stds, 1e-8)
        top_indices = np.argsort(deviations)[-3:][::-1]

        for idx in top_indices:
            feature_name, feature_label = FEATURE_LABELS[idx]
            mean_val = means[idx]
            std_val = stds[idx]
            actual_val = features[idx]
            dev = deviations[idx]

            feature_severity_score = min(100.0, dev * 20)
            if feature_severity_score >= 75:
                feature_severity = SeverityLevel.CRITICAL
            elif feature_severity_score >= 50:
                feature_severity = SeverityLevel.HIGH
            elif feature_severity_score >= 25:
                feature_severity = SeverityLevel.MEDIUM
            else:
                feature_severity = SeverityLevel.LOW

            anomalies.append(Anomaly(
                anomaly_type=AnomalyType.STATISTICAL_OUTLIER,
                severity=feature_severity,
                severity_score=feature_severity_score,
                field=feature_name,
                description=(
                    f"{feature_label} ({actual_val:.3f}) is {dev:.1f} standard deviations "
                    f"from the population mean ({mean_val:.3f})"
                ),
                actual_value=actual_val,
                expected_range=f"{mean_val:.3f} +/- {std_val * 2:.3f}",
                recommendation=(
                    f"This metric is statistically unusual. "
                    f"Review supporting documentation for {feature_label.lower()}."
                ),
            ))

    return anomalies
