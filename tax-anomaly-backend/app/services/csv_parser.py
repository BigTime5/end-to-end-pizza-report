"""CSV parsing service for uploading financial data."""

import csv
import io
from typing import Any

from app.models.schemas import FinancialRecord, IncomeSource


FIELD_MAPPING: dict[str, str] = {
    "client_id": "client_id",
    "client": "client_id",
    "tax_year": "tax_year",
    "year": "tax_year",
    "gross_income": "gross_income",
    "income": "gross_income",
    "total_income": "gross_income",
    "total_deductions": "total_deductions",
    "deductions": "total_deductions",
    "business_income": "business_income",
    "business_expenses": "business_expenses",
    "biz_expenses": "business_expenses",
    "home_office_deduction": "home_office_deduction",
    "home_office": "home_office_deduction",
    "vehicle_deduction": "vehicle_deduction",
    "vehicle": "vehicle_deduction",
    "car_deduction": "vehicle_deduction",
    "meal_deduction": "meal_deduction",
    "meals": "meal_deduction",
    "meal_entertainment": "meal_deduction",
    "travel_deduction": "travel_deduction",
    "travel": "travel_deduction",
    "advertising_deduction": "advertising_deduction",
    "advertising": "advertising_deduction",
    "insurance_deduction": "insurance_deduction",
    "insurance": "insurance_deduction",
    "legal_deduction": "legal_deduction",
    "legal": "legal_deduction",
    "office_expense_deduction": "office_expense_deduction",
    "office_expenses": "office_expense_deduction",
    "supplies_deduction": "supplies_deduction",
    "supplies": "supplies_deduction",
    "utilities_deduction": "utilities_deduction",
    "utilities": "utilities_deduction",
    "other_deductions": "other_deductions",
    "other": "other_deductions",
    "charitable_contributions": "charitable_contributions",
    "charitable": "charitable_contributions",
    "donations": "charitable_contributions",
    "mortgage_interest": "mortgage_interest",
    "mortgage": "mortgage_interest",
    "state_local_taxes": "state_local_taxes",
    "salt": "state_local_taxes",
    "medical_expenses": "medical_expenses",
    "medical": "medical_expenses",
    "industry": "industry",
}


def _normalize_header(header: str) -> str:
    """Normalize a CSV header to match known field names."""
    normalized = header.strip().lower().replace(" ", "_").replace("-", "_")
    return FIELD_MAPPING.get(normalized, normalized)


def _safe_float(value: str) -> float:
    """Parse a string to float, handling currency symbols and commas."""
    if not value or not value.strip():
        return 0.0
    cleaned = value.strip().replace("$", "").replace(",", "").replace("(", "-").replace(")", "")
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def _safe_int(value: str) -> int:
    """Parse a string to int."""
    try:
        return int(value.strip())
    except (ValueError, AttributeError):
        return 0


def parse_csv(content: str) -> list[FinancialRecord]:
    """Parse CSV content into financial records."""
    reader = csv.DictReader(io.StringIO(content))

    if reader.fieldnames is None:
        raise ValueError("CSV file has no headers")

    header_map: dict[str, str] = {}
    for header in reader.fieldnames:
        normalized = _normalize_header(header)
        header_map[header] = normalized

    records: list[FinancialRecord] = []
    for row_num, row in enumerate(reader, start=2):
        mapped: dict[str, Any] = {}
        for original_header, value in row.items():
            field_name = header_map.get(original_header, original_header)
            mapped[field_name] = value

        client_id = mapped.get("client_id", f"client_{row_num}")
        if isinstance(client_id, str):
            client_id = client_id.strip()
        if not client_id:
            client_id = f"client_{row_num}"

        tax_year = _safe_int(str(mapped.get("tax_year", "2024")))
        if tax_year < 1900 or tax_year > 2100:
            tax_year = 2024

        record = FinancialRecord(
            client_id=str(client_id),
            tax_year=tax_year,
            gross_income=_safe_float(str(mapped.get("gross_income", "0"))),
            total_deductions=_safe_float(str(mapped.get("total_deductions", "0"))),
            business_income=_safe_float(str(mapped.get("business_income", "0"))),
            business_expenses=_safe_float(str(mapped.get("business_expenses", "0"))),
            home_office_deduction=_safe_float(str(mapped.get("home_office_deduction", "0"))),
            vehicle_deduction=_safe_float(str(mapped.get("vehicle_deduction", "0"))),
            meal_deduction=_safe_float(str(mapped.get("meal_deduction", "0"))),
            travel_deduction=_safe_float(str(mapped.get("travel_deduction", "0"))),
            advertising_deduction=_safe_float(str(mapped.get("advertising_deduction", "0"))),
            insurance_deduction=_safe_float(str(mapped.get("insurance_deduction", "0"))),
            legal_deduction=_safe_float(str(mapped.get("legal_deduction", "0"))),
            office_expense_deduction=_safe_float(str(mapped.get("office_expense_deduction", "0"))),
            supplies_deduction=_safe_float(str(mapped.get("supplies_deduction", "0"))),
            utilities_deduction=_safe_float(str(mapped.get("utilities_deduction", "0"))),
            other_deductions=_safe_float(str(mapped.get("other_deductions", "0"))),
            charitable_contributions=_safe_float(str(mapped.get("charitable_contributions", "0"))),
            mortgage_interest=_safe_float(str(mapped.get("mortgage_interest", "0"))),
            state_local_taxes=_safe_float(str(mapped.get("state_local_taxes", "0"))),
            medical_expenses=_safe_float(str(mapped.get("medical_expenses", "0"))),
            industry=str(mapped.get("industry", "general")).strip() or "general",
        )
        records.append(record)

    return records
