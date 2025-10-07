interface SystemStatusCardProps {
    title: string;
    status: 'healthy' | 'degraded' | 'down' | 'unknown';
    value?: string | number;
    subtitle?: string;
  }
  
  export default function SystemStatusCard({ title, status, value, subtitle }: SystemStatusCardProps) {
    const statusConfig = {
      healthy: {
        bg: 'bg-green-50',
        border: 'border-green-500',
        text: 'text-green-600',
        dot: 'bg-green-500',
        label: 'Healthy',
      },
      degraded: {
        bg: 'bg-yellow-50',
        border: 'border-yellow-500',
        text: 'text-yellow-600',
        dot: 'bg-yellow-500',
        label: 'Degraded',
      },
      down: {
        bg: 'bg-red-50',
        border: 'border-red-500',
        text: 'text-red-600',
        dot: 'bg-red-500',
        label: 'Down',
      },
      unknown: {
        bg: 'bg-gray-50',
        border: 'border-gray-400',
        text: 'text-gray-600',
        dot: 'bg-gray-400',
        label: 'Unknown',
      },
    };
  
    const config = statusConfig[status];
  
    return (
      <div className={`${config.bg} rounded-lg border-l-4 ${config.border} p-6`}>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-medium text-gray-600">{title}</h3>
          <div className="flex items-center space-x-2">
            <div className={`h-2 w-2 rounded-full ${config.dot} animate-pulse`}></div>
            <span className={`text-xs font-semibold ${config.text} uppercase`}>
              {config.label}
            </span>
          </div>
        </div>
        {value !== undefined && (
          <p className="text-2xl font-bold text-gray-900">{value}</p>
        )}
        {subtitle && (
          <p className="text-xs text-gray-500 mt-1">{subtitle}</p>
        )}
      </div>
    );
  }