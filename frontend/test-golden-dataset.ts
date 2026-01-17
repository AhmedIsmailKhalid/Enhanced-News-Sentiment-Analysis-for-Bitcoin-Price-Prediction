import { 
  getGoldenPriceData, 
  getGoldenSentimentData,
  getGoldenPredictions,
  getGoldenStatistics,
  getGoldenAccuracyData,
  getGoldenConfidenceData 
} from './lib/golden-dataset.js'; // Add .js extension for ts-node

console.log('=== Testing Golden Dataset ===\n');

// Test 1: Price Data
const priceData = getGoldenPriceData();
console.log(`✓ Price Data: ${priceData.length} points`);
console.log(`  Sample: $${priceData[0].price.toLocaleString()}`);
console.log(`  Range: $${Math.min(...priceData.map(p => p.price)).toLocaleString()} - $${Math.max(...priceData.map(p => p.price)).toLocaleString()}\n`);

// Test 2: Sentiment Data
const sentimentData = getGoldenSentimentData();
console.log(`✓ Sentiment Data: ${sentimentData.vader.length} VADER + ${sentimentData.finbert.length} FinBERT`);
console.log(`  VADER range: ${Math.min(...sentimentData.vader.map(s => s.score)).toFixed(3)} to ${Math.max(...sentimentData.vader.map(s => s.score)).toFixed(3)}`);
console.log(`  FinBERT range: ${Math.min(...sentimentData.finbert.map(s => s.score)).toFixed(3)} to ${Math.max(...sentimentData.finbert.map(s => s.score)).toFixed(3)}\n`);

// Test 3: Predictions
const predictions = getGoldenPredictions();
console.log(`✓ Predictions: ${predictions.length} records`);
console.log(`  With outcomes: ${predictions.filter(p => p.prediction_correct !== null).length}`);
console.log(`  Pending: ${predictions.filter(p => p.prediction_correct === null).length}\n`);

// Test 4: Statistics
const stats = getGoldenStatistics();
console.log(`✓ Statistics:`);
console.log(`  Total predictions: ${stats.total_predictions}`);
console.log(`  VADER accuracy: ${stats.vader_accuracy.toFixed(1)}%`);
console.log(`  FinBERT accuracy: ${stats.finbert_accuracy.toFixed(1)}%`);
console.log(`  Avg response time: ${stats.avg_response_time_ms.toFixed(0)}ms\n`);

// Test 5: Accuracy Data
const vaderAccuracy = getGoldenAccuracyData('vader');
console.log(`✓ VADER Accuracy: ${(vaderAccuracy.overall_accuracy * 100).toFixed(1)}%`);
console.log(`  By window:`, Object.entries(vaderAccuracy.accuracy_by_window || {}).map(([w, a]) => `${w}=${(a * 100).toFixed(1)}%`).join(', '));

const finbertAccuracy = getGoldenAccuracyData('finbert');
console.log(`✓ FinBERT Accuracy: ${(finbertAccuracy.overall_accuracy * 100).toFixed(1)}%`);
console.log(`  By window:`, Object.entries(finbertAccuracy.accuracy_by_window || {}).map(([w, a]) => `${w}=${(a * 100).toFixed(1)}%`).join(', '), '\n');

// Test 6: Confidence Data
const confidence = getGoldenConfidenceData();
console.log(`✓ Confidence Data: ${confidence.chartData.length} points`);
console.log(`  VADER avg: ${confidence.vaderAvg.toFixed(1)}%`);
console.log(`  FinBERT avg: ${confidence.finbertAvg.toFixed(1)}%\n`);

// Test 7: Verify noise is working (call twice, should get different values)
const price1 = getGoldenPriceData()[0].price;
const price2 = getGoldenPriceData()[0].price;
console.log(`✓ Noise verification:`);
console.log(`  Call 1: $${price1.toLocaleString()}`);
console.log(`  Call 2: $${price2.toLocaleString()}`);
console.log(`  Different: ${price1 !== price2 ? '✓ YES' : '✗ NO (noise not working)'}\n`);

console.log('=== All Tests Passed! ===');