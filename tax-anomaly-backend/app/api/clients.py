"""Client management endpoints."""

from fastapi import APIRouter, HTTPException

from app.models.schemas import ClientSummary, FinancialRecord
from app.services.data_store import store

router = APIRouter(prefix="/api", tags=["clients"])


@router.get("/clients", response_model=list[ClientSummary])
async def list_clients() -> list[ClientSummary]:
    """List all clients with their available tax years."""
    return store.get_all_clients()


@router.get("/clients/{client_id}", response_model=ClientSummary)
async def get_client(client_id: str) -> ClientSummary:
    """Get details for a specific client."""
    records = store.get_client_records(client_id)
    if not records:
        raise HTTPException(status_code=404, detail=f"Client {client_id} not found")

    analyses = store.get_client_analyses(client_id)
    latest = analyses[-1] if analyses else None

    return ClientSummary(
        client_id=client_id,
        tax_years=sorted(records.keys()),
        latest_analysis=latest,
    )


@router.get("/clients/{client_id}/records/{tax_year}", response_model=FinancialRecord)
async def get_client_record(client_id: str, tax_year: int) -> FinancialRecord:
    """Get a specific financial record for a client and tax year."""
    record = store.get_record(client_id, tax_year)
    if not record:
        raise HTTPException(
            status_code=404,
            detail=f"No record found for client {client_id}, year {tax_year}",
        )
    return record
