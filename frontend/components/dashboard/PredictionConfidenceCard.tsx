'use client';

import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { apiClient } from '@/lib/api';

export default function PredictionConfidenceCard() {
  const [confidenceData, setConfidenceData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadConfidenceData();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadConfidenceData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadConfidenceData = async () => {
    try {
      const response = await apiClient.getRecentPredictions(undefined, 50);
      
      if (response.predictions && response.predictions.length > 0) {
        // Separate VADER and FinBERT predictions
        const vaderPreds = response.predictions
          .filter((p: any) => p.feature_set === 'vader')
          .reverse(); // Oldest first
        
        const finbertPreds = response.predictions
          .filter((p: any) => p.feature_set === 'finbert')
          .reverse();
        
        // Combine for chart
        const combinedData = combineConfidenceData(vaderPreds, finbertPreds);
        
        // Calculate averages
        const vaderAvg = vaderPreds.reduce((sum: number, p: any) => sum + p.confidence, 0) / vaderPreds.length;
        const finbertAvg = finbertPreds.reduce((sum: number, p: any) => sum + p.confidence, 0) / finbertPreds.length;
        
        setConfidenceData({
          chartData: combinedData,
          vaderAvg,
          finbertAvg,
        });
      }
    } catch (error) {
      console.error('Failed to load confidence data:', error);
    } finally {
      setLoading(false);
    }
  };

  const combineConfidenceData = (vaderPreds: any[], finbertPreds: any[]) => {
    const combined = [];
    const maxLength = Math.max(vaderPreds.length, finbertPreds.length);
    
    for (let i = 0; i < maxLength; i++) {
      const entry: any = { index: i + 1 };
      
      if (vaderPreds[i]) {
        entry.vader = (vaderPreds[i].confidence * 100);
      }
      
      if (finbertPreds[i]) {
        entry.finbert = (finbertPreds[i].confidence * 100);
      }
      
      combined.push(entry);
    }
    
    return combined;
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

  if (!confidenceData || confidenceData.chartData.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Prediction Confidence</h3>
        <div className="flex items-center justify-center h-64 text-gray-500">
          <p>No prediction data available yet</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Prediction Confidence (Recent)</h3>
      
      {/* Average Confidence */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <p className="text-sm text-gray-600">VADER Avg</p>
          <p className="text-2xl font-bold text-cyan-600">
            {(confidenceData.vaderAvg * 100).toFixed(1)}%
          </p>
          <p className="text-xs text-gray-500">Last {confidenceData.chartData.filter((d: any) => d.vader).length} predictions</p>
        </div>
        <div>
          <p className="text-sm text-gray-600">FinBERT Avg</p>
          <p className="text-2xl font-bold text-rose-600">
            {(confidenceData.finbertAvg * 100).toFixed(1)}%
          </p>
          <p className="text-xs text-gray-500">Last {confidenceData.chartData.filter((d: any) => d.finbert).length} predictions</p>
        </div>
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={confidenceData.chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis 
            dataKey="index" 
            stroke="#6b7280"
            style={{ fontSize: '12px' }}
            label={{ value: 'Prediction #', position: 'insideBottom', offset: -5 }}
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
            dot={{ r: 3 }}
            connectNulls
          />
          <Line 
            type="monotone" 
            dataKey="finbert" 
            stroke="#f43f5e" 
            strokeWidth={2}
            name="FinBERT"
            dot={{ r: 3 }}
            connectNulls
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}