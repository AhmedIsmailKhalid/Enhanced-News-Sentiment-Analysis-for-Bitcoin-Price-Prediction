// API Response Types
export interface PredictionResponse {
    success: boolean;
    prediction: {
      direction: 'up' | 'down';
      direction_numeric: number;
      probability: {
        down: number;
        up: number;
      };
      confidence: number;
    };
    model_info: {
      feature_set: string;
      model_type: string;
      model_version: string;
      features_used: number;
    };
    performance: {
      response_time_ms: number;
      cached_features: boolean;
    };
    prediction_id?: number;
    timestamp: string;
  }
  
  export interface DualPredictionResponse {
    vader: PredictionResponse;
    finbert: PredictionResponse;
    agreement: boolean;
    performance: {
      total_response_time_ms: number;
    };
  }
  
  export interface PredictionLog {
    id: number;
    feature_set: string;
    model_type: string;
    model_version: string;
    prediction: number;
    probability_down: number;
    probability_up: number;
    confidence: number;
    actual_direction: number | null;
    prediction_correct: boolean | null;
    bitcoin_price_at_prediction: number | null;
    bitcoin_price_1h_later: number | null;
    price_change_pct: number | null;
    response_time_ms: number;
    predicted_at: string;
    outcome_recorded_at: string | null;
  }
  
  export interface AccuracyStats {
    feature_set: string;
    model_type: string;
    period_days: number;
    total_predictions: number;
    correct_predictions: number;
    incorrect_predictions: number;
    accuracy: number;
    up_predictions: number;
    up_correct: number;
    up_accuracy: number;
    down_predictions: number;
    down_correct: number;
    down_accuracy: number;
    avg_confidence: number;
    avg_confidence_when_correct: number;
    avg_confidence_when_incorrect: number;
  }
  
  export interface Statistics {
    total_predictions: number;
    predictions_with_outcomes: number;
    correct_predictions: number;
    overall_accuracy: number | null;
    vader_predictions: number;
    finbert_predictions: number;
    avg_response_time_ms: number | null;
    pending_outcomes: number;
  }
  
  export interface DriftAnalysis {
    status: string;
    feature_set: string;
    drift_severity?: string;
    message?: string;
    features_tested?: number;
    significant_drift_count?: number;
    drift_results?: Array<{
      feature: string;
      ks_statistic: number;
      ks_pvalue: number;
      psi: number;
      drift_detected: boolean;
      reference_mean: number;
      current_mean: number;
    }>;
  }
  
  export interface ModelDrift {
    status: string;
    feature_set: string;
    model_type: string;
    drift_severity?: string;
    accuracy?: {
      reference: number;
      current: number;
      drop: number;
      drift_detected: boolean;
    };
    confidence?: {
      reference_avg: number;
      current_avg: number;
      reference_calibration_gap: number;
      current_calibration_gap: number;
      calibration_degradation: number;
    };
  }
  
  export interface RetrainingStatus {
    vader: {
      should_retrain: boolean;
      reasons: string[];
      data_available: number;
      data_required: number;
    };
    finbert: {
      should_retrain: boolean;
      reasons: string[];
      data_available: number;
      data_required: number;
    };
    thresholds: {
      accuracy_degradation: number;
      drift_severity: string;
      min_samples: number;
      min_predictions: number;
    };
  }
  
  export interface HealthStatus {
    status: string;
    timestamp: string;
    loaded_models: number;
  }