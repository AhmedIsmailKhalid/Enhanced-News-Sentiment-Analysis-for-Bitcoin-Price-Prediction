'use client';

import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { apiClient } from '@/lib/api';
import { saveToCache, loadFromCache, formatCacheAge, isCacheStale } from '@/lib/cache';

interface AccuracyCacheData {
  chartData: Array<{
    window: number;
    vader: number | null;
    finbert: number | null;
  }>;
  vaderOverall: number;
  finbertOverall: number;
}

const CACHE_KEY = 'model_accuracy';

export default function PredictionAccuracyCard() {
  const [accuracyData, setAccuracyData] = useState<AccuracyCacheData | null>(null);
  const [loading, setLoading] = useState(true);
  const [isStale, setIsStale] = useState(false);
  const [cacheAge, setCacheAge] = useState<string | null>(null);

  useEffect(() => {
    loadAccuracyData();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadAccuracyData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadAccuracyData = async () => {
    try {
      // 1. Try to load from cache first
      const cached = loadFromCache<AccuracyCacheData>(CACHE_KEY);
      if (cached) {
        console.log('Loading accuracy data from cache');
        setAccuracyData(cached.data);
        
        const isDataStale = isCacheStale(cached.metadata.cachedAt, 60);
        setIsStale(isDataStale);
        setCacheAge(formatCacheAge(cached.metadata.cachedAt));
        
        setLoading(false);
      }

      // 2. Fetch fresh data from API (with golden dataset fallback)
      const [vaderResponse, finbertResponse] = await Promise.all([
        apiClient.getModelAccuracy('vader', 'random_forest'),
        apiClient.getModelAccuracy('finbert', 'random_forest'),
      ]);

      // Extract accuracy stats from response
      const vaderStats = vaderResponse.accuracy_stats;
      const finbertStats = finbertResponse.accuracy_stats;

      // Get rolling window accuracy for chart
      const rollingWindows = [10, 20, 30, 40, 50];
      const chartData = rollingWindows.map(window => ({
        window: window,
        vader: vaderStats.accuracy_by_window?.[window] ? vaderStats.accuracy_by_window[window] * 100 : null,
        finbert: finbertStats.accuracy_by_window?.[window] ? finbertStats.accuracy_by_window[window] * 100 : null,
      }));

      const newData = {
        chartData,
        vaderOverall: vaderStats.overall_accuracy * 100,
        finbertOverall: finbertStats.overall_accuracy * 100,
      };

      setAccuracyData(newData);
      setIsStale(false);
      setCacheAge(null);

      // Save to cache
      saveToCache<AccuracyCacheData>(CACHE_KEY, newData);
    } catch (error) {
      console.error('Failed to load accuracy data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading && !accuracyData) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-2/3 mb-4"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (!accuracyData) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Model Accuracy (Rolling Window)
        </h3>
        <div className="flex items-center justify-center h-64 text-gray-500">
          <p>No accuracy data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      {/* Stale Data Warning Banner */}
      {isStale && cacheAge && (
        <div className="mb-4 px-4 py-2 bg-yellow-50 border border-yellow-200 rounded-lg">
          <div className="flex items-center space-x-2">
            <span className="text-yellow-600">⚠️</span>
            <span className="text-sm text-yellow-800">
              Showing cached data from <strong>{cacheAge}</strong>. Fetching live data...
            </span>
          </div>
        </div>
      )}

      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          Model Accuracy (Rolling Window)
        </h3>
        {!isStale && (
          <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">
            ● Live
          </span>
        )}
      </div>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="text-center p-4 bg-cyan-50 rounded-lg">
          <p className="text-sm text-gray-600">VADER Overall</p>
          <p className="text-3xl font-bold text-cyan-600">
            {accuracyData.vaderOverall ? accuracyData.vaderOverall.toFixed(1) : '0.0'}%
          </p>
          <p className="text-xs text-gray-500 mt-1">
            All predictions with outcomes
          </p>
        </div>

        <div className="text-center p-4 bg-rose-50 rounded-lg">
          <p className="text-sm text-gray-600">FinBERT Overall</p>
          <p className="text-3xl font-bold text-rose-600">
            {accuracyData.finbertOverall ? accuracyData.finbertOverall.toFixed(1) : '0.0'}%
          </p>
          <p className="text-xs text-gray-500 mt-1">
            All predictions with outcomes
          </p>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={240}>
        <LineChart data={accuracyData.chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis 
            dataKey="window" 
            label={{ value: 'Prediction Window', position: 'insideBottom', offset: -5 }}
            stroke="#6b7280"
            style={{ fontSize: '12px' }}
          />
          <YAxis 
            label={{ value: 'Accuracy (%)', angle: -90, position: 'insideLeft' }}
            domain={[0, 100]}
            stroke="#6b7280"
            style={{ fontSize: '12px' }}
          />
          <Tooltip 
            contentStyle={{
              backgroundColor: 'white',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              padding: '8px'
            }}
            formatter={(value: unknown) => {
              const numValue = value as number | null;
              if (numValue === null || numValue === undefined) return ['N/A', ''];
              return [`${numValue.toFixed(1)}%`, ''];
            }}
          />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="vader" 
            stroke="#06b6d4" 
            strokeWidth={2}
            name="VADER"
            connectNulls
            dot={{ r: 4 }}
          />
          <Line 
            type="monotone" 
            dataKey="finbert" 
            stroke="#f43f5e" 
            strokeWidth={2}
            name="FinBERT"
            connectNulls
            dot={{ r: 4 }}
          />
        </LineChart>
      </ResponsiveContainer>

      <div className="mt-4 text-xs text-gray-500 text-center">
        Rolling accuracy calculated over 10, 20, 30, 40, 50 prediction windows
      </div>
    </div>
  );
}