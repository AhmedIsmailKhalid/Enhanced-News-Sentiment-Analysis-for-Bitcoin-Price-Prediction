interface DriftStatusCardProps {
    title: string;
    severity: string;
    message?: string;
    color?: 'green' | 'yellow' | 'orange' | 'red' | 'gray';
  }
  
  export default function DriftStatusCard({ title, severity, message, color = 'gray' }: DriftStatusCardProps) {
    const colorClasses = {
      green: {
        border: 'border-green-500',
        bg: 'bg-green-50',
        text: 'text-green-600',
      },
      yellow: {
        border: 'border-yellow-500',
        bg: 'bg-yellow-50',
        text: 'text-yellow-600',
      },
      orange: {
        border: 'border-orange-500',
        bg: 'bg-orange-50',
        text: 'text-orange-600',
      },
      red: {
        border: 'border-red-500',
        bg: 'bg-red-50',
        text: 'text-red-600',
      },
      gray: {
        border: 'border-gray-400',
        bg: 'bg-gray-50',
        text: 'text-gray-600',
      },
    };
  
    const colors = colorClasses[color];
  
    const getSeverityColor = (sev: string): typeof color => {
      const normalized = sev.toLowerCase();
      if (normalized === 'none' || normalized === 'stable') return 'green';
      if (normalized === 'low') return 'yellow';
      if (normalized === 'medium') return 'orange';
      if (normalized === 'high') return 'red';
      return 'gray';
    };
  
    const displayColor = color === 'gray' ? getSeverityColor(severity) : color;
    const displayColors = colorClasses[displayColor];
  
    return (
      <div className={`bg-white rounded-lg shadow p-6 border-l-4 ${displayColors.border}`}>
        <h3 className="text-sm font-medium text-gray-600 mb-2">{title}</h3>
        <p className={`text-3xl font-bold ${displayColors.text} uppercase`}>
          {severity}
        </p>
        {message && <p className="text-sm text-gray-500 mt-2">{message}</p>}
      </div>
    );
  }