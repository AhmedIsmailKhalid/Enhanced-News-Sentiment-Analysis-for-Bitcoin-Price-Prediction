'use client';

import { useState, useEffect } from 'react';
import ModelCard from '@/components/predictions/ModelCard';
import { apiClient } from '@/lib/api';

export default function PredictionsPage() {
  const [predictions, setPredictions] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadLatestPredictions();
    
    // Auto-refresh every 30 seconds to show new predictions
    const interval = setInterval(loadLatestPredictions, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadLatestPredictions = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Get the most recent predictions for both models
      const response = await apiClient.getRecentPredictions(undefined, 2); // Get 2 most recent (1 VADER, 1 FinBERT)
      
      if (response.predictions && response.predictions.length > 0) {
        // Separate VADER and FinBERT predictions
        const vaderPred = response.predictions.find((p: any) => p.feature_set === 'vader');
        const finbertPred = response.predictions.find((p: any) => p.feature_set === 'finbert');
        
        if (vaderPred && finbertPred) {
          setPredictions({
            vader: {
              success: true,
              prediction: {
                direction: vaderPred.prediction === 1 ? 'up' : 'down',
                direction_numeric: vaderPred.prediction,
                probability: {
                  down: vaderPred.probability_down,
                  up: vaderPred.probability_up,
                },
                confidence: vaderPred.confidence,
              },
              model_info: {
                feature_set: 'vader',
                model_type: vaderPred.model_type,
                model_version: vaderPred.model_version,
              },
              timestamp: vaderPred.predicted_at,
            },
            finbert: {
              success: true,
              prediction: {
                direction: finbertPred.prediction === 1 ? 'up' : 'down',
                direction_numeric: finbertPred.prediction,
                probability: {
                  down: finbertPred.probability_down,
                  up: finbertPred.probability_up,
                },
                confidence: finbertPred.confidence,
              },
              model_info: {
                feature_set: 'finbert',
                model_type: finbertPred.model_type,
                model_version: finbertPred.model_version,
              },
              timestamp: finbertPred.predicted_at,
            },
            agreement: vaderPred.prediction === finbertPred.prediction,
          });
        }
      }
    } catch (err) {
      console.error('Failed to load predictions:', err);
      setError('Failed to load latest predictions');
    } finally {
      setLoading(false);
    }
  };

  if (loading && !predictions) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Bitcoin Sentiment Prediction</h1>
          <p className="mt-2 text-gray-600">
            Real-time predictions from VADER and FinBERT models
          </p>
        </div>
        <div className="animate-pulse space-y-4">
          <div className="h-64 bg-gray-200 rounded-lg"></div>
          <div className="h-64 bg-gray-200 rounded-lg"></div>
        </div>
      </div>
    );
  }

  if (error || !predictions) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Bitcoin Sentiment Prediction</h1>
          <p className="mt-2 text-gray-600">
            Real-time predictions from VADER and FinBERT models
          </p>
        </div>
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
          <p className="text-yellow-800">
            No predictions available yet. Predictions are generated automatically every 15 minutes.
          </p>
          <button
            onClick={loadLatestPredictions}
            className="mt-4 px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700"
          >
            Refresh
          </button>
        </div>
      </div>
    );
  }

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'just now';
    if (diffMins < 60) return `${diffMins} min ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Bitcoin Sentiment Prediction</h1>
          <p className="mt-2 text-gray-600">
            Latest predictions from VADER and FinBERT models
          </p>
          <p className="mt-1 text-sm text-gray-500">
            Last updated: {formatTimestamp(predictions.vader.timestamp)}
          </p>
        </div>
        <button
          onClick={loadLatestPredictions}
          disabled={loading}
          className="px-4 py-2 bg-cyan-600 text-white rounded-lg hover:bg-cyan-700 disabled:opacity-50"
        >
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <ModelCard
          prediction={predictions.vader}
          modelName="VADER Model"
          modelColor="cyan"
          modelType="Rule-Based"
        />
        <ModelCard
          prediction={predictions.finbert}
          modelName="FinBERT Model"
          modelColor="rose"
          modelType="Deep Learning"
        />
      </div>

      {predictions.agreement !== undefined && (
        <div className={`p-6 rounded-lg border-2 ${
          predictions.agreement 
            ? 'bg-green-50 border-green-500' 
            : 'bg-yellow-50 border-yellow-500'
        }`}>
          <div className="flex items-center justify-center">
            <span className={`text-lg font-semibold ${
              predictions.agreement ? 'text-green-800' : 'text-yellow-800'
            }`}>
              {predictions.agreement 
                ? '✓ Models Agree - Higher Confidence' 
                : '⚠ Models Disagree - Lower Confidence'}
            </span>
          </div>
        </div>
      )}

      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-sm text-blue-800">
          <strong>Note:</strong> Predictions are generated automatically every 15 minutes when new data is collected. 
          This page refreshes every 30 seconds to show the latest predictions.
        </p>
      </div>
    </div>
  );
}