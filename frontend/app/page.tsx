'use client';

import { useState, useEffect } from 'react';
import RealtimePriceChart from '@/components/dashboard/RealtimePriceChart';
import SentimentScoreCard from '@/components/dashboard/SentimentScoreCard';
// import PredictionAccuracyCard from '@/components/dashboard/PredictionAccuracyCard';
import PredictionConfidenceCard from '@/components/dashboard/PredictionConfidenceCard';
import PredictionTable from '@/components/dashboard/PredictionTable';

export default function OverviewPage() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Bitcoin Sentiment MLOps</h1>
        <p className="mt-2 text-gray-600">
          Real-time sentiment analysis and price prediction monitoring
        </p>
      </div>

      {/* Top Row: Three Main Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <RealtimePriceChart />
        <SentimentScoreCard />
        {/* <PredictionAccuracyCard /> */}
        <PredictionConfidenceCard />
      </div>

      {/* Bottom Row: Recent Predictions Table */}
      <PredictionTable />
    </div>
  );
}