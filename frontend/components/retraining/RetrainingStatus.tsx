interface RetrainingStatusProps {
    featureSet: string;
    status: {
      should_retrain: boolean;
      reasons: string[];
      data_available: number;
      data_required: number;
    };
    color: 'cyan' | 'rose';
  }
  
  export default function RetrainingStatus({ featureSet, status, color }: RetrainingStatusProps) {
    const colorClasses = {
      cyan: {
        border: 'border-cyan-500',
        progress: 'bg-cyan-600',
        text: 'text-cyan-600',
      },
      rose: {
        border: 'border-rose-500',
        progress: 'bg-rose-600',
        text: 'text-rose-600',
      },
    };
  
    const colors = colorClasses[color];
    const progressPercentage = Math.min((status.data_available / status.data_required) * 100, 100);
    const samplesNeeded = Math.max(status.data_required - status.data_available, 0);
  
    return (
      <div className={`border ${colors.border} rounded-lg p-6`}>
        <div className="flex items-center justify-between mb-4">
          <h4 className="font-semibold text-gray-900 text-lg">{featureSet} Model</h4>
          <span
            className={`px-3 py-1 text-sm font-medium rounded ${
              status.should_retrain
                ? 'bg-green-100 text-green-800'
                : 'bg-yellow-100 text-yellow-800'
            }`}
          >
            {status.should_retrain ? 'Ready to Retrain' : 'Waiting for Data'}
          </span>
        </div>
  
        <div className="space-y-4">
          {/* Data Availability Progress */}
          <div>
            <div className="flex justify-between text-sm mb-2">
              <span className="text-gray-600">Data Available</span>
              <span className="font-semibold">
                {status.data_available} / {status.data_required} samples
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className={`h-3 rounded-full transition-all ${colors.progress}`}
                style={{ width: `${progressPercentage}%` }}
              />
            </div>
            <p className="text-xs text-gray-500 mt-1">
              {samplesNeeded > 0
                ? `Need ${samplesNeeded} more samples`
                : 'Sufficient data available'}
            </p>
          </div>
  
          {/* Should Retrain Status */}
          <div className="pt-4 border-t border-gray-200">
            <p className="text-sm text-gray-600 mb-2">Should Retrain:</p>
            <p
              className={`text-lg font-semibold ${
                status.should_retrain ? 'text-green-600' : 'text-red-600'
              }`}
            >
              {status.should_retrain ? 'YES' : 'NO'}
            </p>
            {status.reasons.length > 0 ? (
              <div className="mt-2 space-y-1">
                {status.reasons.map((reason, idx) => (
                  <p key={idx} className="text-sm text-gray-600">
                    • {reason}
                  </p>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500 mt-1">
                Reason: Insufficient data (need {samplesNeeded} more samples)
              </p>
            )}
          </div>
        </div>
      </div>
    );
  }