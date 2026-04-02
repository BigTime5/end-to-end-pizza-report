import { Badge } from '@/components/ui/badge';

interface SeverityBadgeProps {
  severity: 'low' | 'medium' | 'high' | 'critical';
  score?: number;
}

const severityConfig = {
  low: { label: 'Low', className: 'bg-green-100 text-green-800 hover:bg-green-100' },
  medium: { label: 'Medium', className: 'bg-yellow-100 text-yellow-800 hover:bg-yellow-100' },
  high: { label: 'High', className: 'bg-orange-100 text-orange-800 hover:bg-orange-100' },
  critical: { label: 'Critical', className: 'bg-red-100 text-red-800 hover:bg-red-100' },
};

export function SeverityBadge({ severity, score }: SeverityBadgeProps) {
  const config = severityConfig[severity];
  return (
    <Badge className={config.className}>
      {config.label}
      {score !== undefined && ` (${score.toFixed(0)})`}
    </Badge>
  );
}
