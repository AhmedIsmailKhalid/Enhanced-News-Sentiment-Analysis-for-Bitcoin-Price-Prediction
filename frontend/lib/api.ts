/**
 * API Client with Golden Dataset Fallback
 * Automatically falls back to sample data when backend is unavailable
 */

import type {
  PriceResponse,
  SentimentResponse,
  PredictionsResponse,
  StatisticsResponse,
  DualPredictionResponse,
  AccuracyStats,
} from './types';

import {
  getGoldenPriceData,
  getGoldenSentimentData,
  getGoldenPredictions,
  getGoldenStatistics,
  getGoldenAccuracyData,
  getGoldenConfidenceData,
  shouldUseGoldenDataset,
} from './golden-dataset';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Track if we're using golden dataset globally
let isUsingGoldenDataset = false;

export function getIsUsingGoldenDataset(): boolean {
  return isUsingGoldenDataset;
}

// Helper function to make API calls with fallback
async function apiCallWithFallback<T>(
  endpoint: string,
  fallbackData: T
): Promise<T> {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      // Add timeout
      signal: AbortSignal.timeout(10000), // 10 second timeout
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    
    // API succeeded, we're using live data
    isUsingGoldenDataset = false;
    return data;
    
  } catch (error) {
    console.warn(`API call failed for ${endpoint}, using golden dataset:`, error);
    
    // Use golden dataset as fallback
    isUsingGoldenDataset = true;
    return fallbackData;
  }
}

class APIClient {
  async getRecentPrices(
    symbol: string = 'BTC',
    hours: number = 24,
    limit: number = 200
  ): Promise<PriceResponse> {
    const fallbackData: PriceResponse = {
      success: true,
      symbol,
      count: 96,
      latest_price: 95533,
      latest_timestamp: new Date().toISOString(),
      data: getGoldenPriceData(),
    };

    return apiCallWithFallback(
      `/price/recent?symbol=${symbol}&hours=${hours}&limit=${limit}`,
      fallbackData
    );
  }

  async getSentimentTimeline(hours: number = 24): Promise<SentimentResponse> {
    const sentimentData = getGoldenSentimentData();
    
    const fallbackData: SentimentResponse = {
      success: true,
      vader: {
        data: sentimentData.vader,
        latest_score: sentimentData.vader[sentimentData.vader.length - 1].score,
      },
      finbert: {
        data: sentimentData.finbert,
        latest_score: sentimentData.finbert[sentimentData.finbert.length - 1].score,
      },
    };

    return apiCallWithFallback(
      `/sentiment/timeline?hours=${hours}`,
      fallbackData
    );
  }

  async getRecentPredictions(
    feature_set?: string,
    limit: number = 10
  ): Promise<PredictionsResponse> {
    const allPredictions = getGoldenPredictions();
    const filteredPredictions = feature_set
      ? allPredictions.filter(p => p.feature_set === feature_set)
      : allPredictions;

    const fallbackData: PredictionsResponse = {
      predictions: filteredPredictions.slice(0, limit),
      total: filteredPredictions.length,
    };

    const url = feature_set
      ? `/predictions/recent?feature_set=${feature_set}&limit=${limit}`
      : `/predictions/recent?limit=${limit}`;

    return apiCallWithFallback(url, fallbackData);
  }

  async getStatistics(): Promise<StatisticsResponse> {
    const fallbackData = getGoldenStatistics();

    return apiCallWithFallback('/predictions/statistics', fallbackData);
  }

  async getModelAccuracy(
    feature_set: 'vader' | 'finbert',
    model_type: string = 'random_forest',
    days: number = 7
  ): Promise<{ success: boolean; accuracy_stats: AccuracyStats }> {
    const fallbackData = {
      success: true,
      accuracy_stats: getGoldenAccuracyData(feature_set),
    };

    return apiCallWithFallback(
      `/predictions/accuracy?feature_set=${feature_set}&model_type=${model_type}&days=${days}`,
      fallbackData
    );
  }

  async makePrediction(
    feature_set: 'vader' | 'finbert'
  ): Promise<DualPredictionResponse> {
    // Predictions cannot use golden dataset (requires live data)
    // Just let it fail gracefully
    try {
      const response = await fetch(`${API_BASE_URL}/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ feature_set }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Prediction failed:', error);
      throw error; // Don't use fallback for predictions
    }
  }

  async makeDualPrediction(): Promise<DualPredictionResponse> {
    // Predictions cannot use golden dataset (requires live data)
    try {
      const response = await fetch(`${API_BASE_URL}/predict/both`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Dual prediction failed:', error);
      throw error; // Don't use fallback for predictions
    }
  }

  async getHealthCheck(): Promise<any> {
    // Health check doesn't get fallback
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }

  // New method to get confidence data with fallback
  async getConfidenceData(): Promise<any> {
    const fallbackData = getGoldenConfidenceData();

    return apiCallWithFallback('/predictions/recent?limit=25', {
      predictions: getGoldenPredictions(),
      ...fallbackData,
    });
  }
}

export const apiClient = new APIClient();