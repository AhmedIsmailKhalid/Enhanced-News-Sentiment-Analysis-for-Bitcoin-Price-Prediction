/**
 * Type definitions for Bitcoin Sentiment MLOps Dashboard
 * Updated to match actual backend API response structure
 */

export interface PredictionLog {
  id: number;
  feature_set: 'vader' | 'finbert';
  model_type: string;
  model_version: string;
  prediction: number; // 0 or 1 (DOWN or UP)
  probability_down: number;
  probability_up: number;
  confidence: number; // NOT confidence_score
  features_json: Record<string, unknown>;
  feature_count: number;
  actual_direction: number | null; // NOT actual_outcome
  prediction_correct: boolean | null; // NOT is_correct
  bitcoin_price_at_prediction: number | null;
  bitcoin_price_1h_later: number | null;
  price_change_pct: number | null;
  response_time_ms: number | null;
  cached_features: boolean;
  predicted_at: string;
  outcome_recorded_at: string | null;
}

export interface AccuracyStats {
  total_predictions: number;
  predictions_with_outcomes: number;
  correct_predictions: number;
  overall_accuracy: number;
  accuracy_by_window?: Record<number, number>;
  by_model?: {
    [key: string]: {
      total: number;
      correct: number;
      accuracy: number;
    };
  };
}

export interface DriftMetrics {
  feature_drift?: {
    features: Array<{
      feature_name: string;
      drift_score: number;
      severity: 'none' | 'low' | 'medium' | 'high';
    }>;
    overall_drift: number;
  };
  model_drift?: {
    current_accuracy: number;
    baseline_accuracy: number;
    accuracy_drop: number;
    is_significant: boolean;
  };
}

export interface SystemHealth {
  status: 'healthy' | 'degraded' | 'down';
  timestamp: string;
  loaded_models: number;
  database_connected: boolean;
  uptime_seconds?: number;
  memory_usage?: number;
}

export interface PriceData {
  timestamp: string;
  price: number;
  volume_24h: number | null;
  change_24h: number | null;
}

export interface SentimentData {
  timestamp: string;
  score: number;
}

export interface SentimentResponse {
  success: boolean;
  vader: {
    data: SentimentData[];
    latest_score: number;
  };
  finbert: {
    data: SentimentData[];
    latest_score: number;
  };
}

export interface PriceResponse {
  success: boolean;
  symbol: string;
  count: number;
  latest_price: number;
  latest_timestamp: string;
  data: PriceData[];
}

export interface PredictionsResponse {
  predictions: PredictionLog[];
  total: number;
}

export interface StatisticsResponse {
  total_predictions: number;
  predictions_with_outcomes: number;
  vader_accuracy: number;
  finbert_accuracy: number;
  avg_response_time_ms: number;
}

export interface DualPredictionResponse {
  vader: {
    prediction: number;
    probabilities: {
      down: number;
      up: number;
    };
    confidence: number;
    model_type: string;
  };
  finbert: {
    prediction: number;
    probabilities: {
      down: number;
      up: number;
    };
    confidence: number;
    model_type: string;
  };
  agreement: boolean;
  response_time_ms: number;
  prediction_ids: {
    vader: number;
    finbert: number;
  };
}

export interface RetrainingStatus {
  feature_set: string;
  should_retrain: boolean;
  reasons: string[];
  data_available: number;
  data_required: number;
  current_accuracy?: number;
  drift_detected?: boolean;
}

export interface DriftSummaryResponse {
  feature_set: string;
  overall_drift_score: number;
  drift_severity: 'none' | 'low' | 'medium' | 'high';
  features_with_drift: Array<{
    feature_name: string;
    drift_score: number;
    severity: 'none' | 'low' | 'medium' | 'high';
  }>;
  recommendation: string;
}

export interface HealthCheckResponse {
  status: string;
  timestamp: string;
  loaded_models: number;
  database: {
    connected: boolean;
    active_database: string;
  };
  endpoints: {
    [key: string]: string;
  };
}

export interface DailyAccuracyResponse {
  feature_set: string;
  model_type: string;
  daily_accuracy: Array<{
    date: string;
    total_predictions: number;
    correct_predictions: number;
    accuracy: number;
  }>;
}