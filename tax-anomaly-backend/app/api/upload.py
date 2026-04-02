"""CSV upload endpoint."""

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.models.schemas import UploadResponse
from app.services.csv_parser import parse_csv
from app.services.data_store import store

router = APIRouter(prefix="/api", tags=["upload"])


@router.post("/upload", response_model=UploadResponse)
async def upload_csv(file: UploadFile = File(...)) -> UploadResponse:
    """Upload a CSV file with client financial data."""
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")

    content = await file.read()
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        try:
            text = content.decode("latin-1")
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="Unable to decode file")

    try:
        records = parse_csv(text)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not records:
        raise HTTPException(status_code=400, detail="No valid records found in CSV")

    client_years: dict[str, set[int]] = {}
    for record in records:
        store.add_record(record)
        client_years.setdefault(record.client_id, set()).add(record.tax_year)

    client_ids = list(client_years.keys())
    return UploadResponse(
        client_id=client_ids[0],
        records_count=len(records),
        tax_years=sorted(client_years[client_ids[0]]),
        message=f"Successfully uploaded {len(records)} records for {len(client_ids)} client(s)",
    )
