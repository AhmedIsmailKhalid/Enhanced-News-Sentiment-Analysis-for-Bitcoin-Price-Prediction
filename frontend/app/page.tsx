'use client';

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api';
import MetricCard from '@/components/dashboard/MetricCard';
import AccuracyChart from '@/components/dashboard/AccuracyChart';
import PredictionTable from '@/components/dashboard/PredictionTable';
import type { AccuracyStats, Statistics } from '@/lib/types';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import RealtimePriceChart from '@/components/dashboard/RealtimePriceChart';

export default function OverviewPage() {
  const [vaderAccuracy, setVaderAccuracy] = useState<AccuracyStats | null>(null);
  const [finbertAccuracy, setFinbertAccuracy] = useState<AccuracyStats | null>(null);
  const [statistics, setStatistics] = useState<Statistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [showBarChart, setShowBarChart] = useState(false);

  const [chartData, setChartData] = useState<
    Array<{ date: string; vader?: number; finbert?: number }>
  >([]);

  useEffect(() => {
    loadData();

    // Refresh every 30 seconds
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const [vaderResp, finbertResp, statsResp, vaderDaily, finbertDaily] = await Promise.all([
        apiClient.getModelAccuracy('vader', 'random_forest', 30),
        apiClient.getModelAccuracy('finbert', 'random_forest', 30),
        apiClient.getStatistics(),
        apiClient.getDailyAccuracy('vader', 'random_forest', 7),
        apiClient.getDailyAccuracy('finbert', 'random_forest', 7),
      ]);

      setVaderAccuracy(vaderResp.accuracy_stats);
      setFinbertAccuracy(finbertResp.accuracy_stats);
      setStatistics(statsResp.statistics);

      // Combine daily accuracy data
      const dailyMap = new Map<string, { date: string; vader?: number; finbert?: number }>();

      vaderDaily.daily_accuracy.forEach((day) => {
        const shortDate = new Date(day.date).toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric',
        });
        dailyMap.set(day.date, { date: shortDate, vader: day.accuracy || 0 });
      });

      finbertDaily.daily_accuracy.forEach((day) => {
        const shortDate = new Date(day.date).toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric',
        });
        const existing = dailyMap.get(day.date) || { date: shortDate };
        dailyMap.set(day.date, { ...existing, finbert: day.accuracy || 0 });
      });

      const combined = Array.from(dailyMap.values()).filter(
        (item) => item.vader !== undefined || item.finbert !== undefined
      );

      setChartData(combined);
    } catch (error) {
      console.error('Failed to load overview data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatAccuracy = (
    accuracy: number | null | undefined,
    predictions: number | null | undefined
  ) => {
    if (accuracy === null || accuracy === undefined) return 'N/A';
    if (predictions === 0 || predictions === null || predictions === undefined) return 'N/A';
    return `${(accuracy * 100).toFixed(0)}%`;
  };

  const getBarChartData = () => {
    return [
      {
        model: 'VADER',
        'UP Accuracy': vaderAccuracy?.up_accuracy ? vaderAccuracy.up_accuracy * 100 : 0,
        'DOWN Accuracy': vaderAccuracy?.down_accuracy ? vaderAccuracy.down_accuracy * 100 : 0,
      },
      {
        model: 'FinBERT',
        'UP Accuracy': finbertAccuracy?.up_accuracy ? finbertAccuracy.up_accuracy * 100 : 0,
        'DOWN Accuracy': finbertAccuracy?.down_accuracy ? finbertAccuracy.down_accuracy * 100 : 0,
      },
    ];
  };

  if (loading) {
    return (
      <div className="space-y-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-white rounded-lg shadow p-6 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
              <div className="h-8 bg-gray-200 rounded w-3/4"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="VADER Accuracy"
          value={vaderAccuracy?.accuracy ? `${(vaderAccuracy.accuracy * 100).toFixed(1)}%` : 'N/A'}
          subtitle={`Last 30 days (${vaderAccuracy?.total_predictions || 0} predictions)`}
          color="cyan"
        />
        <MetricCard
          title="FinBERT Accuracy"
          value={
            finbertAccuracy?.accuracy ? `${(finbertAccuracy.accuracy * 100).toFixed(1)}%` : 'N/A'
          }
          subtitle={`Last 30 days (${finbertAccuracy?.total_predictions || 0} predictions)`}
          color="rose"
        />
        <MetricCard
          title="Total Predictions"
          value={statistics?.total_predictions || 0}
          subtitle={`${statistics?.predictions_with_outcomes || 0} with outcomes`}
          color="green"
        />
        <MetricCard
          title="Avg Response"
          value={
            statistics?.avg_response_time_ms
              ? `${statistics.avg_response_time_ms.toFixed(0)}ms`
              : 'N/A'
          }
          subtitle={
            statistics?.avg_response_time_ms
              ? statistics.avg_response_time_ms < 200
                ? `${(200 - statistics.avg_response_time_ms).toFixed(0)}ms under target`
                : `${(statistics.avg_response_time_ms - 200).toFixed(0)}ms over target`
              : 'Target: <200ms'
          }
          color="yellow"
        />
      </div>

      {/* First Row - Full Width Price Chart */}
      <div className="w-full">
        <RealtimePriceChart />
      </div>

      {/* Second Row - Accuracy Chart & Prediction Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <AccuracyChart data={chartData} />

        {/* Prediction Distribution */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Prediction Distribution</h3>
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={showBarChart}
                onChange={(e) => setShowBarChart(e.target.checked)}
                className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
              <span className="text-sm text-gray-600">Show Chart</span>
            </label>
          </div>

          {showBarChart ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={getBarChartData()}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="model" />
                <YAxis domain={[0, 100]} tickFormatter={(value) => `${value}%`} />
                <Tooltip formatter={(value: number) => `${value.toFixed(1)}%`} />
                <Legend />
                <Bar dataKey="UP Accuracy" fill="#10b981" />
                <Bar dataKey="DOWN Accuracy" fill="#ef4444" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="space-y-6">
              {/* VADER Distribution */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-600">VADER</span>
                  <span className="text-sm text-gray-500">
                    {vaderAccuracy?.total_predictions || 0} predictions
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-green-50 rounded-lg">
                    <p className="text-xs text-gray-600 mb-1">UP Accuracy</p>
                    <p className="text-2xl font-bold text-green-600">
                      {formatAccuracy(vaderAccuracy?.up_accuracy, vaderAccuracy?.up_predictions)}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {vaderAccuracy?.up_correct || 0} / {vaderAccuracy?.up_predictions || 0}
                    </p>
                  </div>
                  <div className="p-4 bg-red-50 rounded-lg">
                    <p className="text-xs text-gray-600 mb-1">DOWN Accuracy</p>
                    <p className="text-2xl font-bold text-red-600">
                      {formatAccuracy(vaderAccuracy?.down_accuracy, vaderAccuracy?.down_predictions)}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {vaderAccuracy?.down_correct || 0} / {vaderAccuracy?.down_predictions || 0}
                    </p>
                  </div>
                </div>
              </div>

              {/* FinBERT Distribution */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-600">FinBERT</span>
                  <span className="text-sm text-gray-500">
                    {finbertAccuracy?.total_predictions || 0} predictions
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-green-50 rounded-lg">
                    <p className="text-xs text-gray-600 mb-1">UP Accuracy</p>
                    <p className="text-2xl font-bold text-green-600">
                      {formatAccuracy(finbertAccuracy?.up_accuracy, finbertAccuracy?.up_predictions)}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {finbertAccuracy?.up_correct || 0} / {finbertAccuracy?.up_predictions || 0}
                    </p>
                  </div>
                  <div className="p-4 bg-red-50 rounded-lg">
                    <p className="text-xs text-gray-600 mb-1">DOWN Accuracy</p>
                    <p className="text-2xl font-bold text-red-600">
                      {formatAccuracy(
                        finbertAccuracy?.down_accuracy,
                        finbertAccuracy?.down_predictions
                      )}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {finbertAccuracy?.down_correct || 0} / {finbertAccuracy?.down_predictions || 0}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Predictions Table */}
      <PredictionTable />
    </div>
  );
}
