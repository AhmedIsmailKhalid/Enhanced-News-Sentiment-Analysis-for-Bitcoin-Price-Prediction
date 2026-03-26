/**
 * Golden Dataset - Static sample data with dynamic noise for demo mode
 * Used as fallback when backend is unavailable
 */
/* eslint-disable @typescript-eslint/no-unused-vars */
/* eslint-disable @typescript-eslint/no-explicit-any */

import type { 
  PriceData, 
  SentimentData, 
  PredictionLog,
  StatisticsResponse,
  AccuracyStats 
} from './types';

// ============================================================================
// NOISE FUNCTIONS - Add realistic variation
// ============================================================================

function addPriceNoise(price: number, variance: number = 0.008): number {
  // ±0.8% variation (realistic for 15-min intervals)
  return Math.round(price * (1 + (Math.random() - 0.5) * variance));
}

function addSentimentNoise(score: number, variance: number = 0.05): number {
  // ±0.05 variation, clamped to [-1, 1]
  const noisy = score + (Math.random() - 0.5) * variance;
  return Math.max(-1, Math.min(1, noisy));
}

function addPercentageNoise(value: number, variance: number = 0.01): number {
  // ±1% variation for accuracy percentages
  return value * (1 + (Math.random() - 0.5) * variance);
}

function addTimeNoise(ms: number, variance: number = 0.1): number {
  // ±10% variation for response times
  return Math.round(ms * (1 + (Math.random() - 0.5) * variance));
}

// ============================================================================
// BASE PRICE DATA - Last 24 hours (96 points, every 15 min)
// ============================================================================

