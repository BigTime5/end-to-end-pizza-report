import { useState, useEffect } from 'react';
import { BarChart3, Download, Play, AlertTriangle, Shield, TrendingUp } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts';
import { AnomalyTable } from './AnomalyTable';
import { RiskGauge } from './RiskGauge';
import { PriorYearComparison } from './PriorYearComparison';
import { SeverityBadge } from './SeverityBadge';
import {
  runAnalysis,
  getReportPdfUrl,
  type AnalysisResult,
  type ClientSummary,
} from '@/services/api';

interface AnalysisDashboardProps {
  client: ClientSummary;
}

const SEVERITY_COLORS = {
  low: '#16a34a',
  medium: '#ca8a04',
  high: '#ea580c',
  critical: '#dc2626',
};

export function AnalysisDashboard({ client }: AnalysisDashboardProps) {
  const [analyses, setAnalyses] = useState<Record<number, AnalysisResult>>({});
  const [activeYear, setActiveYear] = useState<number>(
    Math.max(...client.tax_years)
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setAnalyses({});
    setActiveYear(Math.max(...client.tax_years));
    setError(null);
  }, [client.client_id, client.tax_years]);

  const currentAnalysis = analyses[activeYear];

  const handleAnalyze = async (year: number) => {
    setLoading(true);
    setError(null);
    try {
      const result = await runAnalysis(client.client_id, year);
      setAnalyses((prev) => ({ ...prev, [year]: result }));
      setActiveYear(year);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPdf = () => {
    if (!currentAnalysis) return;
    window.open(getReportPdfUrl(currentAnalysis.analysis_id), '_blank');
  };

  const severityData = currentAnalysis
    ? Object.entries(
        currentAnalysis.anomalies.reduce(
          (acc, a) => {
            acc[a.severity] = (acc[a.severity] || 0) + 1;
            return acc;
          },
          {} as Record<string, number>
        )
      ).map(([name, value]) => ({ name: name.charAt(0).toUpperCase() + name.slice(1), value }))
    : [];

  const typeData = currentAnalysis
    ? Object.entries(
        currentAnalysis.anomalies.reduce(
          (acc, a) => {
            const label =
              a.anomaly_type === 'deduction_ratio'
                ? 'Deduction Ratio'
                : a.anomaly_type === 'income_mismatch'
                ? 'Income Mismatch'
                : a.anomaly_type === 'schedule_c_red_flag'
                ? 'Schedule C'
                : 'Statistical';
            acc[label] = (acc[label] || 0) + 1;
            return acc;
          },
          {} as Record<string, number>
        )
      ).map(([name, count]) => ({ name, count }))
    : [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold flex items-center gap-2">
          <BarChart3 className="h-5 w-5" />
          {client.client_id} Analysis
        </h2>
        <div className="flex gap-2">
          {client.tax_years.sort((a, b) => b - a).map((year) => (
            <Button
              key={year}
              size="sm"
              variant={activeYear === year ? 'default' : 'outline'}
              onClick={() => {
                setActiveYear(year);
                if (!analyses[year]) handleAnalyze(year);
              }}
              disabled={loading}
            >
              {year}
            </Button>
          ))}
        </div>
      </div>

      {!currentAnalysis && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Play className="h-12 w-12 text-zinc-300 mb-4" />
            <p className="text-zinc-500 mb-4">
              Run anomaly detection for {client.client_id} ({activeYear})
            </p>
            <Button onClick={() => handleAnalyze(activeYear)} disabled={loading}>
              {loading ? 'Analyzing...' : 'Run Analysis'}
            </Button>
            {error && <p className="text-sm text-red-600 mt-3">{error}</p>}
          </CardContent>
        </Card>
      )}

      {currentAnalysis && (
        <>
          {/* Summary cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="pt-6 flex flex-col items-center">
                <RiskGauge score={currentAnalysis.risk_score} />
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center gap-2 mb-2">
                  <AlertTriangle className="h-4 w-4 text-orange-500" />
                  <span className="text-sm font-medium text-zinc-600">Total Anomalies</span>
                </div>
                <p className="text-3xl font-bold">{currentAnalysis.total_anomalies}</p>
                <div className="flex gap-1 mt-2 flex-wrap">
                  {currentAnalysis.anomalies
                    .reduce(
                      (acc, a) => {
                        if (!acc.find((x) => x === a.severity)) acc.push(a.severity);
                        return acc;
                      },
                      [] as string[]
                    )
                    .map((s) => (
                      <SeverityBadge key={s} severity={s as 'low' | 'medium' | 'high' | 'critical'} />
                    ))}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center gap-2 mb-2">
                  <Shield className="h-4 w-4 text-blue-500" />
                  <span className="text-sm font-medium text-zinc-600">Tax Year</span>
                </div>
                <p className="text-3xl font-bold">{currentAnalysis.tax_year}</p>
                <p className="text-xs text-zinc-400 mt-2">
                  Analyzed {new Date(currentAnalysis.created_at).toLocaleDateString()}
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingUp className="h-4 w-4 text-green-500" />
                  <span className="text-sm font-medium text-zinc-600">Actions</span>
                </div>
                <Button
                  onClick={handleDownloadPdf}
                  size="sm"
                  className="w-full mt-2"
                  variant="outline"
                >
                  <Download className="h-4 w-4 mr-2" />
                  Export PDF Report
                </Button>
                <Button
                  onClick={() => handleAnalyze(activeYear)}
                  size="sm"
                  className="w-full mt-2"
                  variant="outline"
                  disabled={loading}
                >
                  Re-run Analysis
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Summary text */}
          <Card>
            <CardContent className="pt-6">
              <p className="text-sm text-zinc-700">{currentAnalysis.summary}</p>
            </CardContent>
          </Card>

          {/* Detailed tabs */}
          <Tabs defaultValue="anomalies">
            <TabsList>
              <TabsTrigger value="anomalies">
                Flagged Items ({currentAnalysis.total_anomalies})
              </TabsTrigger>
              <TabsTrigger value="charts">Charts</TabsTrigger>
              <TabsTrigger value="comparison">Prior Year</TabsTrigger>
            </TabsList>

            <TabsContent value="anomalies" className="mt-4">
              <AnomalyTable anomalies={currentAnalysis.anomalies} />
            </TabsContent>

            <TabsContent value="charts" className="mt-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Anomalies by Type</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={250}>
                      <BarChart data={typeData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                        <YAxis allowDecimals={false} />
                        <Tooltip />
                        <Bar dataKey="count" fill="#6366f1" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Severity Distribution</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={250}>
                      <PieChart>
                        <Pie
                          data={severityData}
                          dataKey="value"
                          nameKey="name"
                          cx="50%"
                          cy="50%"
                          outerRadius={80}
                          label={({ name, value }) => `${name}: ${value}`}
                        >
                          {severityData.map((entry) => (
                            <Cell
                              key={entry.name}
                              fill={
                                SEVERITY_COLORS[
                                  entry.name.toLowerCase() as keyof typeof SEVERITY_COLORS
                                ] || '#6366f1'
                              }
                            />
                          ))}
                        </Pie>
                        <Tooltip />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="comparison" className="mt-4">
              <PriorYearComparison
                clientId={client.client_id}
                taxYears={client.tax_years}
              />
            </TabsContent>
          </Tabs>
        </>
      )}
    </div>
  );
}
