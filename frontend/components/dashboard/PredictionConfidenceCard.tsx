'use client';

import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { apiClient } from '@/lib/api';
import { saveToCache, loadFromCache, formatCacheAge, isCacheStale } from '@/lib/cache';
import type { PredictionLog } from '@/lib/types';

interface ChartDataPoint {
  index: number;
  vader: number | null;
  finbert: number | null;
}

interface ConfidenceCacheData {
  chartData: ChartDataPoint[];
  vaderAvg: number;
  finbertAvg: number;
}

const CACHE_KEY = 'prediction_confidence';

export default function PredictionConfidenceCard() {
  const [confidenceData, setConfidenceData] = useState<ConfidenceCacheData | null>(null);
  const [loading, setLoading] = useState(true);
  const [isStale, setIsStale] = useState(false);
  const [cacheAge, setCacheAge] = useState<string | null>(null);

  useEffect(() => {
    loadConfidenceData();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadConfidenceData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadConfidenceData = async () => {
    try {
      // 1. Try to load from cache first
      const cached = loadFromCache<ConfidenceCacheData>(CACHE_KEY);
      if (cached) {
        console.log('Loading confidence data from cache');
        setConfidenceData(cached.data);
        
        const isDataStale = isCacheStale(cached.metadata.cachedAt, 30);
        setIsStale(isDataStale);
        setCacheAge(formatCacheAge(cached.metadata.cachedAt));
        
        setLoading(false);
      }

      // 2. Fetch fresh data from API (with golden dataset fallback)
      const response = await apiClient.getRecentPredictions(undefined, 25);
      
      if (response && response.predictions && response.predictions.length > 0) {
        const chartData: ChartDataPoint[] = response.predictions.map((pred: PredictionLog, index: number) => ({
          index: index + 1,
          vader: pred.feature_set === 'vader' ? (pred.confidence * 100) : null,
          finbert: pred.feature_set === 'finbert' ? (pred.confidence * 100) : null,
        }));

        // Calculate averages
        const vaderPreds = response.predictions.filter((p: PredictionLog) => p.feature_set === 'vader');
        const finbertPreds = response.predictions.filter((p: PredictionLog) => p.feature_set === 'finbert');
        
        const vaderAvg = vaderPreds.length > 0
          ? vaderPreds.reduce((sum: number, p: PredictionLog) => sum + p.confidence, 0) / vaderPreds.length * 100
          : 0;
        
        const finbertAvg = finbertPreds.length > 0
          ? finbertPreds.reduce((sum: number, p: PredictionLog) => sum + p.confidence, 0) / finbertPreds.length * 100
          : 0;

        const newData: ConfidenceCacheData = {
          chartData,
          vaderAvg,
          finbertAvg,
        };

        setConfidenceData(newData);
        setIsStale(false);
        setCacheAge(null);

        // Save to cache
        saveToCache<ConfidenceCacheData>(CACHE_KEY, newData);
      }
    } catch (error) {
      console.error('Failed to load confidence data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading && !confidenceData) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-2/3 mb-4"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (!confidenceData || confidenceData.chartData.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Prediction Confidence (Recent)
        </h3>
        <div className="flex items-center justify-center h-64 text-gray-500">
          <p>No prediction data available</p>
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
          Prediction Confidence (Recent)
        </h3>
        {!isStale && (
          <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">
            ● Live
          </span>
        )}
      </div>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="text-center p-4 bg-cyan-50 rounded-lg">
          <p className="text-sm text-gray-600">VADER Avg</p>
          <p className="text-3xl font-bold text-cyan-600">
            {confidenceData.vaderAvg ? confidenceData.vaderAvg.toFixed(1) : '0.0'}%
          </p>
          <p className="text-xs text-gray-500 mt-1">
            Last {confidenceData.chartData.filter((d: ChartDataPoint) => d.vader !== null).length} predictions
          </p>
        </div>

        <div className="text-center p-4 bg-rose-50 rounded-lg">
          <p className="text-sm text-gray-600">FinBERT Avg</p>
          <p className="text-3xl font-bold text-rose-600">
            {confidenceData.finbertAvg ? confidenceData.finbertAvg.toFixed(1) : '0.0'}%
          </p>
          <p className="text-xs text-gray-500 mt-1">
            Last {confidenceData.chartData.filter((d: ChartDataPoint) => d.finbert !== null).length} predictions
          </p>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={240}>
        <LineChart data={confidenceData.chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis 
            dataKey="index" 
            label={{ value: 'Prediction #', position: 'insideBottom', offset: -5 }}
            stroke="#6b7280"
            style={{ fontSize: '12px' }}
          />
          <YAxis 
            label={{ value: 'Confidence (%)', angle: -90, position: 'insideLeft' }}
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
            dot={{ r: 3 }}
          />
          <Line 
            type="monotone" 
            dataKey="finbert" 
            stroke="#f43f5e" 
            strokeWidth={2}
            name="FinBERT"
            connectNulls
            dot={{ r: 3 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}