const BASE_PRICE_DATA: Array<{ timestamp: string; price: number }> = [
  // Start at midnight, trend upward with realistic volatility
  { timestamp: "2026-01-15T00:00:00Z", price: 94230 },
  { timestamp: "2026-01-15T00:15:00Z", price: 94350 },
  { timestamp: "2026-01-15T00:30:00Z", price: 94180 },
  { timestamp: "2026-01-15T00:45:00Z", price: 94420 },
  { timestamp: "2026-01-15T01:00:00Z", price: 94550 },
  { timestamp: "2026-01-15T01:15:00Z", price: 94480 },
  { timestamp: "2026-01-15T01:30:00Z", price: 94620 },
  { timestamp: "2026-01-15T01:45:00Z", price: 94590 },
  { timestamp: "2026-01-15T02:00:00Z", price: 94750 },
  { timestamp: "2026-01-15T02:15:00Z", price: 94680 },
  { timestamp: "2026-01-15T02:30:00Z", price: 94820 },
  { timestamp: "2026-01-15T02:45:00Z", price: 94900 },
  { timestamp: "2026-01-15T03:00:00Z", price: 95050 },
  { timestamp: "2026-01-15T03:15:00Z", price: 94980 },
  { timestamp: "2026-01-15T03:30:00Z", price: 95120 },
  { timestamp: "2026-01-15T03:45:00Z", price: 95080 },
  { timestamp: "2026-01-15T04:00:00Z", price: 95200 },
  { timestamp: "2026-01-15T04:15:00Z", price: 95350 },
  { timestamp: "2026-01-15T04:30:00Z", price: 95280 },
  { timestamp: "2026-01-15T04:45:00Z", price: 95420 },
  { timestamp: "2026-01-15T05:00:00Z", price: 95550 },
  { timestamp: "2026-01-15T05:15:00Z", price: 95480 },
  { timestamp: "2026-01-15T05:30:00Z", price: 95620 },
  { timestamp: "2026-01-15T05:45:00Z", price: 95700 },
  { timestamp: "2026-01-15T06:00:00Z", price: 95850 },
  { timestamp: "2026-01-15T06:15:00Z", price: 95780 },
  { timestamp: "2026-01-15T06:30:00Z", price: 95920 },
  { timestamp: "2026-01-15T06:45:00Z", price: 96050 },
  { timestamp: "2026-01-15T07:00:00Z", price: 96200 },
  { timestamp: "2026-01-15T07:15:00Z", price: 96150 },
  { timestamp: "2026-01-15T07:30:00Z", price: 96280 },
  { timestamp: "2026-01-15T07:45:00Z", price: 96220 },
  { timestamp: "2026-01-15T08:00:00Z", price: 96350 },
  { timestamp: "2026-01-15T08:15:00Z", price: 96480 },
  { timestamp: "2026-01-15T08:30:00Z", price: 96420 },
  { timestamp: "2026-01-15T08:45:00Z", price: 96550 },
  { timestamp: "2026-01-15T09:00:00Z", price: 96480 },
  { timestamp: "2026-01-15T09:15:00Z", price: 96380 },
  { timestamp: "2026-01-15T09:30:00Z", price: 96250 },
  { timestamp: "2026-01-15T09:45:00Z", price: 96180 },
  { timestamp: "2026-01-15T10:00:00Z", price: 96050 },
  { timestamp: "2026-01-15T10:15:00Z", price: 95950 },
  { timestamp: "2026-01-15T10:30:00Z", price: 95880 },
  { timestamp: "2026-01-15T10:45:00Z", price: 95750 },
  { timestamp: "2026-01-15T11:00:00Z", price: 95680 },
  { timestamp: "2026-01-15T11:15:00Z", price: 95550 },
  { timestamp: "2026-01-15T11:30:00Z", price: 95620 },
  { timestamp: "2026-01-15T11:45:00Z", price: 95750 },
  { timestamp: "2026-01-15T12:00:00Z", price: 95850 },
  { timestamp: "2026-01-15T12:15:00Z", price: 95920 },
  { timestamp: "2026-01-15T12:30:00Z", price: 96050 },
  { timestamp: "2026-01-15T12:45:00Z", price: 96120 },
  { timestamp: "2026-01-15T13:00:00Z", price: 96250 },
  { timestamp: "2026-01-15T13:15:00Z", price: 96180 },
  { timestamp: "2026-01-15T13:30:00Z", price: 96320 },
  { timestamp: "2026-01-15T13:45:00Z", price: 96280 },
  { timestamp: "2026-01-15T14:00:00Z", price: 96150 },
  { timestamp: "2026-01-15T14:15:00Z", price: 96080 },
  { timestamp: "2026-01-15T14:30:00Z", price: 95950 },
  { timestamp: "2026-01-15T14:45:00Z", price: 95880 },
  { timestamp: "2026-01-15T15:00:00Z", price: 95750 },
  { timestamp: "2026-01-15T15:15:00Z", price: 95680 },
  { timestamp: "2026-01-15T15:30:00Z", price: 95550 },
  { timestamp: "2026-01-15T15:45:00Z", price: 95480 },
  { timestamp: "2026-01-15T16:00:00Z", price: 95350 },
  { timestamp: "2026-01-15T16:15:00Z", price: 95280 },
  { timestamp: "2026-01-15T16:30:00Z", price: 95150 },
  { timestamp: "2026-01-15T16:45:00Z", price: 95080 },
  { timestamp: "2026-01-15T17:00:00Z", price: 94950 },
  { timestamp: "2026-01-15T17:15:00Z", price: 94880 },
  { timestamp: "2026-01-15T17:30:00Z", price: 94750 },
  { timestamp: "2026-01-15T17:45:00Z", price: 94820 },
  { timestamp: "2026-01-15T18:00:00Z", price: 94950 },
  { timestamp: "2026-01-15T18:15:00Z", price: 95050 },
  { timestamp: "2026-01-15T18:30:00Z", price: 95180 },
  { timestamp: "2026-01-15T18:45:00Z", price: 95250 },
  { timestamp: "2026-01-15T19:00:00Z", price: 95380 },
  { timestamp: "2026-01-15T19:15:00Z", price: 95450 },
  { timestamp: "2026-01-15T19:30:00Z", price: 95580 },
  { timestamp: "2026-01-15T19:45:00Z", price: 95650 },
  { timestamp: "2026-01-15T20:00:00Z", price: 95780 },
  { timestamp: "2026-01-15T20:15:00Z", price: 95850 },
  { timestamp: "2026-01-15T20:30:00Z", price: 95920 },
  { timestamp: "2026-01-15T20:45:00Z", price: 95850 },
  { timestamp: "2026-01-15T21:00:00Z", price: 95750 },
  { timestamp: "2026-01-15T21:15:00Z", price: 95680 },
  { timestamp: "2026-01-15T21:30:00Z", price: 95550 },
  { timestamp: "2026-01-15T21:45:00Z", price: 95480 },
  { timestamp: "2026-01-15T22:00:00Z", price: 95350 },
  { timestamp: "2026-01-15T22:15:00Z", price: 95420 },
  { timestamp: "2026-01-15T22:30:00Z", price: 95550 },
  { timestamp: "2026-01-15T22:45:00Z", price: 95480 },
  { timestamp: "2026-01-15T23:00:00Z", price: 95350 },
  { timestamp: "2026-01-15T23:15:00Z", price: 95280 },
  { timestamp: "2026-01-15T23:30:00Z", price: 95420 },
  { timestamp: "2026-01-15T23:45:00Z", price: 95533 },
];

