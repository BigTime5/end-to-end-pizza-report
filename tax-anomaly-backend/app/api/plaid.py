"""Plaid integration endpoints (mock for local dev)."""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/plaid", tags=["plaid"])


class LinkTokenResponse(BaseModel):
    link_token: str
    expiration: str


class ExchangeTokenRequest(BaseModel):
    public_token: str
    client_id: str


class ExchangeTokenResponse(BaseModel):
    access_token: str
    item_id: str
    message: str


class PlaidTransaction(BaseModel):
    transaction_id: str
    date: str
    amount: float
    category: str
    name: str
    merchant_name: str | None = None


class TransactionsResponse(BaseModel):
    client_id: str
    transactions: list[PlaidTransaction]
    total_count: int


_mock_tokens: dict[str, str] = {}


@router.post("/create-link-token", response_model=LinkTokenResponse)
async def create_link_token() -> LinkTokenResponse:
    """Create a Plaid Link token for client-side initialization.

    In production, this would call plaid.LinkToken.create().
    For local dev, returns a mock token.
    """
    token = f"link-sandbox-{uuid.uuid4().hex[:16]}"
    return LinkTokenResponse(
        link_token=token,
        expiration=datetime(2099, 12, 31, tzinfo=timezone.utc).isoformat(),
    )


@router.post("/exchange-token", response_model=ExchangeTokenResponse)
async def exchange_token(request: ExchangeTokenRequest) -> ExchangeTokenResponse:
    """Exchange a Plaid public token for an access token.

    In production, this would call plaid.Item.public_token.exchange().
    For local dev, returns a mock access token.
    """
    if not request.public_token:
        raise HTTPException(status_code=400, detail="public_token is required")

    access_token = f"access-sandbox-{uuid.uuid4().hex[:16]}"
    item_id = f"item-{uuid.uuid4().hex[:8]}"
    _mock_tokens[request.client_id] = access_token

    return ExchangeTokenResponse(
        access_token=access_token,
        item_id=item_id,
        message="Token exchanged successfully (sandbox mode)",
    )


@router.get("/transactions/{client_id}", response_model=TransactionsResponse)
async def get_transactions(client_id: str) -> TransactionsResponse:
    """Fetch transactions for a client from Plaid.

    In production, this would call plaid.Transactions.get().
    For local dev, returns mock transaction data.
    """
    mock_transactions = [
        PlaidTransaction(
            transaction_id=f"txn-{i}",
            date=f"2024-{(i % 12) + 1:02d}-15",
            amount=amount,
            category=category,
            name=name,
            merchant_name=merchant,
        )
        for i, (amount, category, name, merchant) in enumerate([
            (5200.00, "Income", "Monthly Salary", "ACME Corp"),
            (1200.00, "Rent", "Monthly Rent", "Property Mgmt LLC"),
            (450.00, "Office Supplies", "Office Depot Purchase", "Office Depot"),
            (85.50, "Meals", "Client Lunch Meeting", "Restaurant"),
            (1500.00, "Consulting Income", "Consulting Fee", "Client ABC"),
            (200.00, "Software", "Adobe Subscription", "Adobe"),
            (350.00, "Travel", "Business Flight", "United Airlines"),
            (125.00, "Insurance", "Business Insurance", "State Farm"),
            (75.00, "Utilities", "Internet Service", "Comcast"),
            (2500.00, "Income", "Freelance Project", None),
        ])
    ]

    return TransactionsResponse(
        client_id=client_id,
        transactions=mock_transactions,
        total_count=len(mock_transactions),
    )
