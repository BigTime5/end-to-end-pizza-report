from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AnomalyType(str, Enum):
    DEDUCTION_RATIO = "deduction_ratio"
    INCOME_MISMATCH = "income_mismatch"
    SCHEDULE_C_RED_FLAG = "schedule_c_red_flag"
    STATISTICAL_OUTLIER = "statistical_outlier"


class IncomeSource(BaseModel):
    source: str
    reported_amount: float
    w2_amount: float | None = None
    ten99_amount: float | None = None


class FinancialRecord(BaseModel):
    client_id: str
    tax_year: int
    gross_income: float = 0.0
    total_deductions: float = 0.0
    business_income: float = 0.0
    business_expenses: float = 0.0
    home_office_deduction: float = 0.0
    vehicle_deduction: float = 0.0
    meal_deduction: float = 0.0
    travel_deduction: float = 0.0
    advertising_deduction: float = 0.0
    insurance_deduction: float = 0.0
    legal_deduction: float = 0.0
    office_expense_deduction: float = 0.0
    supplies_deduction: float = 0.0
    utilities_deduction: float = 0.0
    other_deductions: float = 0.0
    charitable_contributions: float = 0.0
    mortgage_interest: float = 0.0
    state_local_taxes: float = 0.0
    medical_expenses: float = 0.0
    income_sources: list[IncomeSource] = Field(default_factory=list)
    industry: str = "general"


class Anomaly(BaseModel):
    anomaly_type: AnomalyType
    severity: SeverityLevel
    severity_score: float = Field(ge=0, le=100)
    field: str
    description: str
    actual_value: float
    expected_range: str
    recommendation: str


class AnalysisResult(BaseModel):
    analysis_id: str
    client_id: str
    tax_year: int
    created_at: datetime
    anomalies: list[Anomaly]
    total_anomalies: int
    risk_score: float = Field(ge=0, le=100)
    summary: str


class PriorYearComparison(BaseModel):
    field: str
    current_year: float
    prior_year: float
    change_amount: float
    change_percent: float
    is_significant: bool
    note: str


class ComparisonResult(BaseModel):
    client_id: str
    current_year: int
    prior_year: int
    comparisons: list[PriorYearComparison]
    significant_changes: int


class UploadResponse(BaseModel):
    client_id: str
    records_count: int
    tax_years: list[int]
    message: str


class ClientSummary(BaseModel):
    client_id: str
    tax_years: list[int]
    latest_analysis: AnalysisResult | None = None
