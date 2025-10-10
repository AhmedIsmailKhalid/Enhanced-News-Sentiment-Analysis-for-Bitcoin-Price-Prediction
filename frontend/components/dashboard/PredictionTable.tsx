'use client';

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api';
import type { PredictionLog } from '@/lib/types';

export default function PredictionTable() {
  const [predictions, setPredictions] = useState<PredictionLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadPredictions();
    
    // Auto-refresh every 30 seconds for real-time updates
    const interval = setInterval(() => {
      loadPredictions();
    }, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const loadPredictions = async () => {
    try {
      setLoading(true);
      const response = await apiClient.getRecentPredictions(undefined, 10);
      setPredictions(response.predictions || []);
      setError(null);
    } catch (err) {
      setError('Failed to load predictions');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    
    if (minutes < 1) return 'just now';
    if (minutes < 60) return `${minutes} min ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    return date.toLocaleDateString();
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Predictions</h3>
        <div className="animate-pulse space-y-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-12 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Recent Predictions</h3>
        <div className="flex items-center space-x-3">
          <span className="text-xs text-gray-500">Auto-refresh: 30s</span>
          <button
            onClick={loadPredictions}
            disabled={loading}
            className="text-sm text-cyan-600 hover:text-cyan-700 font-medium disabled:opacity-50"
          >
            {loading ? 'Refreshing...' : 'Refresh Now'}
          </button>
        </div>
      </div>
      
      {error && (
        <div className="px-6 py-4 bg-red-50 border-b border-red-200">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Timestamp
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Model
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Prediction
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Confidence
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Response
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {predictions.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-6 py-8 text-center text-gray-500">
                  No predictions yet
                </td>
              </tr>
            ) : (
              predictions.map((pred) => (
                <tr key={pred.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatTimestamp(pred.predicted_at)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded ${
                        pred.feature_set === 'vader'
                          ? 'bg-cyan-100 text-cyan-800'
                          : 'bg-rose-100 text-rose-800'
                      }`}
                    >
                      {pred.feature_set.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`font-medium ${
                        pred.prediction === 1 ? 'text-green-600' : 'text-red-600'
                      }`}
                    >
                      {pred.prediction === 1 ? '↑ UP' : '↓ DOWN'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {(pred.confidence * 100).toFixed(1)}%
                  </td>                  
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {pred.response_time_ms.toFixed(0)}ms
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}