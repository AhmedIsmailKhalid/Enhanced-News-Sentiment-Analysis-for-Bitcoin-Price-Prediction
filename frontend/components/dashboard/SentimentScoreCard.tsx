'use client';

import { useEffect, useMemo, useRef, useState, useCallback } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { apiClient } from '@/lib/api';
import { saveToCache, loadFromCache, formatCacheAge, isCacheStale } from '@/lib/cache';

// type SentimentModel = 'vader' | 'finbert';

interface ApiTimelinePoint {
  timestamp: string; // ISO string
  score: number; // sentiment score
}

interface ChartPoint {
  time: string; // formatted for X axis
  vader?: number;
  finbert?: number;
  // useful for debugging/tooltips if you want later:
  // timestamp?: string;
}

interface SentimentData {
  chartData: ChartPoint[];
  vaderLatest: number | null;
  finbertLatest: number | null;
}

interface SentimentCacheData {
  chartData: ChartPoint[];
  vaderLatest: number | null;
  finbertLatest: number | null;
}

const CACHE_KEY = 'sentiment_data';

export default function SentimentScoreCard() {
  const [sentimentData, setSentimentData] = useState<SentimentData | null>(null);
  const [loading, setLoading] = useState(true);
  const [isStale, setIsStale] = useState(false);
  const [cacheAge, setCacheAge] = useState<string | null>(null);

  // Avoid overlapping requests (interval + slow network)
  const isFetchingRef = useRef(false);

  // Format is stable; avoids recalculating function identity in deps
  const timeFormatter = useMemo(
    () =>
      new Intl.DateTimeFormat('en-US', {
        hour: '2-digit',
        minute: '2-digit',
      }),
    []
  );

  const combineTimelineData = useCallback(
    (vaderData: ApiTimelinePoint[], finbertData: ApiTimelinePoint[]): ChartPoint[] => {
      // Use timestamp as the join key
      const map = new Map<string, ChartPoint>();

      for (const item of vaderData) {
        const time = timeFormatter.format(new Date(item.timestamp));
        map.set(item.timestamp, { time, vader: item.score });
      }

      for (const item of finbertData) {
        const time = timeFormatter.format(new Date(item.timestamp));
        const existing = map.get(item.timestamp);
        if (existing) {
          existing.finbert = item.score;
        } else {
          map.set(item.timestamp, { time, finbert: item.score });
        }
      }

      // Sort by timestamp so the chart is in correct order
      return Array.from(map.entries())
        .sort(([a], [b]) => new Date(a).getTime() - new Date(b).getTime())
        .map(([, value]) => value);
    },
    [timeFormatter]
  );

  const loadSentimentData = useCallback(async () => {
    if (isFetchingRef.current) return;
    isFetchingRef.current = true;

    try {
      // 1) Cache first
      const cached = loadFromCache<SentimentCacheData>(CACHE_KEY);
      if (cached) {
        setSentimentData(cached.data);

        const dataIsStale = isCacheStale(cached.metadata.cachedAt, 30);
        setIsStale(dataIsStale);
        setCacheAge(formatCacheAge(cached.metadata.cachedAt));

        setLoading(false);
      }

      // 2) Fresh fetch
      const response = await apiClient.getSentimentTimeline(24, 100);

      if (response.success) {
        // Assume your API returns arrays like: { timestamp, score }
        const vaderPoints = (response.vader.data as ApiTimelinePoint[]) ?? [];
        const finbertPoints = (response.finbert.data as ApiTimelinePoint[]) ?? [];

        const combined = combineTimelineData(vaderPoints, finbertPoints);

        const newData: SentimentData = {
          chartData: combined,
          vaderLatest: response.vader.latest_score ?? null,
          finbertLatest: response.finbert.latest_score ?? null,
        };

        setSentimentData(newData);
        setIsStale(false);
        setCacheAge(null);

        saveToCache<SentimentCacheData>(CACHE_KEY, newData);
      }
    } catch (error) {
      console.error('Failed to load sentiment data:', error);
    } finally {
      setLoading(false);
      isFetchingRef.current = false;
    }
  }, [combineTimelineData]);

  useEffect(() => {
    loadSentimentData();

    const interval = setInterval(() => {
      loadSentimentData();
    }, 30000);

    return () => clearInterval(interval);
  }, [loadSentimentData]);

  const getSentimentLabel = (score: number | null) => {
    if (score === null) return 'N/A';
    if (score > 0.05) return 'Positive';
    if (score < -0.05) return 'Negative';
    return 'Neutral';
  };

  const getSentimentColor = (score: number | null) => {
    if (score === null) return 'text-gray-500';
    if (score > 0.05) return 'text-green-600';
    if (score < -0.05) return 'text-red-600';
    return 'text-gray-600';
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/2 mb-4"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (!sentimentData) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Sentiment Score</h3>
        <div className="flex items-center justify-center h-64 text-gray-500">
          <p>No sentiment data available</p>
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
        <h3 className="text-lg font-semibold text-gray-900">Sentiment Score</h3>
        {!isStale && (
          <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">
            ● Live
          </span>
        )}
      </div>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="p-4 border-l-4 border-cyan-500 bg-cyan-50 rounded">
          <p className="text-sm text-gray-600">VADER</p>
          <p className={`text-2xl font-bold ${getSentimentColor(sentimentData.vaderLatest)}`}>
            {sentimentData.vaderLatest !== null ? sentimentData.vaderLatest.toFixed(3) : 'N/A'}
          </p>
          <p className={`text-sm ${getSentimentColor(sentimentData.vaderLatest)}`}>
            {getSentimentLabel(sentimentData.vaderLatest)}
          </p>
        </div>

        <div className="p-4 border-l-4 border-rose-500 bg-rose-50 rounded">
          <p className="text-sm text-gray-600">FinBERT</p>
          <p className={`text-2xl font-bold ${getSentimentColor(sentimentData.finbertLatest)}`}>
            {sentimentData.finbertLatest !== null ? sentimentData.finbertLatest.toFixed(3) : 'N/A'}
          </p>
          <p className={`text-sm ${getSentimentColor(sentimentData.finbertLatest)}`}>
            {getSentimentLabel(sentimentData.finbertLatest)}
          </p>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={sentimentData.chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="time" stroke="#6b7280" style={{ fontSize: '11px' }} />
          <YAxis stroke="#6b7280" style={{ fontSize: '11px' }} domain={[-1, 1]} />
          <Tooltip
            contentStyle={{
              backgroundColor: 'white',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              padding: '8px',
            }}
          />
          <Legend />
          <Line type="monotone" dataKey="vader" stroke="#06b6d4" name="VADER" strokeWidth={2} dot={false} />
          <Line
            type="monotone"
            dataKey="finbert"
            stroke="#f43f5e"
            name="FinBERT"
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>

      <div className="mt-4 text-xs text-gray-500 text-center">Range: -1 (Negative) to +1 (Positive)</div>
    </div>
  );
}