// ============================================================================
// BASE SENTIMENT DATA - Last 24 hours (48 points, every 30 min)
// ============================================================================

const BASE_SENTIMENT_DATA = {
  vader: [
    { time: "2026-01-15T00:00:00Z", score: 0.05 },
    { time: "2026-01-15T00:30:00Z", score: 0.12 },
    { time: "2026-01-15T01:00:00Z", score: 0.08 },
    { time: "2026-01-15T01:30:00Z", score: 0.15 },
    { time: "2026-01-15T02:00:00Z", score: 0.22 },
    { time: "2026-01-15T02:30:00Z", score: 0.18 },
    { time: "2026-01-15T03:00:00Z", score: 0.25 },
    { time: "2026-01-15T03:30:00Z", score: 0.20 },
    { time: "2026-01-15T04:00:00Z", score: 0.28 },
    { time: "2026-01-15T04:30:00Z", score: 0.32 },
    { time: "2026-01-15T05:00:00Z", score: 0.35 },
    { time: "2026-01-15T05:30:00Z", score: 0.30 },
    { time: "2026-01-15T06:00:00Z", score: 0.38 },
    { time: "2026-01-15T06:30:00Z", score: 0.40 },
    { time: "2026-01-15T07:00:00Z", score: 0.35 },
    { time: "2026-01-15T07:30:00Z", score: 0.32 },
    { time: "2026-01-15T08:00:00Z", score: 0.28 },
    { time: "2026-01-15T08:30:00Z", score: 0.25 },
    { time: "2026-01-15T09:00:00Z", score: 0.18 },
    { time: "2026-01-15T09:30:00Z", score: 0.12 },
    { time: "2026-01-15T10:00:00Z", score: 0.05 },
    { time: "2026-01-15T10:30:00Z", score: -0.02 },
    { time: "2026-01-15T11:00:00Z", score: -0.08 },
    { time: "2026-01-15T11:30:00Z", score: -0.05 },
    { time: "2026-01-15T12:00:00Z", score: 0.02 },
    { time: "2026-01-15T12:30:00Z", score: 0.08 },
    { time: "2026-01-15T13:00:00Z", score: 0.15 },
    { time: "2026-01-15T13:30:00Z", score: 0.12 },
    { time: "2026-01-15T14:00:00Z", score: 0.05 },
    { time: "2026-01-15T14:30:00Z", score: -0.02 },
    { time: "2026-01-15T15:00:00Z", score: -0.10 },
    { time: "2026-01-15T15:30:00Z", score: -0.15 },
    { time: "2026-01-15T16:00:00Z", score: -0.20 },
    { time: "2026-01-15T16:30:00Z", score: -0.18 },
    { time: "2026-01-15T17:00:00Z", score: -0.12 },
    { time: "2026-01-15T17:30:00Z", score: -0.08 },
    { time: "2026-01-15T18:00:00Z", score: -0.02 },
    { time: "2026-01-15T18:30:00Z", score: 0.05 },
    { time: "2026-01-15T19:00:00Z", score: 0.12 },
    { time: "2026-01-15T19:30:00Z", score: 0.18 },
    { time: "2026-01-15T20:00:00Z", score: 0.22 },
    { time: "2026-01-15T20:30:00Z", score: 0.18 },
    { time: "2026-01-15T21:00:00Z", score: 0.12 },
    { time: "2026-01-15T21:30:00Z", score: 0.08 },
    { time: "2026-01-15T22:00:00Z", score: 0.02 },
    { time: "2026-01-15T22:30:00Z", score: 0.05 },
    { time: "2026-01-15T23:00:00Z", score: 0.08 },
    { time: "2026-01-15T23:30:00Z", score: 0.00 },
  ],
  finbert: [
    { time: "2026-01-15T00:00:00Z", score: 0.08 },
    { time: "2026-01-15T00:30:00Z", score: 0.15 },
    { time: "2026-01-15T01:00:00Z", score: 0.12 },
    { time: "2026-01-15T01:30:00Z", score: 0.18 },
    { time: "2026-01-15T02:00:00Z", score: 0.25 },
    { time: "2026-01-15T02:30:00Z", score: 0.22 },
    { time: "2026-01-15T03:00:00Z", score: 0.28 },
    { time: "2026-01-15T03:30:00Z", score: 0.25 },
    { time: "2026-01-15T04:00:00Z", score: 0.32 },
    { time: "2026-01-15T04:30:00Z", score: 0.38 },
    { time: "2026-01-15T05:00:00Z", score: 0.42 },
    { time: "2026-01-15T05:30:00Z", score: 0.38 },
    { time: "2026-01-15T06:00:00Z", score: 0.45 },
    { time: "2026-01-15T06:30:00Z", score: 0.48 },
    { time: "2026-01-15T07:00:00Z", score: 0.42 },
    { time: "2026-01-15T07:30:00Z", score: 0.38 },
    { time: "2026-01-15T08:00:00Z", score: 0.32 },
    { time: "2026-01-15T08:30:00Z", score: 0.28 },
    { time: "2026-01-15T09:00:00Z", score: 0.22 },
    { time: "2026-01-15T09:30:00Z", score: 0.15 },
    { time: "2026-01-15T10:00:00Z", score: 0.08 },
    { time: "2026-01-15T10:30:00Z", score: 0.02 },
    { time: "2026-01-15T11:00:00Z", score: -0.05 },
    { time: "2026-01-15T11:30:00Z", score: -0.02 },
    { time: "2026-01-15T12:00:00Z", score: 0.05 },
    { time: "2026-01-15T12:30:00Z", score: 0.12 },
    { time: "2026-01-15T13:00:00Z", score: 0.18 },
    { time: "2026-01-15T13:30:00Z", score: 0.15 },
    { time: "2026-01-15T14:00:00Z", score: 0.08 },
    { time: "2026-01-15T14:30:00Z", score: 0.02 },
    { time: "2026-01-15T15:00:00Z", score: -0.08 },
    { time: "2026-01-15T15:30:00Z", score: -0.12 },
    { time: "2026-01-15T16:00:00Z", score: -0.18 },
    { time: "2026-01-15T16:30:00Z", score: -0.15 },
    { time: "2026-01-15T17:00:00Z", score: -0.10 },
    { time: "2026-01-15T17:30:00Z", score: -0.05 },
    { time: "2026-01-15T18:00:00Z", score: 0.02 },
    { time: "2026-01-15T18:30:00Z", score: 0.08 },
    { time: "2026-01-15T19:00:00Z", score: 0.15 },
    { time: "2026-01-15T19:30:00Z", score: 0.22 },
    { time: "2026-01-15T20:00:00Z", score: 0.25 },
    { time: "2026-01-15T20:30:00Z", score: 0.22 },
    { time: "2026-01-15T21:00:00Z", score: 0.15 },
    { time: "2026-01-15T21:30:00Z", score: 0.10 },
    { time: "2026-01-15T22:00:00Z", score: 0.05 },
    { time: "2026-01-15T22:30:00Z", score: 0.08 },
    { time: "2026-01-15T23:00:00Z", score: 0.12 },
    { time: "2026-01-15T23:30:00Z", score: 0.02 },
  ]
};

