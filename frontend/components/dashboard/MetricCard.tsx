interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: {
    value: string;
    direction: 'up' | 'down';
    isGood?: boolean; // New prop to indicate if trend is positive
  };
  color?: 'cyan' | 'rose' | 'green' | 'yellow' | 'red';
}

export default function MetricCard({ title, value, subtitle, trend, color = 'cyan' }: MetricCardProps) {
  const colorClasses = {
    cyan: 'border-cyan-500',
    rose: 'border-rose-500',
    green: 'border-green-500',
    yellow: 'border-yellow-500',
    red: 'border-red-500',
  };

  // Fix issue #3: Determine trend color based on context
  const getTrendColor = () => {
    if (!trend) return '';
    
    // If isGood is explicitly set, use that
    if (trend.isGood !== undefined) {
      return trend.isGood ? 'text-green-600' : 'text-red-600';
    }
    
    // Default behavior: up is good, down is bad
    return trend.direction === 'up' ? 'text-green-600' : 'text-red-600';
  };

  return (
    <div className={`bg-white rounded-lg shadow p-6 border-l-4 ${colorClasses[color]}`}>
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-medium text-gray-600">{title}</h3>
        {trend && (
          <span className={`text-xs font-medium ${getTrendColor()}`}>
            {trend.direction === 'up' ? '↑' : '↓'} {trend.value}
          </span>
        )}
      </div>
      <p className="text-3xl font-bold text-gray-900">{value}</p>
      {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
    </div>
  );
}