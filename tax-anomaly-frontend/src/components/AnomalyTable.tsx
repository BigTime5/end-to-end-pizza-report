import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { SeverityBadge } from './SeverityBadge';
import type { Anomaly } from '@/services/api';

interface AnomalyTableProps {
  anomalies: Anomaly[];
}

const typeLabels: Record<string, string> = {
  deduction_ratio: 'Deduction Ratio',
  income_mismatch: 'Income Mismatch',
  schedule_c_red_flag: 'Schedule C Red Flag',
  statistical_outlier: 'Statistical Outlier',
};

export function AnomalyTable({ anomalies }: AnomalyTableProps) {
  if (anomalies.length === 0) {
    return (
      <div className="text-center py-8 text-zinc-500">
        No anomalies detected. Tax return appears normal.
      </div>
    );
  }

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-12">#</TableHead>
            <TableHead>Type</TableHead>
            <TableHead>Severity</TableHead>
            <TableHead>Score</TableHead>
            <TableHead className="min-w-64">Description</TableHead>
            <TableHead>Expected</TableHead>
            <TableHead className="min-w-48">Recommendation</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {anomalies.map((anomaly, index) => (
            <TableRow key={`${anomaly.field}-${anomaly.anomaly_type}-${index}`}>
              <TableCell className="font-medium">{index + 1}</TableCell>
              <TableCell>
                <span className="text-xs font-medium px-2 py-1 rounded bg-zinc-100">
                  {typeLabels[anomaly.anomaly_type] || anomaly.anomaly_type}
                </span>
              </TableCell>
              <TableCell>
                <SeverityBadge severity={anomaly.severity} />
              </TableCell>
              <TableCell className="font-mono text-sm">
                {anomaly.severity_score.toFixed(0)}
              </TableCell>
              <TableCell className="text-sm">{anomaly.description}</TableCell>
              <TableCell className="text-sm font-mono">
                {anomaly.expected_range}
              </TableCell>
              <TableCell className="text-sm text-zinc-600">
                {anomaly.recommendation}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
