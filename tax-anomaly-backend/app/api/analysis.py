"""Analysis endpoints for anomaly detection."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.schemas import AnalysisResult, ComparisonResult
from app.services.anomaly_detector import analyze_record
from app.services.prior_year import compare_years
from app.services.data_store import store

router = APIRouter(prefix="/api", tags=["analysis"])


class AnalyzeRequest(BaseModel):
    client_id: str
    tax_year: int


class CompareRequest(BaseModel):
    client_id: str
    current_year: int
    prior_year: int


@router.post("/analyze", response_model=AnalysisResult)
async def run_analysis(request: AnalyzeRequest) -> AnalysisResult:
    """Run anomaly detection on a client's financial data for a given tax year."""
    record = store.get_record(request.client_id, request.tax_year)
    if not record:
        raise HTTPException(
            status_code=404,
            detail=f"No record found for client {request.client_id}, year {request.tax_year}",
        )

    result = analyze_record(record)
    store.add_analysis(result)
    return result


@router.get("/analysis/{analysis_id}", response_model=AnalysisResult)
async def get_analysis(analysis_id: str) -> AnalysisResult:
    """Retrieve a previously computed analysis result."""
    result = store.get_analysis(analysis_id)
    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return result


@router.post("/compare", response_model=ComparisonResult)
async def compare_years_endpoint(request: CompareRequest) -> ComparisonResult:
    """Compare a client's financial data between two tax years."""
    current = store.get_record(request.client_id, request.current_year)
    if not current:
        raise HTTPException(
            status_code=404,
            detail=f"No record for client {request.client_id}, year {request.current_year}",
        )

    prior = store.get_record(request.client_id, request.prior_year)
    if not prior:
        raise HTTPException(
            status_code=404,
            detail=f"No record for client {request.client_id}, year {request.prior_year}",
        )

    return compare_years(current, prior)
