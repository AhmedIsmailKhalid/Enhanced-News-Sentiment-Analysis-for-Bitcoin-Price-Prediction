'use client';

import { useState, useEffect } from 'react';
import RealtimePriceChart from '@/components/dashboard/RealtimePriceChart';
import SentimentScoreCard from '@/components/dashboard/SentimentScoreCard';
import PredictionAccuracyCard from '@/components/dashboard/PredictionAccuracyCard';
import PredictionConfidenceCard from '@/components/dashboard/PredictionConfidenceCard';
import PredictionTable from '@/components/dashboard/PredictionTable';
import { apiClient, getIsUsingGoldenDataset } from '@/lib/api';
import { saveToCache, loadFromCache, formatCacheAge, isCacheStale } from '@/lib/cache';

interface StatisticsCacheData {
  total_predictions: number;
  predictions_with_outcomes: number;
  vader_accuracy: number;
  finbert_accuracy: number;
  avg_response_time_ms: number;
}

const CACHE_KEY = 'statistics';

export default function OverviewPage() {
  const [statistics, setStatistics] = useState<StatisticsCacheData | null>(null);
  const [isStale, setIsStale] = useState(false);
  const [cacheAge, setCacheAge] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [usingGolden, setUsingGolden] = useState(false);

  useEffect(() => {
    loadStatistics();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadStatistics, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadStatistics = async () => {
    try {
      // 1. Try to load from cache first
      const cached = loadFromCache<StatisticsCacheData>(CACHE_KEY);
      if (cached) {
        console.log('Loading statistics from cache');
        setStatistics(cached.data);
        
        const isDataStale = isCacheStale(cached.metadata.cachedAt, 30);
        setIsStale(isDataStale);
        setCacheAge(formatCacheAge(cached.metadata.cachedAt));
        setLoading(false);
      }

      // 2. Fetch fresh data from API
      const response = await apiClient.getStatistics();
      
      if (response) {
        setStatistics(response);
        setIsStale(false);
        setCacheAge(null);
        
        // Check if using golden dataset
        setUsingGolden(getIsUsingGoldenDataset());

        // Save to cache
        saveToCache<StatisticsCacheData>(CACHE_KEY, response);
      }
    } catch (error) {
      console.error('Failed to load statistics:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Golden Dataset Banner */}
      {usingGolden && (
        <div className="mb-6 px-4 py-3 bg-amber-50 border-l-4 border-amber-500 rounded-lg">
          <div className="flex items-start">
            <span className="text-amber-600 text-xl mr-3">⚠️</span>
            <div>
              <h3 className="text-sm font-semibold text-amber-900">Demo Mode - Sample Data</h3>
              <p className="text-sm text-amber-800 mt-1">
                Automated data collection disabled to preserve NeonDB free tier.
                Sample data updates every 30s to demonstrate system capabilities.
              </p>
              <p className="text-xs text-amber-700 mt-2">
                💡 Enable GitHub Actions workflow for real-time updates
              </p>
            </div>
          </div>
        </div>
      )}

      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Bitcoin Sentiment MLOps</h1>
        <p className="mt-2 text-gray-600">
          Real-time sentiment analysis and price prediction monitoring
        </p>
      </div>

      {/* Stale Statistics Warning Banner (only show if NOT using golden dataset) */}
      {!usingGolden && isStale && cacheAge && (
        <div className="mb-6 px-4 py-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <div className="flex items-center space-x-2">
            <span className="text-yellow-600">⚠️</span>
            <span className="text-sm text-yellow-800">
              Dashboard showing cached data from <strong>{cacheAge}</strong>. Fetching latest updates...
            </span>
          </div>
        </div>
      )}

      {/* Statistics Summary Cards */}
      {loading && !statistics ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-white rounded-lg shadow p-6 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
              <div className="h-8 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      ) : statistics ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Total Predictions */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Predictions</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  {statistics.total_predictions || 0}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {statistics.predictions_with_outcomes || 0} with outcomes
                </p>
              </div>
              {!isStale && !usingGolden && (
                <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse"></div>
              )}
              {usingGolden && (
                <span className="px-2 py-1 text-xs bg-amber-100 text-amber-800 rounded">
                  Sample
                </span>
              )}
            </div>
          </div>

          {/* VADER Accuracy */}
          <div className="bg-white rounded-lg shadow p-6 border-l-4 border-cyan-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">VADER Accuracy</p>
                <p className="text-3xl font-bold text-cyan-600 mt-2">
                  {statistics.vader_accuracy ? statistics.vader_accuracy.toFixed(1) : '0.0'}%
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Random Forest model
                </p>
              </div>
              {usingGolden && (
                <span className="px-2 py-1 text-xs bg-amber-100 text-amber-800 rounded">
                  Sample
                </span>
              )}
            </div>
          </div>

          {/* FinBERT Accuracy */}
          <div className="bg-white rounded-lg shadow p-6 border-l-4 border-rose-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">FinBERT Accuracy</p>
                <p className="text-3xl font-bold text-rose-600 mt-2">
                  {statistics.finbert_accuracy ? statistics.finbert_accuracy.toFixed(1) : '0.0'}%
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Random Forest model
                </p>
              </div>
              {usingGolden && (
                <span className="px-2 py-1 text-xs bg-amber-100 text-amber-800 rounded">
                  Sample
                </span>
              )}
            </div>
          </div>

          {/* Avg Response Time */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Avg Response Time</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  {statistics.avg_response_time_ms ? statistics.avg_response_time_ms.toFixed(0) : '0'}ms
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {statistics.avg_response_time_ms && statistics.avg_response_time_ms < 200
                    ? `${(200 - statistics.avg_response_time_ms).toFixed(0)}ms under target`
                    : statistics.avg_response_time_ms 
                    ? `${(statistics.avg_response_time_ms - 200).toFixed(0)}ms over target`
                    : 'Target: <200ms'}
                </p>
              </div>
              {statistics.avg_response_time_ms && statistics.avg_response_time_ms < 200 && !usingGolden && (
                <span className="text-green-500 text-2xl">✓</span>
              )}
              {usingGolden && (
                <span className="px-2 py-1 text-xs bg-amber-100 text-amber-800 rounded">
                  Sample
                </span>
              )}
            </div>
          </div>
        </div>
      ) : null}

      {/* Top Row: Price and Sentiment Charts */}
      <div className="grid grid-cols-2 gap-6 mb-6">
        <RealtimePriceChart />
        <SentimentScoreCard />
      </div>

      {/* Second Row: Confidence and Accuracy Charts */}
      <div className="grid grid-cols-2 gap-6 mb-6">
        <PredictionConfidenceCard />
        <PredictionAccuracyCard />
      </div>

      {/* Bottom Row: Recent Predictions Table */}
      <PredictionTable />
    </div>
  );
}