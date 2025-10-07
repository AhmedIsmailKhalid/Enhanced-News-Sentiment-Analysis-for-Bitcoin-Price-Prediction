import type { PredictionResponse } from '@/lib/types';

interface ModelCardProps {
  prediction: PredictionResponse;
  modelName: string;
  modelColor: 'cyan' | 'rose';
  modelType: string;
}

export default function ModelCard({ prediction, modelName, modelColor, modelType }: ModelCardProps) {
  const colorClasses = {
    cyan: {
      border: 'border-cyan-500',
      badge: 'bg-cyan-100 text-cyan-800',
      progress: 'bg-cyan-600',
    },
    rose: {
      border: 'border-rose-500',
      badge: 'bg-rose-100 text-rose-800',
      progress: 'bg-rose-600',
    },
  };
  

  const colors = colorClasses[modelColor];
  const isUp = prediction.prediction.direction === 'up';

  return (
    <div className={`border-2 ${colors.border} rounded-lg p-6`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">{modelName}</h3>
        <span className={`px-3 py-1 text-sm font-medium rounded ${colors.badge}`}>
          {modelType}
        </span>
      </div>

      <div className="text-center mb-6">
        <div className={`text-5xl font-bold mb-2 ${isUp ? 'text-green-600' : 'text-red-600'}`}>
          {isUp ? '↑ UP' : '↓ DOWN'}
        </div>
        <p className="text-gray-600">
          Bitcoin sentiment is {isUp ? 'positive' : 'negative'}
        </p>
      </div>

      <div className="space-y-3">
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-600">Confidence</span>
            <span className="font-semibold">{(prediction.prediction.confidence * 100).toFixed(1)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full ${isUp ? 'bg-green-600' : 'bg-red-600'}`}
              style={{ width: `${prediction.prediction.confidence * 100}%` }}
            />
          </div>
        </div>

        <div className="pt-3 border-t border-gray-200">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">UP Probability</span>
            <span className="font-semibold text-green-600">
              {(prediction.prediction.probability.up * 100).toFixed(1)}%
            </span>
          </div>
          <div className="flex justify-between text-sm mt-1">
            <span className="text-gray-600">DOWN Probability</span>
            <span className="font-semibold text-red-600">
              {(prediction.prediction.probability.down * 100).toFixed(1)}%
            </span>
          </div>
        </div>

        {prediction.model_info && (
          <div className="pt-3 border-t border-gray-200 text-xs text-gray-500 space-y-1">
            <div className="flex justify-between">
              <span>Model Version</span>
              <span className="font-mono">{prediction.model_info.model_version}</span>
            </div>
            <div className="flex justify-between">
              <span>Features Used</span>
              <span>{prediction.model_info.features_used}</span>
            </div>
            {prediction.performance && (
              <>
                <div className="flex justify-between">
                  <span>Response Time</span>
                  <span>{prediction.performance.response_time_ms.toFixed(0)}ms</span>
                </div>
                <div className="flex justify-between">
                  <span>Cached Features</span>
                  <span>{prediction.performance.cached_features ? 'Yes' : 'No'}</span>
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}