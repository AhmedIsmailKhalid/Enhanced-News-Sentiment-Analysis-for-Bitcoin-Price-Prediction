'use client';

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface AccuracyChartProps {
  data?: Array<{
    date: string;
    vader?: number;
    finbert?: number;
  }>;
}

export default function AccuracyChart({ data }: AccuracyChartProps) {
  // Show message if no data available
  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Accuracy Over Time (7 Days)</h3>
        <div className="flex items-center justify-center h-64 text-gray-500">
          <p>No accuracy data available yet. Make predictions to see trends.</p>
        </div>
      </div>
    );
  }

  const chartData = data;

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Accuracy Over Time (7 Days)</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis domain={[0, 1]} tickFormatter={(value) => `${(value * 100).toFixed(0)}%`} />
          <Tooltip formatter={(value: number) => `${(value * 100).toFixed(1)}%`} />
          <Legend />
          <Line
            type="monotone"
            dataKey="vader"
            stroke="#06b6d4"
            strokeWidth={2}
            name="VADER"
            dot={{ fill: '#06b6d4' }}
            connectNulls={true}
          />
          <Line
            type="monotone"
            dataKey="finbert"
            stroke="#f43f5e"
            strokeWidth={2}
            name="FinBERT"
            dot={{ fill: '#f43f5e' }}
            connectNulls={true}
          />
        </LineChart>
      </ResponsiveContainer>
      <div className="mt-4 flex items-center justify-between text-sm">
        <div className="flex items-center space-x-4">
          <div className="flex items-center">
            <div className="w-3 h-3 bg-cyan-500 rounded-full mr-2"></div>
            <span className="text-gray-600">VADER</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-rose-500 rounded-full mr-2"></div>
            <span className="text-gray-600">FinBERT</span>
          </div>
        </div>
      </div>
    </div>
  );
}