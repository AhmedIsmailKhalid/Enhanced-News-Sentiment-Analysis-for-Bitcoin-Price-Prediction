'use client';

import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { apiClient } from '@/lib/api';

export default function PredictionAccuracyCard() {
  const [accuracyData, setAccuracyData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAccuracyData();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadAccuracyData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadAccuracyData = async () => {
    try {
      const response = await apiClient.getPredictionAccuracyTimeline(24);
      
      if (response.success) {
        // Combine data for chart
        const combinedData = combineAccuracyData(
          response.vader_accuracy,
          response.finbert_accuracy
        );
        
        // Calculate latest accuracy
        const vaderLatest = response.vader_accuracy.length > 0 
          ? response.vader_accuracy[response.vader_accuracy.length - 1].accuracy 
          : null;
        const finbertLatest = response.finbert_accuracy.length > 0 
          ? response.finbert_accuracy[response.finbert_accuracy.length - 1].accuracy 
          : null;
        
        setAccuracyData({
          chartData: combinedData,
          vaderLatest,
          finbertLatest,
        });
      }
    } catch (error) {
      console.error('Failed to load accuracy data:', error);
    } finally {
      setLoading(false);
    }
  };

  const combineAccuracyData = (vaderData: any[], finbertData: any[]) => {
    const dataMap = new Map();
    
    vaderData.forEach(item => {
      const time = new Date(item.timestamp).toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
      });
      dataMap.set(item.timestamp, { time, vader: item.accuracy * 100 });
    });
    
    finbertData.forEach(item => {
      const time = new Date(item.timestamp).toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
      });
      const existing = dataMap.get(item.timestamp) || { time };
      dataMap.set(item.timestamp, { ...existing, finbert: item.accuracy * 100 });
    });
    
    return Array.from(dataMap.values());
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

  if (!accuracyData || accuracyData.chartData.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Prediction Accuracy</h3>
        <div className="flex items-center justify-center h-64 text-gray-500">
          <p>Not enough prediction data yet (need 10+ predictions with outcomes)</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Prediction Accuracy (24h)</h3>
      
      {/* Current Accuracy */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <p className="text-sm text-gray-600">VADER</p>
          <p className="text-2xl font-bold text-cyan-600">
            {accuracyData.vaderLatest 
              ? `${(accuracyData.vaderLatest * 100).toFixed(1)}%` 
              : 'N/A'}
          </p>
          <p className="text-xs text-gray-500">Rolling 10-prediction window</p>
        </div>
        <div>
          <p className="text-sm text-gray-600">FinBERT</p>
          <p className="text-2xl font-bold text-rose-600">
            {accuracyData.finbertLatest 
              ? `${(accuracyData.finbertLatest * 100).toFixed(1)}%` 
              : 'N/A'}
          </p>
          <p className="text-xs text-gray-500">Rolling 10-prediction window</p>
        </div>
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={accuracyData.chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis 
            dataKey="time" 
            stroke="#6b7280"
            style={{ fontSize: '12px' }}
          />
          <YAxis 
            stroke="#6b7280"
            style={{ fontSize: '12px' }}
            domain={[0, 100]}
            tickFormatter={(value) => `${value}%`}
          />
          <Tooltip 
            contentStyle={{
              backgroundColor: 'white',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
            }}
            formatter={(value: number) => [`${value.toFixed(1)}%`, '']}
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