// ============================================================================
// BASE PREDICTIONS - Last 25 predictions
// ============================================================================

const BASE_PREDICTIONS: Partial<PredictionLog>[] = [
  { id: 2501, feature_set: 'finbert', model_type: 'random_forest', prediction: 0, confidence: 0.989, predicted_at: '2026-01-15T23:45:00Z', prediction_correct: null, actual_direction: null },
  { id: 2500, feature_set: 'vader', model_type: 'random_forest', prediction: 0, confidence: 0.679, predicted_at: '2026-01-15T23:45:00Z', prediction_correct: null, actual_direction: null },
  { id: 2499, feature_set: 'finbert', model_type: 'random_forest', prediction: 0, confidence: 0.991, predicted_at: '2026-01-15T23:30:00Z', prediction_correct: null, actual_direction: null },
  { id: 2498, feature_set: 'vader', model_type: 'random_forest', prediction: 0, confidence: 0.679, predicted_at: '2026-01-15T23:30:00Z', prediction_correct: null, actual_direction: null },
  { id: 2497, feature_set: 'finbert', model_type: 'random_forest', prediction: 0, confidence: 0.989, predicted_at: '2026-01-15T23:15:00Z', prediction_correct: true, actual_direction: 0 },
  { id: 2496, feature_set: 'vader', model_type: 'random_forest', prediction: 0, confidence: 0.679, predicted_at: '2026-01-15T23:15:00Z', prediction_correct: false, actual_direction: 1 },
  { id: 2495, feature_set: 'finbert', model_type: 'random_forest', prediction: 0, confidence: 0.991, predicted_at: '2026-01-15T23:00:00Z', prediction_correct: true, actual_direction: 0 },
  { id: 2494, feature_set: 'vader', model_type: 'random_forest', prediction: 0, confidence: 0.679, predicted_at: '2026-01-15T23:00:00Z', prediction_correct: false, actual_direction: 1 },
  { id: 2493, feature_set: 'finbert', model_type: 'random_forest', prediction: 1, confidence: 0.989, predicted_at: '2026-01-15T22:45:00Z', prediction_correct: true, actual_direction: 1 },
  { id: 2492, feature_set: 'vader', model_type: 'random_forest', prediction: 0, confidence: 0.679, predicted_at: '2026-01-15T22:45:00Z', prediction_correct: false, actual_direction: 1 },
  { id: 2491, feature_set: 'finbert', model_type: 'random_forest', prediction: 0, confidence: 0.991, predicted_at: '2026-01-15T22:30:00Z', prediction_correct: true, actual_direction: 0 },
  { id: 2490, feature_set: 'vader', model_type: 'random_forest', prediction: 1, confidence: 0.679, predicted_at: '2026-01-15T22:30:00Z', prediction_correct: false, actual_direction: 0 },
  { id: 2489, feature_set: 'finbert', model_type: 'random_forest', prediction: 0, confidence: 0.989, predicted_at: '2026-01-15T22:15:00Z', prediction_correct: true, actual_direction: 0 },
  { id: 2488, feature_set: 'vader', model_type: 'random_forest', prediction: 0, confidence: 0.679, predicted_at: '2026-01-15T22:15:00Z', prediction_correct: true, actual_direction: 0 },
  { id: 2487, feature_set: 'finbert', model_type: 'random_forest', prediction: 0, confidence: 0.991, predicted_at: '2026-01-15T22:00:00Z', prediction_correct: false, actual_direction: 1 },
  { id: 2486, feature_set: 'vader', model_type: 'random_forest', prediction: 0, confidence: 0.679, predicted_at: '2026-01-15T22:00:00Z', prediction_correct: false, actual_direction: 1 },
  { id: 2485, feature_set: 'finbert', model_type: 'random_forest', prediction: 1, confidence: 0.989, predicted_at: '2026-01-15T21:45:00Z', prediction_correct: false, actual_direction: 0 },
  { id: 2484, feature_set: 'vader', model_type: 'random_forest', prediction: 0, confidence: 0.679, predicted_at: '2026-01-15T21:45:00Z', prediction_correct: true, actual_direction: 0 },
  { id: 2483, feature_set: 'finbert', model_type: 'random_forest', prediction: 0, confidence: 0.991, predicted_at: '2026-01-15T21:30:00Z', prediction_correct: true, actual_direction: 0 },
  { id: 2482, feature_set: 'vader', model_type: 'random_forest', prediction: 1, confidence: 0.679, predicted_at: '2026-01-15T21:30:00Z', prediction_correct: false, actual_direction: 0 },
  { id: 2481, feature_set: 'finbert', model_type: 'random_forest', prediction: 0, confidence: 0.989, predicted_at: '2026-01-15T21:15:00Z', prediction_correct: true, actual_direction: 0 },
  { id: 2480, feature_set: 'vader', model_type: 'random_forest', prediction: 0, confidence: 0.679, predicted_at: '2026-01-15T21:15:00Z', prediction_correct: true, actual_direction: 0 },
  { id: 2479, feature_set: 'finbert', model_type: 'random_forest', prediction: 1, confidence: 0.991, predicted_at: '2026-01-15T21:00:00Z', prediction_correct: false, actual_direction: 0 },
  { id: 2478, feature_set: 'vader', model_type: 'random_forest', prediction: 0, confidence: 0.679, predicted_at: '2026-01-15T21:00:00Z', prediction_correct: true, actual_direction: 0 },
  { id: 2477, feature_set: 'finbert', model_type: 'random_forest', prediction: 1, confidence: 0.989, predicted_at: '2026-01-15T20:45:00Z', prediction_correct: false, actual_direction: 0 },
];

