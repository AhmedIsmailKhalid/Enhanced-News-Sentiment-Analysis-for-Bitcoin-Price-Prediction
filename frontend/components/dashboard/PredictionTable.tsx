'use client';

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api';
import { saveToCache, loadFromCache, formatCacheAge, isCacheStale } from '@/lib/cache';
import type { PredictionLog } from '@/lib/types';

interface PredictionsCacheData {
  predictions: PredictionLog[];
}

const CACHE_KEY = 'recent_predictions';

export default function PredictionTable() {
  const [predictions, setPredictions] = useState<PredictionLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isStale, setIsStale] = useState(false);
  const [cacheAge, setCacheAge] = useState<string | null>(null);

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
      // 1. Try to load from cache first
      const cached = loadFromCache<PredictionsCacheData>(CACHE_KEY);
      if (cached) {
        console.log('Loading predictions from cache');
        setPredictions(cached.data.predictions);
        
        const isDataStale = isCacheStale(cached.metadata.cachedAt, 30);
        setIsStale(isDataStale);
        setCacheAge(formatCacheAge(cached.metadata.cachedAt));
        
        setLoading(false);
      }

      // 2. Fetch fresh data from API
      const response = await apiClient.getRecentPredictions(undefined, 10);
      setPredictions(response.predictions || []);
      setError(null);
      setIsStale(false);
      setCacheAge(null);

      // Save to cache
      saveToCache<PredictionsCacheData>(CACHE_KEY, {
        predictions: response.predictions || [],
      });
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
          {isStale && cacheAge && (
            <span className="text-xs text-yellow-600">
              Cached: {cacheAge}
            </span>
          )}
          {!isStale && (
            <span className="text-xs text-green-600 flex items-center">
              <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse mr-1"></div>
              Live
            </span>
          )}
          <span className="text-xs text-gray-500">Auto-refresh: 30s</span>
          <button
            onClick={loadPredictions}
            disabled={loading}
            className="text-sm text-cyan-600 hover:text-cyan-700 font-medium disabled:opacity-50"
          >
            {loading ? '...' : 'Refresh'}
          </button>
        </div>
      </div>

      {error && (
        <div className="px-6 py-4 bg-red-50 text-red-600 text-sm">
          {error}
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Time
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
                Outcome
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Response
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {predictions.map((prediction) => (
              <tr key={prediction.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {formatTimestamp(prediction.predicted_at)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    prediction.feature_set === 'vader' 
                      ? 'bg-cyan-100 text-cyan-800' 
                      : 'bg-rose-100 text-rose-800'
                  }`}>
                    {prediction.feature_set.toUpperCase()}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex items-center text-sm font-medium ${
                    prediction.prediction === 1 
                      ? 'text-green-600' 
                      : 'text-red-600'
                  }`}>
                    {prediction.prediction === 1 ? '↑ UP' : '↓ DOWN'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {(prediction.confidence * 100).toFixed(1)}%
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {prediction.actual_direction === null ? (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
                      Pending
                    </span>
                  ) : prediction.actual_direction === prediction.prediction ? (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      ✓ Correct
                    </span>
                  ) : (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                      ✗ Wrong
                    </span>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {prediction.response_time_ms ? `${prediction.response_time_ms}ms` : 'N/A'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {predictions.length === 0 && !loading && (
        <div className="px-6 py-12 text-center text-gray-500">
          No predictions available yet
        </div>
      )}
    </div>
  );
}