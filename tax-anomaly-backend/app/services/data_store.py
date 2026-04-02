"""In-memory data store for client records and analysis results."""

from app.models.schemas import FinancialRecord, AnalysisResult, ClientSummary


class DataStore:
    """Simple in-memory store for financial records and analysis results."""

    def __init__(self) -> None:
        self._records: dict[str, dict[int, FinancialRecord]] = {}
        self._analyses: dict[str, AnalysisResult] = {}
        self._client_analyses: dict[str, list[str]] = {}

    def add_record(self, record: FinancialRecord) -> None:
        """Store a financial record, keyed by client_id and tax_year."""
        if record.client_id not in self._records:
            self._records[record.client_id] = {}
        self._records[record.client_id][record.tax_year] = record

    def get_record(self, client_id: str, tax_year: int) -> FinancialRecord | None:
        """Retrieve a specific record."""
        return self._records.get(client_id, {}).get(tax_year)

    def get_client_records(self, client_id: str) -> dict[int, FinancialRecord]:
        """Get all records for a client, keyed by tax year."""
        return self._records.get(client_id, {})

    def get_all_clients(self) -> list[ClientSummary]:
        """List all clients with summary info."""
        summaries: list[ClientSummary] = []
        for client_id, years in self._records.items():
            analysis_ids = self._client_analyses.get(client_id, [])
            latest = None
            if analysis_ids:
                latest = self._analyses.get(analysis_ids[-1])
            summaries.append(ClientSummary(
                client_id=client_id,
                tax_years=sorted(years.keys()),
                latest_analysis=latest,
            ))
        return summaries

    def add_analysis(self, analysis: AnalysisResult) -> None:
        """Store an analysis result."""
        self._analyses[analysis.analysis_id] = analysis
        if analysis.client_id not in self._client_analyses:
            self._client_analyses[analysis.client_id] = []
        self._client_analyses[analysis.client_id].append(analysis.analysis_id)

    def get_analysis(self, analysis_id: str) -> AnalysisResult | None:
        """Retrieve an analysis result by ID."""
        return self._analyses.get(analysis_id)

    def get_client_analyses(self, client_id: str) -> list[AnalysisResult]:
        """Get all analyses for a client."""
        analysis_ids = self._client_analyses.get(client_id, [])
        return [
            self._analyses[aid]
            for aid in analysis_ids
            if aid in self._analyses
        ]


store = DataStore()