// ============================================================================
// EXPORTED FUNCTIONS - Return data with fresh noise
// ============================================================================

export function getGoldenPriceData(): PriceData[] {
  return BASE_PRICE_DATA.map(point => ({
    timestamp: point.timestamp,
    price: addPriceNoise(point.price),
    volume_24h: addPriceNoise(125000000000, 0.1), // ~$125B with ±10% variation
    change_24h: (Math.random() - 0.5) * 4, // ±2%
  }));
}

export function getGoldenSentimentData() {
  return {
    vader: BASE_SENTIMENT_DATA.vader.map(point => ({
      time: point.time,
      score: addSentimentNoise(point.score),
    })),
    finbert: BASE_SENTIMENT_DATA.finbert.map(point => ({
      time: point.time,
      score: addSentimentNoise(point.score),
    })),
  };
}

export function getGoldenPredictions(): PredictionLog[] {
  return BASE_PREDICTIONS.map(pred => ({
    ...pred,
    confidence: addPercentageNoise(pred.confidence || 0.7, 0.02),
  })) as PredictionLog[];
}

export function getGoldenStatistics(): StatisticsResponse {
  return {
    total_predictions: 2847,
    predictions_with_outcomes: 2450,
    correct_predictions: 1250,
    overall_accuracy: 0.51,
    vader_predictions: 1423,
    finbert_predictions: 1424,
    avg_response_time_ms: addTimeNoise(145, 0.15),
    pending_outcomes: 397,
  };
}

