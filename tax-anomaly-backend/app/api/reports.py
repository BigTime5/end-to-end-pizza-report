"""PDF report generation endpoint."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from app.services.data_store import store
from app.services.pdf_generator import generate_analysis_pdf
from app.services.prior_year import compare_years

router = APIRouter(prefix="/api", tags=["reports"])


@router.get("/report/{analysis_id}/pdf")
async def export_pdf(analysis_id: str) -> Response:
    """Generate and download a PDF report for an analysis."""
    analysis = store.get_analysis(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    comparison = None
    records = store.get_client_records(analysis.client_id)
    years = sorted(records.keys())
    current_idx = years.index(analysis.tax_year) if analysis.tax_year in years else -1
    if current_idx > 0:
        prior_year = years[current_idx - 1]
        current_record = records[analysis.tax_year]
        prior_record = records[prior_year]
        comparison = compare_years(current_record, prior_record)

    pdf_bytes = generate_analysis_pdf(analysis, comparison)

    filename = f"tax_anomaly_report_{analysis.client_id}_{analysis.tax_year}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
