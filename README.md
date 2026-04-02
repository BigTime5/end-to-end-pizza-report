# TaxGuard AI - Tax Anomaly Detector

AI-powered tax anomaly detection system for CPAs. Uses Isolation Forest ML and a rule engine to flag suspicious deductions, income mismatches, and IRS Schedule C red flags.

## Features

- **CSV Upload** - Import client financial data from CSV files
- **Plaid Integration** - Connect bank accounts via Plaid Link (sandbox mode)
- **ML Anomaly Detection** - Isolation Forest detects statistical outliers
- **Rule Engine** - Checks deduction ratios, income mismatches, IRS Schedule C red flags
- **Industry Benchmarks** - Compare against consulting, retail, healthcare, tech, and more
- **Dashboard** - Visual severity scores, charts, and flagged items
- **PDF Export** - Generate summary reports for client review
- **Prior Year Comparison** - Automatic year-over-year analysis

## Tech Stack

- **Backend**: Python FastAPI, scikit-learn, pandas
- **Frontend**: React + TypeScript, Vite, Tailwind CSS, shadcn/ui, Recharts
- **ML**: Isolation Forest (scikit-learn), custom rule engine
- **PDF**: fpdf2

## Quick Start

### Backend

```bash
cd tax-anomaly-backend
poetry install
poetry run fastapi dev app/main.py --port 8000
```

### Frontend

```bash
cd tax-anomaly-frontend
npm install
npm run dev
```

Then open http://localhost:5173 and upload the included `sample_data.csv`.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload` | Upload CSV financial data |
| POST | `/api/analyze` | Run anomaly detection |
| GET | `/api/analysis/{id}` | Get analysis results |
| GET | `/api/clients` | List all clients |
| POST | `/api/compare` | Compare two tax years |
| GET | `/api/report/{id}/pdf` | Export PDF report |
| POST | `/api/plaid/create-link-token` | Create Plaid link token |
| POST | `/api/plaid/exchange-token` | Exchange Plaid token |
| GET | `/api/plaid/transactions/{id}` | Get transactions |
