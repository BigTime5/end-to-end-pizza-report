const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface IncomeSource {
  source: string;
  reported_amount: number;
  w2_amount: number | null;
  ten99_amount: number | null;
}

export interface FinancialRecord {
  client_id: string;
  tax_year: number;
  gross_income: number;
  total_deductions: number;
  business_income: number;
  business_expenses: number;
  home_office_deduction: number;
  vehicle_deduction: number;
  meal_deduction: number;
  travel_deduction: number;
  advertising_deduction: number;
  insurance_deduction: number;
  legal_deduction: number;
  office_expense_deduction: number;
  supplies_deduction: number;
  utilities_deduction: number;
  other_deductions: number;
  charitable_contributions: number;
  mortgage_interest: number;
  state_local_taxes: number;
  medical_expenses: number;
  industry: string;
  income_sources: IncomeSource[];
}

export interface Anomaly {
  anomaly_type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  severity_score: number;
  field: string;
  description: string;
  actual_value: number;
  expected_range: string;
  recommendation: string;
}

export interface AnalysisResult {
  analysis_id: string;
  client_id: string;
  tax_year: number;
  created_at: string;
  anomalies: Anomaly[];
  total_anomalies: number;
  risk_score: number;
  summary: string;
}

export interface UploadResponse {
  client_id: string;
  records_count: number;
  tax_years: number[];
  message: string;
}

export interface ClientSummary {
  client_id: string;
  tax_years: number[];
  latest_analysis: AnalysisResult | null;
}

export interface PriorYearComparison {
  field: string;
  current_year: number;
  prior_year: number;
  change_amount: number;
  change_percent: number;
  is_significant: boolean;
  note: string;
}

export interface ComparisonResult {
  client_id: string;
  current_year: number;
  prior_year: number;
  comparisons: PriorYearComparison[];
  significant_changes: number;
}

export interface PlaidLinkToken {
  link_token: string;
  expiration: string;
}

export interface PlaidTransaction {
  transaction_id: string;
  date: string;
  amount: number;
  category: string;
  name: string;
  merchant_name: string | null;
}

export interface TransactionsResponse {
  client_id: string;
  transactions: PlaidTransaction[];
  total_count: number;
}

export async function uploadCSV(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_URL}/api/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Upload failed');
  }
  return res.json();
}

export async function runAnalysis(clientId: string, taxYear: number): Promise<AnalysisResult> {
  const res = await fetch(`${API_URL}/api/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ client_id: clientId, tax_year: taxYear }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Analysis failed');
  }
  return res.json();
}

export async function getAnalysis(analysisId: string): Promise<AnalysisResult> {
  const res = await fetch(`${API_URL}/api/analysis/${analysisId}`);
  if (!res.ok) throw new Error('Analysis not found');
  return res.json();
}

export async function getClients(): Promise<ClientSummary[]> {
  const res = await fetch(`${API_URL}/api/clients`);
  if (!res.ok) throw new Error('Failed to fetch clients');
  return res.json();
}

export async function getClient(clientId: string): Promise<ClientSummary> {
  const res = await fetch(`${API_URL}/api/clients/${clientId}`);
  if (!res.ok) throw new Error('Client not found');
  return res.json();
}

export async function compareYears(
  clientId: string,
  currentYear: number,
  priorYear: number
): Promise<ComparisonResult> {
  const res = await fetch(`${API_URL}/api/compare`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ client_id: clientId, current_year: currentYear, prior_year: priorYear }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Comparison failed');
  }
  return res.json();
}

export function getReportPdfUrl(analysisId: string): string {
  return `${API_URL}/api/report/${analysisId}/pdf`;
}

export async function createPlaidLinkToken(): Promise<PlaidLinkToken> {
  const res = await fetch(`${API_URL}/api/plaid/create-link-token`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to create link token');
  return res.json();
}

export async function exchangePlaidToken(publicToken: string, clientId: string) {
  const res = await fetch(`${API_URL}/api/plaid/exchange-token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ public_token: publicToken, client_id: clientId }),
  });
  if (!res.ok) throw new Error('Token exchange failed');
  return res.json();
}

export async function getPlaidTransactions(clientId: string): Promise<TransactionsResponse> {
  const res = await fetch(`${API_URL}/api/plaid/transactions/${clientId}`);
  if (!res.ok) throw new Error('Failed to fetch transactions');
  return res.json();
}