export function getGoldenAccuracyData(feature_set: 'vader' | 'finbert'): AccuracyStats {
  const baseAccuracy = feature_set === 'vader' ? 54.5 : 51.2;
  
  return {
    total_predictions: 2847,
    predictions_with_outcomes: 2450,
    correct_predictions: Math.round(2450 * (baseAccuracy / 100)),
    overall_accuracy: addPercentageNoise(baseAccuracy, 0.01) / 100,
    accuracy_by_window: {
      10: addPercentageNoise(feature_set === 'vader' ? 48 : 45, 0.02) / 100,
      20: addPercentageNoise(feature_set === 'vader' ? 52 : 48, 0.02) / 100,
      30: addPercentageNoise(feature_set === 'vader' ? 54 : 51, 0.02) / 100,
      40: addPercentageNoise(feature_set === 'vader' ? 55 : 52, 0.02) / 100,
      50: addPercentageNoise(feature_set === 'vader' ? 56 : 54, 0.02) / 100,
    },
  };
}

export function getGoldenConfidenceData() {
  // Generate 25 recent predictions with alternating models
  const predictions = [];
  const now = new Date();
  
  for (let i = 0; i < 25; i++) {
    const isVader = i % 2 === 0;
    const timestamp = new Date(now.getTime() - i * 15 * 60 * 1000); // Every 15 min
    
    predictions.push({
      index: 25 - i,
      vader: isVader ? addPercentageNoise(67.9, 0.02) : null,
      finbert: !isVader ? addPercentageNoise(99.1, 0.02) : null,
    });
  }
  
  return {
    chartData: predictions,
    vaderAvg: addPercentageNoise(67.9, 0.01),
    finbertAvg: addPercentageNoise(99.1, 0.01),
  };
}

// ============================================================================
// HELPER - Check if we should use golden dataset
// ============================================================================

export function shouldUseGoldenDataset(error: unknown): boolean {
  // Use golden dataset when:
  // 1. Network error (backend down)
  // 2. 500+ server errors
  // 3. Timeout errors
  
  if (!error) return false;
  
  // Type guard for Error objects
  const errorMessage = error instanceof Error 
    ? error.message.toLowerCase() 
    : String(error).toLowerCase();
  
  // Type guard for response objects (axios/fetch style)
  const statusCode = typeof error === 'object' && error !== null && 'response' in error
    ? (error as any).response?.status
    : undefined;
  
  return (
    errorMessage.includes('network') ||
    errorMessage.includes('failed to fetch') ||
    errorMessage.includes('timeout') ||
    (statusCode !== undefined && statusCode >= 500)
  );
}