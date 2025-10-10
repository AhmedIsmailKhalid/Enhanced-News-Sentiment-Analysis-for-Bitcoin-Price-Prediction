'use client';

import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { apiClient } from '@/lib/api';

export default function SentimentScoreCard() {
  const [sentimentData, setSentimentData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSentimentData();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadSentimentData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadSentimentData = async () => {
    try {
      const response = await apiClient.getSentimentTimeline(24, 100);
      
      if (response.success) {
        // Combine data for chart
        const combinedData = combineTimelineData(
          response.vader.data,
          response.finbert.data
        );
        
        setSentimentData({
          chartData: combinedData,
          vaderLatest: response.vader.latest_score,
          finbertLatest: response.finbert.latest_score,
        });
      }
    } catch (error) {
      console.error('Failed to load sentiment data:', error);
    } finally {
      setLoading(false);
    }
  };

  const combineTimelineData = (vaderData: any[], finbertData: any[]) => {
    const dataMap = new Map();
    
    vaderData.forEach(item => {
      const time = new Date(item.timestamp).toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
      });
      dataMap.set(item.timestamp, { time, vader: item.score });
    });
    
    finbertData.forEach(item => {
      const time = new Date(item.timestamp).toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
      });
      const existing = dataMap.get(item.timestamp) || { time };
      dataMap.set(item.timestamp, { ...existing, finbert: item.score });
    });
    
    return Array.from(dataMap.values());
  };

  const getSentimentLabel = (score: number | null) => {
    if (score === null) return 'N/A';
    if (score > 0.2) return 'Bullish';
    if (score < -0.2) return 'Bearish';
    return 'Neutral';
  };

  const getSentimentColor = (score: number | null) => {
    if (score === null) return 'text-gray-500';
    if (score > 0.2) return 'text-green-600';
    if (score < -0.2) return 'text-red-600';
    return 'text-yellow-600';
  };

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

  if (!sentimentData || sentimentData.chartData.length === 0) {
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
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Sentiment Score (24h)</h3>
      
      {/* Current Scores */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <p className="text-sm text-gray-600">VADER</p>
          <p className="text-2xl font-bold text-cyan-600">
            {sentimentData.vaderLatest?.toFixed(2) || 'N/A'}
          </p>
          <p className={`text-sm font-medium ${getSentimentColor(sentimentData.vaderLatest)}`}>
            {getSentimentLabel(sentimentData.vaderLatest)}
          </p>
        </div>
        <div>
          <p className="text-sm text-gray-600">FinBERT</p>
          <p className="text-2xl font-bold text-rose-600">
            {sentimentData.finbertLatest?.toFixed(2) || 'N/A'}
          </p>
          <p className={`text-sm font-medium ${getSentimentColor(sentimentData.finbertLatest)}`}>
            {getSentimentLabel(sentimentData.finbertLatest)}
          </p>
        </div>
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={sentimentData.chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis 
            dataKey="time" 
            stroke="#6b7280"
            style={{ fontSize: '12px' }}
          />
          <YAxis 
            stroke="#6b7280"
            style={{ fontSize: '12px' }}
            domain={[-1, 1]}
            ticks={[-1, -0.5, 0, 0.5, 1]}
          />
          <Tooltip 
            contentStyle={{
              backgroundColor: 'white',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
            }}
          />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="vader" 
            stroke="#06b6d4" 
            strokeWidth={2}
            name="VADER"
            dot={false}
          />
          <Line 
            type="monotone" 
            dataKey="finbert" 
            stroke="#f43f5e" 
            strokeWidth={2}
            name="FinBERT"
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}