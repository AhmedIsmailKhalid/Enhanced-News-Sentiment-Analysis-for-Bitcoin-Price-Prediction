'use client';

import { useEffect, useState, useRef, useCallback } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { apiClient, getIsUsingGoldenDataset } from '@/lib/api';
import { saveToCache, loadFromCache, formatCacheAge, isCacheStale } from '@/lib/cache';

interface PricePoint {
  timestamp: string;
  price: number;
  volume_24h: number | null;
  change_24h: number | null;
}

interface PriceCacheData {
  data: PricePoint[];
  latestPrice: number | null;
  latestTimestamp: string;
  timeRange: number;
}

const CACHE_KEY = 'price_data';

export default function RealtimePriceChart() {
  const [priceData, setPriceData] = useState<PricePoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [latestPrice, setLatestPrice] = useState<number | null>(null);
  const [lastUpdate, setLastUpdate] = useState<string>('');
  const [isUpdating, setIsUpdating] = useState(false);
  const [timeRange, setTimeRange] = useState<number>(24);
  const [isStale, setIsStale] = useState(false);
  const [cacheAge, setCacheAge] = useState<string | null>(null);
  const [usingGolden, setUsingGolden] = useState(false);

  const previousCountRef = useRef<number>(0);
  const updateTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price);
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);

    if (timeRange <= 24) {
      return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
      });
    } else if (timeRange <= 168) {
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
      });
    } else {
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
      });
    }
  };

  const loadPriceData = useCallback(async () => {
    try {
      // 1) Load from cache first (if available)
      const cached = loadFromCache<PriceCacheData>(CACHE_KEY);

      if (cached && cached.data.timeRange === timeRange) {
        setPriceData(cached.data.data);
        setLatestPrice(cached.data.latestPrice);
        setLastUpdate(new Date(cached.data.latestTimestamp).toLocaleTimeString());

        const isDataStale = isCacheStale(cached.metadata.cachedAt, 30);
        setIsStale(isDataStale);
        setCacheAge(formatCacheAge(cached.metadata.cachedAt));

        setLoading(false);
      }

      // 2) Fetch fresh data regardless
      const response = await apiClient.getRecentPrices('BTC', timeRange, 200);

      if (response.data?.length) {
        setPriceData(response.data);
        setLatestPrice(response.latest_price);
        setLastUpdate(new Date(response.latest_timestamp || '').toLocaleTimeString());
        previousCountRef.current = response.count;

        setIsStale(false);
        setCacheAge(null);
        
        // Check if using golden dataset
        setUsingGolden(getIsUsingGoldenDataset());

        saveToCache<PriceCacheData>(CACHE_KEY, {
          data: response.data,
          latestPrice: response.latest_price,
          latestTimestamp: response.latest_timestamp || new Date().toISOString(),
          timeRange,
        });
      }
    } catch (error) {
      console.error('Failed to load price data:', error);
      // On error, check golden status
      setUsingGolden(getIsUsingGoldenDataset());
    } finally {
      setLoading(false);
    }
  }, [timeRange]);

  const checkForNewData = useCallback(async () => {
    try {
      const response = await apiClient.getRecentPrices('BTC', timeRange, 200);

      // Update golden dataset status
      setUsingGolden(getIsUsingGoldenDataset());

      // Only update if NEW data (count increased)
      if (response.count > previousCountRef.current) {
        setIsUpdating(true);
        setPriceData(response.data);
        setLatestPrice(response.latest_price);
        setLastUpdate(new Date(response.latest_timestamp || '').toLocaleTimeString());
        previousCountRef.current = response.count;

        setIsStale(false);
        setCacheAge(null);

        saveToCache<PriceCacheData>(CACHE_KEY, {
          data: response.data,
          latestPrice: response.latest_price,
          latestTimestamp: response.latest_timestamp || new Date().toISOString(),
          timeRange,
        });

        // Flash update indicator (clear previous timeout if any)
        if (updateTimeoutRef.current) clearTimeout(updateTimeoutRef.current);
        updateTimeoutRef.current = setTimeout(() => setIsUpdating(false), 1000);
      }
    } catch (error) {
      console.error('Failed to check for new data:', error);
      // On error, definitely check golden status
      setUsingGolden(getIsUsingGoldenDataset());
    }
  }, [timeRange]);

  useEffect(() => {
    loadPriceData();
  }, [loadPriceData]);

  useEffect(() => {
    const interval = setInterval(() => {
      checkForNewData();
    }, 10000);

    return () => clearInterval(interval);
  }, [checkForNewData]);

  // Cleanup any pending timeout on unmount
  useEffect(() => {
    return () => {
      if (updateTimeoutRef.current) clearTimeout(updateTimeoutRef.current);
    };
  }, []);

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (!priceData || priceData.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Bitcoin Price (24h)</h3>
        <div className="flex items-center justify-center h-64 text-gray-500">
          <p>No price data available. Waiting for data collection...</p>
        </div>
      </div>
    );
  }

  const sampleInterval = Math.ceil(priceData.length / 20);
  const chartData = priceData
    .filter((_, index) => index % sampleInterval === 0 || index === priceData.length - 1)
    .map((point) => ({
      time: formatTimestamp(point.timestamp),
      price: point.price,
      fullTimestamp: point.timestamp,
    }));

  return (
    <div className="bg-white rounded-lg shadow p-6">
      {/* Stale Data Warning Banner - only show if NOT using golden dataset */}
      {!usingGolden && isStale && cacheAge && (
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
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Bitcoin Price</h3>
          <div className="flex items-center space-x-3 mt-1">
            {latestPrice !== null && (
              <span className="text-2xl font-bold text-gray-900">{formatPrice(latestPrice)}</span>
            )}

            {/* Sample Data Badge */}
            {usingGolden && (
              <span className="px-2 py-1 text-xs font-medium bg-amber-100 text-amber-800 rounded">
                📊 Sample Data
              </span>
            )}

            {/* Live Update Flash */}
            {isUpdating && !usingGolden && (
              <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded animate-pulse">
                ● Live Update
              </span>
            )}

            {/* Live Indicator - only show if NOT stale AND NOT updating AND NOT using golden */}
            {!isStale && !isUpdating && !usingGolden && (
              <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">
                ● Live
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(Number(e.target.value))}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500"
          >
            <option value={1}>1 Hour</option>
            <option value={2}>2 Hours</option>
            <option value={6}>6 Hours</option>
            <option value={12}>12 Hours</option>
            <option value={24}>24 Hours</option>
            <option value={168}>7 Days</option>
            <option value={336}>14 Days</option>
            <option value={720}>30 Days</option>
            <option value={1440}>60 Days</option>
            <option value={2160}>90 Days</option>
          </select>

          <div className="text-right">
            <p className="text-sm text-gray-600">Last Update</p>
            <p className="text-sm font-medium text-gray-900">{lastUpdate}</p>
            <p className="text-xs text-gray-500 mt-1">{priceData.length} data points</p>
          </div>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="time"
            stroke="#6b7280"
            style={{ fontSize: '12px' }}
            angle={timeRange > 24 ? -45 : 0}
            textAnchor={timeRange > 24 ? 'end' : 'middle'}
            height={timeRange > 24 ? 80 : 30}
          />
          <YAxis
            stroke="#6b7280"
            style={{ fontSize: '12px' }}
            tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'white',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              padding: '8px',
            }}
            formatter={(value: number) => [formatPrice(value), 'Price']}
            labelFormatter={(label) => `Time: ${label}`}
          />
          <Line
            type="monotone"
            dataKey="price"
            stroke="#f59e0b"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 6, fill: '#f59e0b' }}
          />
        </LineChart>
      </ResponsiveContainer>

      <div className="mt-4 flex items-center justify-between text-xs text-gray-500">
        <span>
          {usingGolden 
            ? 'Sample data updates every 30s to demonstrate system' 
            : 'Auto-updates when new data is collected'}
        </span>
        <span className="flex items-center space-x-1">
          <div
            className={`h-2 w-2 rounded-full ${
              usingGolden ? 'bg-amber-500' : isStale ? 'bg-yellow-500' : 'bg-green-500 animate-pulse'
            }`}
          ></div>
          <span>{usingGolden ? 'Sample' : isStale ? 'Updating...' : 'Live'}</span>
        </span>
      </div>
    </div>
  );
}