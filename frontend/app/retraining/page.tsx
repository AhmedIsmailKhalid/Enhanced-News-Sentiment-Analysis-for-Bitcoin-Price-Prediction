'use client';

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api';
import RetrainingStatus from '@/components/retraining/RetrainingStatus';

interface RetrainingStatusData {
  vader: {
    should_retrain: boolean;
    reasons: string[];
    data_available: number;
    data_required: number;
  };
  finbert: {
    should_retrain: boolean;
    reasons: string[];
    data_available: number;
    data_required: number;
  };
  thresholds: {
    accuracy_degradation: number;
    drift_severity: string;
    min_samples: number;
    min_predictions: number;
  };
}

export default function RetrainingPage() {
  const [status, setStatus] = useState<RetrainingStatusData | null>(null);
  const [loading, setLoading] = useState(true);
  const [retraining, setRetraining] = useState<{
    vader: boolean;
    finbert: boolean;
  }>({ vader: false, finbert: false });
  const [retrainingResult, setRetrainingResult] = useState<{
    vader: any;
    finbert: any;
  }>({ vader: null, finbert: null });

  useEffect(() => {
    loadStatus();

    // Refresh every 30 seconds
    const interval = setInterval(loadStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadStatus = async () => {
    try {
      const response = await apiClient.getRetrainingStatus();
      setStatus(response.status);
    } catch (error) {
      console.error('Failed to load retraining status:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRetrain = async (featureSet: 'vader' | 'finbert') => {
    try {
      setRetraining((prev) => ({ ...prev, [featureSet]: true }));
      setRetrainingResult((prev) => ({ ...prev, [featureSet]: null }));

      const result = await apiClient.executeRetraining(featureSet, 'random_forest', false);
      setRetrainingResult((prev) => ({ ...prev, [featureSet]: result }));

      // Refresh status after retraining
      await loadStatus();
    } catch (error) {
      console.error(`Failed to retrain ${featureSet}:`, error);
      setRetrainingResult((prev) => ({
        ...prev,
        [featureSet]: { success: false, error: 'Retraining failed' },
      }));
    } finally {
      setRetraining((prev) => ({ ...prev, [featureSet]: false }));
    }
  };

  const handleRetrainBoth = async () => {
    setRetraining({ vader: true, finbert: true });
    await Promise.all([handleRetrain('vader'), handleRetrain('finbert')]);
  };

  if (loading) {
    return (
      <div className="space-y-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {[...Array(2)].map((_, i) => (
            <div key={i} className="bg-white rounded-lg shadow p-6 animate-pulse">
              <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
              <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-2/3"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Retraining Status */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-6">Retraining Status</h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {status && (
            <>
              <RetrainingStatus featureSet="VADER" status={status.vader} color="cyan" />
              <RetrainingStatus featureSet="FinBERT" status={status.finbert} color="rose" />
            </>
          )}
        </div>

        {/* Thresholds Info */}
        {status && (
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <h4 className="font-medium text-gray-900 mb-2">Retraining Thresholds</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <p className="text-gray-600">Accuracy Drop</p>
                <p className="font-semibold">{(status.thresholds.accuracy_degradation * 100).toFixed(0)}%</p>
              </div>
              <div>
                <p className="text-gray-600">Drift Severity</p>
                <p className="font-semibold capitalize">{status.thresholds.drift_severity}</p>
              </div>
              <div>
                <p className="text-gray-600">Min Samples</p>
                <p className="font-semibold">{status.thresholds.min_samples}</p>
              </div>
              <div>
                <p className="text-gray-600">Min Predictions</p>
                <p className="font-semibold">{status.thresholds.min_predictions}</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Actions</h3>
        <div className="flex flex-wrap gap-4">
          <button
            onClick={loadStatus}
            className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
          >
            Refresh Status
          </button>

          <button
            onClick={() => handleRetrain('vader')}
            disabled={!status?.vader.should_retrain || retraining.vader}
            className={`px-6 py-3 font-medium rounded-lg transition-colors ${
              status?.vader.should_retrain && !retraining.vader
                ? 'bg-cyan-600 text-white hover:bg-cyan-700'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            {retraining.vader ? (
              <span className="flex items-center space-x-2">
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                    fill="none"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                <span>Retraining VADER...</span>
              </span>
            ) : (
              `Retrain VADER ${!status?.vader.should_retrain ? '(Insufficient Data)' : ''}`
            )}
          </button>

          <button
            onClick={() => handleRetrain('finbert')}
            disabled={!status?.finbert.should_retrain || retraining.finbert}
            className={`px-6 py-3 font-medium rounded-lg transition-colors ${
              status?.finbert.should_retrain && !retraining.finbert
                ? 'bg-rose-600 text-white hover:bg-rose-700'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            {retraining.finbert ? (
              <span className="flex items-center space-x-2">
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                    fill="none"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                <span>Retraining FinBERT...</span>
              </span>
            ) : (
              `Retrain FinBERT ${!status?.finbert.should_retrain ? '(Insufficient Data)' : ''}`
            )}
          </button>

          <button
            onClick={handleRetrainBoth}
            disabled={
              (!status?.vader.should_retrain && !status?.finbert.should_retrain) ||
              retraining.vader ||
              retraining.finbert
            }
            className={`px-6 py-3 font-medium rounded-lg transition-colors ${
              (status?.vader.should_retrain || status?.finbert.should_retrain) &&
              !retraining.vader &&
              !retraining.finbert
                ? 'bg-green-600 text-white hover:bg-green-700'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            Retrain Both Models
          </button>
        </div>
      </div>

      {/* Retraining Results */}
      {(retrainingResult.vader || retrainingResult.finbert) && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Retraining Results</h3>
          <div className="space-y-4">
            {retrainingResult.vader && (
              <div
                className={`p-4 rounded-lg ${
                  retrainingResult.vader.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
                }`}
              >
                <h4 className="font-medium mb-2">VADER Retraining</h4>
                {retrainingResult.vader.success ? (
                  <div className="text-sm space-y-1">
                    <p className="text-green-600">✓ Retraining completed successfully</p>
                    {retrainingResult.vader.result?.new_model && (
                      <>
                        <p>Test Accuracy: {(retrainingResult.vader.result.new_model.test_accuracy * 100).toFixed(1)}%</p>
                        <p>Samples Used: {retrainingResult.vader.result.samples_used}</p>
                        <p>Duration: {retrainingResult.vader.result.training_duration_seconds?.toFixed(1)}s</p>
                      </>
                    )}
                  </div>
                ) : (
                  <p className="text-red-600 text-sm">✗ {retrainingResult.vader.error || 'Retraining failed'}</p>
                )}
              </div>
            )}

            {retrainingResult.finbert && (
              <div
                className={`p-4 rounded-lg ${
                  retrainingResult.finbert.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
                }`}
              >
                <h4 className="font-medium mb-2">FinBERT Retraining</h4>
                {retrainingResult.finbert.success ? (
                  <div className="text-sm space-y-1">
                    <p className="text-green-600">✓ Retraining completed successfully</p>
                    {retrainingResult.finbert.result?.new_model && (
                      <>
                        <p>Test Accuracy: {(retrainingResult.finbert.result.new_model.test_accuracy * 100).toFixed(1)}%</p>
                        <p>Samples Used: {retrainingResult.finbert.result.samples_used}</p>
                        <p>Duration: {retrainingResult.finbert.result.training_duration_seconds?.toFixed(1)}s</p>
                      </>
                    )}
                  </div>
                ) : (
                  <p className="text-red-600 text-sm">✗ {retrainingResult.finbert.error || 'Retraining failed'}</p>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Retraining History Placeholder */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Retraining History</h3>
        </div>
        <div className="p-6 text-center text-gray-500">
          No retraining runs yet - waiting for sufficient data
        </div>
      </div>
    </div>
  );
}