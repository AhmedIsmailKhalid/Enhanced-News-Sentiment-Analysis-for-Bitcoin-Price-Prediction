const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class APIClient {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
  }

  // Health
  async getHealth() {
    return this.request<{ status: string; timestamp: string; loaded_models: number }>('/health');
  }

  // Price
  async getRecentPrices(
    symbol: string = 'BTC',
    hours: number = 24,
    limit: number = 100
  ): Promise<{
    success: boolean;
    symbol: string;
    count: number;
    latest_price: number | null;
    latest_timestamp: string | null;
    data: Array<{
      timestamp: string;
      price: number;
      volume_24h: number | null;
      change_24h: number | null;
    }>;
  }> {
    return this.request(`/price/recent?symbol=${symbol}&hours=${hours}&limit=${limit}`);
  }

  async getSentimentTimeline(
    hours: number = 24,
    limit: number = 100
  ): Promise<{
    success: boolean;
    hours: number;
    vader: {
      count: number;
      latest_score: number | null;
      data: Array<{ timestamp: string; score: number }>;
    };
    finbert: {
      count: number;
      latest_score: number | null;
      data: Array<{ timestamp: string; score: number }>;
    };
  }> {
    return this.request(`/sentiment/timeline?hours=${hours}&limit=${limit}`);
  }
  
  async getPredictionAccuracyTimeline(
    hours: number = 24
  ): Promise<{
    success: boolean;
    vader_accuracy: Array<{ timestamp: string; accuracy: number; window_size: number }>;
    finbert_accuracy: Array<{ timestamp: string; accuracy: number; window_size: number }>;
  }> {
    return this.request(`/predictions/accuracy-timeline?hours=${hours}`);
  }

  // Predictions
  async makePrediction(featureSet: 'vader' | 'finbert', modelType: string = 'random_forest') {
    return this.request<any>(`/predict?feature_set=${featureSet}&model_type=${modelType}`, {
      method: 'POST',
    });
  }

  async makeDualPrediction() {
    return this.request<any>('/predict/both', { method: 'POST' });
  }

  async getRecentPredictions(featureSet?: string, limit: number = 100) {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (featureSet) params.append('feature_set', featureSet);
    return this.request<any>(`/predictions/recent?${params}`);
  }

  async getModelAccuracy(featureSet: string, modelType: string, days: number = 7) {
    return this.request<any>(
      `/predictions/accuracy?feature_set=${featureSet}&model_type=${modelType}&days=${days}`
    );
  }

  async getDailyAccuracy(
    featureSet: string,
    modelType: string,
    days: number = 7
  ): Promise<{
    success: boolean;
    daily_accuracy: Array<{
      date: string;
      accuracy: number | null;
      predictions: number;
      correct: number;
    }>;
  }> {
    return this.request(
      `/predictions/daily-accuracy?feature_set=${featureSet}&model_type=${modelType}&days=${days}`
    );
  }

  async getStatistics() {
    return this.request<any>('/predictions/statistics');
  }

  // Drift Detection
  async getFeatureDrift(featureSet: string, referenceDays: number = 7, currentDays: number = 1) {
    return this.request<any>(
      `/drift/features?feature_set=${featureSet}&reference_days=${referenceDays}&current_days=${currentDays}`
    );
  }

  async getModelDrift(
    featureSet: string,
    modelType: string = 'random_forest',
    referenceDays: number = 7,
    currentDays: number = 1
  ) {
    return this.request<any>(
      `/drift/model?feature_set=${featureSet}&model_type=${modelType}&reference_days=${referenceDays}&current_days=${currentDays}`
    );
  }

  async getDriftSummary(featureSet: string, modelType: string = 'random_forest') {
    return this.request<any>(`/drift/summary?feature_set=${featureSet}&model_type=${modelType}`);
  }

  // Retraining
  async checkRetrainingNeed(featureSet: string, modelType: string = 'random_forest') {
    return this.request<any>(`/retrain/check?feature_set=${featureSet}&model_type=${modelType}`);
  }

  async executeRetraining(
    featureSet: string,
    modelType: string = 'random_forest',
    deployIfBetter: boolean = true
  ) {
    return this.request<any>(
      `/retrain/execute?feature_set=${featureSet}&model_type=${modelType}&deploy_if_better=${deployIfBetter}`,
      { method: 'POST' }
    );
  }

  async getRetrainingStatus() {
    return this.request<any>('/retrain/status');
  }
}

export const apiClient = new APIClient(API_BASE_URL);