'use client';

import { useState } from 'react';
import { apiClient } from '@/lib/api';
import PredictionButton from '@/components/predictions/PredictionButton';
import ModelCard from '@/components/predictions/ModelCard';
import type { DualPredictionResponse } from '@/lib/types';

export default function PredictionsPage() {
  const [loading, setLoading] = useState(false);
  const [prediction, setPrediction] = useState<DualPredictionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handlePredict = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await apiClient.makeDualPrediction();
      setPrediction(result);
    } catch (err) {
      setError('Failed to get prediction. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Make Prediction Section */}
      <div className="bg-white rounded-lg shadow p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
          Bitcoin Sentiment Prediction
        </h2>

        <div className="mb-8">
          <PredictionButton onPredict={handlePredict} loading={loading} />
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-600 text-center">{error}</p>
          </div>
        )}

        {prediction && (
          <>
            {/* Prediction Results */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-6">
              <ModelCard
                prediction={prediction.vader}
                modelName="VADER Model"
                modelColor="cyan"
                modelType="Rule-Based"
              />
              <ModelCard
                prediction={prediction.finbert}
                modelName="FinBERT Model"
                modelColor="rose"
                modelType="Deep Learning"
              />
            </div>

            {/* Agreement Indicator */}
            <div
              className={`p-4 rounded-lg border ${
                prediction.agreement
                  ? 'bg-green-50 border-green-200'
                  : 'bg-yellow-50 border-yellow-200'
              }`}
            >
              <div className="flex items-center justify-center">
                <span
                  className={`font-semibold text-lg ${
                    prediction.agreement ? 'text-green-600' : 'text-yellow-600'
                  }`}
                >
                  {prediction.agreement ? '✓ Both models agree' : '⚠ Models disagree'}: 
                  {' '}
                  {prediction.vader.prediction.direction.toUpperCase()} prediction
                </span>
              </div>
              <p className="text-center text-sm text-gray-600 mt-2">
                Total response time: {prediction.performance.total_response_time_ms.toFixed(0)}ms
              </p>
            </div>
          </>
        )}

        {!prediction && !loading && (
          <div className="text-center py-12 text-gray-500">
            <p>Click the button above to get a Bitcoin sentiment prediction</p>
            <p className="text-sm mt-2">Both VADER and FinBERT models will analyze current sentiment</p>
          </div>
        )}
      </div>

      {/* Prediction History */}
      {prediction && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Latest Prediction Details</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">VADER</h4>
              <dl className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <dt className="text-gray-600">Prediction ID:</dt>
                  <dd className="font-mono">{prediction.vader.prediction_id || 'N/A'}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-gray-600">Timestamp:</dt>
                  <dd>{new Date(prediction.vader.timestamp).toLocaleString()}</dd>
                </div>
              </dl>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-2">FinBERT</h4>
              <dl className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <dt className="text-gray-600">Prediction ID:</dt>
                  <dd className="font-mono">{prediction.finbert.prediction_id || 'N/A'}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-gray-600">Timestamp:</dt>
                  <dd>{new Date(prediction.finbert.timestamp).toLocaleString()}</dd>
                </div>
              </dl>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}