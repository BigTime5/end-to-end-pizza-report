interface RiskGaugeProps {
  score: number;
}

export function RiskGauge({ score }: RiskGaugeProps) {
  const getColor = () => {
    if (score >= 75) return 'text-red-600';
    if (score >= 50) return 'text-orange-500';
    if (score >= 25) return 'text-yellow-500';
    return 'text-green-600';
  };

  const getBgColor = () => {
    if (score >= 75) return 'bg-red-500';
    if (score >= 50) return 'bg-orange-500';
    if (score >= 25) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const getLabel = () => {
    if (score >= 75) return 'Critical Risk';
    if (score >= 50) return 'High Risk';
    if (score >= 25) return 'Medium Risk';
    return 'Low Risk';
  };

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative w-32 h-32">
        <svg className="w-32 h-32 -rotate-90" viewBox="0 0 120 120">
          <circle cx="60" cy="60" r="50" fill="none" stroke="#e5e7eb" strokeWidth="10" />
          <circle
            cx="60"
            cy="60"
            r="50"
            fill="none"
            stroke="currentColor"
            strokeWidth="10"
            strokeDasharray={`${(score / 100) * 314} 314`}
            strokeLinecap="round"
            className={getColor()}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`text-2xl font-bold ${getColor()}`}>{score.toFixed(0)}</span>
          <span className="text-xs text-zinc-500">/ 100</span>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <div className={`w-2 h-2 rounded-full ${getBgColor()}`} />
        <span className={`text-sm font-medium ${getColor()}`}>{getLabel()}</span>
      </div>
    </div>
  );
}
