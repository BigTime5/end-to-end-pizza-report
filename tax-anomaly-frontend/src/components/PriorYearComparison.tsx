import { useState } from 'react';
import { ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { compareYears, type ComparisonResult } from '@/services/api';

interface PriorYearComparisonProps {
  clientId: string;
  taxYears: number[];
}

export function PriorYearComparison({ clientId, taxYears }: PriorYearComparisonProps) {
  const [comparison, setComparison] = useState<ComparisonResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sortedYears = [...taxYears].sort((a, b) => b - a);
  const canCompare = sortedYears.length >= 2;

  const handleCompare = async () => {
    if (!canCompare) return;
    setLoading(true);
    setError(null);
    try {
      const result = await compareYears(clientId, sortedYears[0], sortedYears[1]);
      setComparison(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Comparison failed');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (val: number) =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-lg">Prior Year Comparison</CardTitle>
        {canCompare && !comparison && (
          <Button onClick={handleCompare} disabled={loading} size="sm" variant="outline">
            {loading ? 'Comparing...' : `Compare ${sortedYears[0]} vs ${sortedYears[1]}`}
          </Button>
        )}
      </CardHeader>
      <CardContent>
        {!canCompare && (
          <p className="text-sm text-zinc-500">
            Need at least 2 tax years of data to compare. Upload data for another year.
          </p>
        )}

        {error && <p className="text-sm text-red-600">{error}</p>}

        {comparison && (
          <div className="space-y-3">
            <div className="flex items-center gap-4 text-sm text-zinc-600">
              <span>Comparing {comparison.current_year} vs {comparison.prior_year}</span>
              <span className="font-medium text-orange-600">
                {comparison.significant_changes} significant change{comparison.significant_changes !== 1 ? 's' : ''}
              </span>
            </div>
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Category</TableHead>
                    <TableHead className="text-right">{comparison.prior_year}</TableHead>
                    <TableHead className="text-right">{comparison.current_year}</TableHead>
                    <TableHead className="text-right">Change</TableHead>
                    <TableHead className="text-right">% Change</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {comparison.comparisons.map((comp) => (
                    <TableRow
                      key={comp.field}
                      className={comp.is_significant ? 'bg-red-50' : ''}
                    >
                      <TableCell className="font-medium text-sm">
                        {comp.field}
                        {comp.is_significant && (
                          <span className="ml-2 text-xs text-red-600 font-normal">
                            Significant
                          </span>
                        )}
                      </TableCell>
                      <TableCell className="text-right font-mono text-sm">
                        {formatCurrency(comp.prior_year)}
                      </TableCell>
                      <TableCell className="text-right font-mono text-sm">
                        {formatCurrency(comp.current_year)}
                      </TableCell>
                      <TableCell className="text-right font-mono text-sm">
                        <span className="inline-flex items-center gap-1">
                          {comp.change_amount > 0 ? (
                            <ArrowUpRight className="h-3 w-3 text-red-500" />
                          ) : comp.change_amount < 0 ? (
                            <ArrowDownRight className="h-3 w-3 text-green-500" />
                          ) : (
                            <Minus className="h-3 w-3 text-zinc-400" />
                          )}
                          {formatCurrency(Math.abs(comp.change_amount))}
                        </span>
                      </TableCell>
                      <TableCell className={`text-right font-mono text-sm ${
                        comp.is_significant
                          ? Math.abs(comp.change_percent) > 50
                            ? 'text-red-600 font-bold'
                            : 'text-orange-600'
                          : ''
                      }`}>
                        {comp.change_percent >= 0 ? '+' : ''}{comp.change_percent.toFixed(1)}%
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
