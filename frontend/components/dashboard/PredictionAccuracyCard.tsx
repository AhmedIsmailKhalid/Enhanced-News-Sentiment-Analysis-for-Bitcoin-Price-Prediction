'use client';

import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { apiClient } from '@/lib/api';

export default function PredictionConfidenceCard() {
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
      // Get predictions with outcomes only
      const response = await apiClient.getRecentPredictions(undefined, 100);
      
      if (response.predictions && response.predictions.length > 0) {
        // Filter predictions with outcomes
        const predictionsWithOutcomes = response.predictions.filter(
          (p: any) => p.actual_direction !== null
        );
        
        if (predictionsWithOutcomes.length === 0) {
          setAccuracyData({ chartData: [], vaderAvg: null, finbertAvg: null });
          setLoading(false);
          return;
        }
        
        // Separate VADER and FinBERT predictions
        const vaderPreds = predictionsWithOutcomes
          .filter((p: any) => p.feature_set === 'vader')
          .reverse(); // Oldest first
        
        const finbertPreds = predictionsWithOutcomes
          .filter((p: any) => p.feature_set === 'finbert')
          .reverse();
        
        // Calculate rolling accuracy (window of 10 predictions)
        const vaderRollingAccuracy = calculateRollingAccuracy(vaderPreds, 10);
        const finbertRollingAccuracy = calculateRollingAccuracy(finbertPreds, 10);
        
        // Combine for chart
        const combinedData = combineAccuracyData(vaderRollingAccuracy, finbertRollingAccuracy);
        
        // Calculate overall accuracy
        const vaderAvg = vaderPreds.filter((p: any) => p.prediction_correct).length / vaderPreds.length;
        const finbertAvg = finbertPreds.filter((p: any) => p.prediction_correct).length / finbertPreds.length;
        
        setAccuracyData({
          chartData: combinedData,
          vaderAvg,
          finbertAvg,
          vaderCount: vaderPreds.length,
          finbertCount: finbertPreds.length
        });
      }
    } catch (error) {
      console.error('Failed to load accuracy data:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateRollingAccuracy = (predictions: any[], windowSize: number) => {
    if (predictions.length < windowSize) return [];
    
    const rolling = [];
    for (let i = windowSize - 1; i < predictions.length; i++) {
      const window = predictions.slice(i - windowSize + 1, i + 1);
      const correct = window.filter((p: any) => p.prediction_correct).length;
      const accuracy = correct / windowSize;
      
      rolling.push({
        index: i + 1,
        accuracy: accuracy * 100 // Convert to percentage
      });
    }
    
    return rolling;
  };

  const combineAccuracyData = (vaderData: any[], finbertData: any[]) => {
    const combined = [];
    const maxLength = Math.max(vaderData.length, finbertData.length);
    
    for (let i = 0; i < maxLength; i++) {
      const entry: any = { index: i + 1 };
      
      if (vaderData[i]) {
        entry.vader = vaderData[i].accuracy;
      }
      
      if (finbertData[i]) {
        entry.finbert = finbertData[i].accuracy;
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

  if (!accuracyData || accuracyData.chartData.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Model Accuracy (Rolling 10)</h3>
        <div className="flex items-center justify-center h-64 text-gray-500">
          <p>Need 10+ predictions with outcomes to show accuracy</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Model Accuracy (Rolling Window)</h3>
      
      {/* Overall Accuracy */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <p className="text-sm text-gray-600">VADER Overall</p>
          <p className="text-2xl font-bold text-cyan-600">
            {accuracyData.vaderAvg !== null 
              ? `${(accuracyData.vaderAvg * 100).toFixed(1)}%`
              : 'N/A'}
          </p>
          <p className="text-xs text-gray-500">
            {accuracyData.vaderCount} predictions with outcomes
          </p>
        </div>
        <div>
          <p className="text-sm text-gray-600">FinBERT Overall</p>
          <p className="text-2xl font-bold text-rose-600">
            {accuracyData.finbertAvg !== null 
              ? `${(accuracyData.finbertAvg * 100).toFixed(1)}%`
              : 'N/A'}
          </p>
          <p className="text-xs text-gray-500">
            {accuracyData.finbertCount} predictions with outcomes
          </p>
        </div>
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={accuracyData.chartData}>
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
            name="VADER Accuracy"
            dot={{ r: 3 }}
            connectNulls
          />
          <Line 
            type="monotone" 
            dataKey="finbert" 
            stroke="#f43f5e" 
            strokeWidth={2}
            name="FinBERT Accuracy"
            dot={{ r: 3 }}
            connectNulls
          />
        </LineChart>
      </ResponsiveContainer>
      
      <p className="text-xs text-gray-500 mt-2 text-center">
        Rolling accuracy calculated over 10-prediction windows
      </p>
    </div>
  );
}