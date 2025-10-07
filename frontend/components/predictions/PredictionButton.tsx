'use client';

import { useState } from 'react';

interface PredictionButtonProps {
  onPredict: () => Promise<void>;
  loading: boolean;
}

export default function PredictionButton({ onPredict, loading }: PredictionButtonProps) {
  return (
    <div className="flex justify-center">
      <button
        onClick={onPredict}
        disabled={loading}
        className={`
          px-8 py-4 text-lg font-semibold rounded-lg shadow-lg transition-all
          ${
            loading
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700 text-white hover:shadow-xl'
          }
        `}
      >
        {loading ? (
          <span className="flex items-center space-x-2">
            <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
                fill="none"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            <span>Getting Prediction...</span>
          </span>
        ) : (
          'Get Bitcoin Sentiment Prediction'
        )}
      </button>
    </div>
  );
}