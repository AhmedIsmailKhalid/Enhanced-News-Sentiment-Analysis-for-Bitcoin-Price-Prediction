/**
 * API Client with Golden Dataset Fallback
 * Automatically falls back to sample data when backend is unavailable
 */
/* eslint-disable @typescript-eslint/no-explicit-any */

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
} from './golden-dataset';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

let isUsingGoldenDataset = false;

export function getIsUsingGoldenDataset(): boolean {
  return isUsingGoldenDataset;
}

async function apiCallWithFallback<T>(
  endpoint: string,
  fallbackData: T
): Promise<T> {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
      signal: AbortSignal.timeout(10000),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    isUsingGoldenDataset = false;
    return data;
  } catch (error) {
    console.warn(`API call failed for ${endpoint}, using golden dataset:`, error);
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

  async getSentimentTimeline(
    hours: number = 24,
    limit: number = 100
  ): Promise<SentimentResponse> {
    const sentimentData = getGoldenSentimentData();

    // Normalize golden data: map 'time' -> 'timestamp' to satisfy SentimentData type
    const normalizeItems = (items: { time?: string; timestamp?: string; score: number }[]) =>
      items.map(item => ({
        timestamp: item.timestamp ?? item.time ?? new Date().toISOString(),
        score: item.score,
      }));

    const vaderNorm = normalizeItems(sentimentData.vader);
    const finbertNorm = normalizeItems(sentimentData.finbert);

    const fallbackData: SentimentResponse = {
      success: true,
      vader: {
        data: vaderNorm,
        latest_score: vaderNorm[vaderNorm.length - 1].score,
      },
      finbert: {
        data: finbertNorm,
        latest_score: finbertNorm[finbertNorm.length - 1].score,
      },
    };

    return apiCallWithFallback(
      `/sentiment/timeline?hours=${hours}&limit=${limit}`,
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
    return apiCallWithFallback('/predictions/statistics', getGoldenStatistics());
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

  async makePrediction(feature_set: 'vader' | 'finbert'): Promise<DualPredictionResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ feature_set }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Prediction failed:', error);
      throw error;
    }
  }

  async makeDualPrediction(): Promise<DualPredictionResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/predict/both`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Dual prediction failed:', error);
      throw error;
    }
  }

  async getHealthCheck(): Promise<any> {
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

  async getConfidenceData(): Promise<any> {
    return apiCallWithFallback('/predictions/recent?limit=25', {
      predictions: getGoldenPredictions(),
      ...getGoldenConfidenceData(),
    });
  }

  async getHealth(): Promise<any> {
    const fallbackData = {
      status: 'healthy',
      loaded_models: 2,
      timestamp: new Date().toISOString(),
    };

    return apiCallWithFallback('/health', fallbackData);
  }

  async getDriftSummary(
    feature_set: 'vader' | 'finbert',
    model_type: string = 'random_forest',
    reference_days: number = 30,
    current_days: number = 7
  ): Promise<any> {
    const fallbackData = {
      success: true,
      summary: {
        feature_set,
        model_type,
        overall_severity: 'none',
        feature_drift: {
          status: 'no_data',
          message: 'Insufficient data for drift analysis',
        },
        model_drift: {
          status: 'no_data',
          message: 'Insufficient data for drift analysis',
        },
        recommendations: ['Collect more data for meaningful drift analysis'],
      },
    };

    return apiCallWithFallback(
      `/drift/summary?feature_set=${feature_set}&model_type=${model_type}&reference_days=${reference_days}&current_days=${current_days}`,
      fallbackData
    );
  }

  async getFeatureDrift(
    feature_set: 'vader' | 'finbert',
    reference_days: number = 7,
    current_days: number = 1
  ): Promise<any> {
    const fallbackData = {
      success: true,
      drift_analysis: {
        status: 'no_data',
        drift_severity: 'none',
        message: 'Insufficient data for feature drift analysis',
      },
    };

    return apiCallWithFallback(
      `/drift/features?feature_set=${feature_set}&reference_days=${reference_days}&current_days=${current_days}`,
      fallbackData
    );
  }

  async getModelDrift(
    feature_set: 'vader' | 'finbert',
    model_type: string = 'random_forest',
    reference_days: number = 7,
    current_days: number = 1
  ): Promise<any> {
    const fallbackData = {
      success: true,
      drift_analysis: {
        status: 'no_data',
        drift_severity: 'none',
        message: 'Insufficient data for model drift analysis',
      },
    };

    return apiCallWithFallback(
      `/drift/model?feature_set=${feature_set}&model_type=${model_type}&reference_days=${reference_days}&current_days=${current_days}`,
      fallbackData
    );
  }

  async getRetrainingStatus(): Promise<any> {
    const fallbackData = {
      success: true,
      status: {
        vader: {
          should_retrain: false,
          reasons: [],
          data_available: 0,
          data_required: 100,
        },
        finbert: {
          should_retrain: false,
          reasons: [],
          data_available: 0,
          data_required: 100,
        },
        thresholds: {
          accuracy_degradation: 0.1,
          drift_severity: 'high',
          min_samples: 100,
          min_predictions: 50,
        },
      },
    };

    return apiCallWithFallback('/retrain/status', fallbackData);
  }

  async checkRetrainingNeed(
    feature_set: 'vader' | 'finbert',
    model_type: string = 'random_forest'
  ): Promise<any> {
    const fallbackData = {
      success: true,
      should_retrain: false,
      reasons: [],
      data_available: 0,
      data_required: 100,
    };

    return apiCallWithFallback(
      `/retrain/check?feature_set=${feature_set}&model_type=${model_type}`,
      fallbackData
    );
  }

  async executeRetraining(
    feature_set: 'vader' | 'finbert',
    model_type: string = 'random_forest'
  ): Promise<any> {
    try {
      const response = await fetch(
        `${API_BASE_URL}/retrain/execute?feature_set=${feature_set}&model_type=${model_type}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Retraining execution failed:', error);
      throw error;
    }
  }

  async getDailyAccuracy(
    feature_set: 'vader' | 'finbert',
    model_type: string = 'random_forest',
    days: number = 30
  ): Promise<any> {
    const fallbackData = {
      success: true,
      feature_set,
      model_type,
      days,
      daily_accuracy: [],
    };

    return apiCallWithFallback(
      `/predictions/daily-accuracy?feature_set=${feature_set}&model_type=${model_type}&days=${days}`,
      fallbackData
    );
  }
}

export const apiClient = new APIClient();