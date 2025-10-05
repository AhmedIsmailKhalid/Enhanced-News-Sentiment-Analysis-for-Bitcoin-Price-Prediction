"""
Test Prediction Logging System
Tests all functionality of the PredictionLogger class
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.mlops.prediction_logger import PredictionLogger
from src.shared.database import SessionLocal, engine  # noqa
from src.shared.logging import get_logger, setup_logging
from src.shared.models import Base, PredictionLog  # noqa


def create_prediction_logs_table():
    """Create prediction_logs table if it doesn't exist"""
    logger = get_logger(__name__)
    
    try:
        logger.info("Creating prediction_logs table...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Table created successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create table: {e}")
        return False


def test_log_prediction():
    """Test logging a single prediction"""
    logger = get_logger(__name__)
    logger.info("\n" + "="*60)
    logger.info("TEST 1: Log Single Prediction")
    logger.info("="*60)
    
    try:
        prediction_logger = PredictionLogger()
        
        # Sample features
        sample_features = {
            'price_usd': 43250.50,
            'vader_compound': 0.456,
            'sma_7': 43100.25,
            'rsi_14': 65.3,
            'volume_24h': 25000000000,
            'sentiment_mean_24h': 0.423
        }
        
        # Log prediction
        prediction_id = prediction_logger.log_prediction(
            feature_set='vader',
            model_type='random_forest',
            model_version='20251003_211954',
            prediction=1,  # UP
            probability_down=0.35,
            probability_up=0.65,
            confidence=0.65,
            features=sample_features,
            response_time_ms=52.3,
            cached_features=True,
            bitcoin_price=43250.50
        )
        
        if prediction_id > 0:
            logger.info(f"✅ Prediction logged successfully with ID: {prediction_id}")
            return prediction_id
        else:
            logger.error("❌ Failed to log prediction")
            return None
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return None


def test_update_outcome(prediction_id: int):
    """Test updating prediction with actual outcome"""
    logger = get_logger(__name__)
    logger.info("\n" + "="*60)
    logger.info("TEST 2: Update Prediction Outcome")
    logger.info("="*60)
    
    try:
        prediction_logger = PredictionLogger()
        
        # Update with actual outcome (price went up)
        success = prediction_logger.update_prediction_outcome(
            prediction_id=prediction_id,
            actual_direction=1,  # Actually went UP
            bitcoin_price_1h_later=43450.75
        )
        
        if success:
            logger.info("✅ Prediction outcome updated successfully")
            logger.info("   Prediction was CORRECT (predicted UP, actually went UP)")
        else:
            logger.error("❌ Failed to update prediction outcome")
            
        return success
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False


def test_get_recent_predictions():
    """Test retrieving recent predictions"""
    logger = get_logger(__name__)
    logger.info("\n" + "="*60)
    logger.info("TEST 3: Get Recent Predictions")
    logger.info("="*60)
    
    try:
        prediction_logger = PredictionLogger()
        
        # Get all recent predictions
        predictions = prediction_logger.get_recent_predictions(limit=10)
        
        logger.info(f"Retrieved {len(predictions)} recent predictions")
        
        if predictions:
            logger.info("\nSample prediction:")
            pred = predictions[0]
            logger.info(f"  ID: {pred['id']}")
            logger.info(f"  Feature Set: {pred['feature_set']}")
            logger.info(f"  Model: {pred['model_type']}")
            logger.info(f"  Prediction: {'UP' if pred['prediction'] == 1 else 'DOWN'}")
            logger.info(f"  Confidence: {pred['confidence']:.3f}")
            logger.info(f"  Actual: {'UP' if pred['actual_direction'] == 1 else 'DOWN' if pred['actual_direction'] == 0 else 'Unknown'}")
            logger.info(f"  Correct: {pred['prediction_correct']}")
            logger.info(f"  Response Time: {pred['response_time_ms']:.2f}ms")
            logger.info("✅ Successfully retrieved predictions")
        else:
            logger.warning("⚠️  No predictions found")
            
        return len(predictions) > 0
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False


def test_get_model_accuracy():
    """Test calculating model accuracy"""
    logger = get_logger(__name__)
    logger.info("\n" + "="*60)
    logger.info("TEST 4: Get Model Accuracy")
    logger.info("="*60)
    
    try:
        prediction_logger = PredictionLogger()
        
        # Get accuracy for VADER random forest
        accuracy_stats = prediction_logger.get_model_accuracy(
            feature_set='vader',
            model_type='random_forest',
            days=7
        )
        
        logger.info("Model Accuracy Statistics:")
        logger.info(f"  Feature Set: {accuracy_stats.get('feature_set')}")
        logger.info(f"  Model Type: {accuracy_stats.get('model_type')}")
        logger.info(f"  Period: {accuracy_stats.get('period_days')} days")
        logger.info(f"  Total Predictions: {accuracy_stats.get('total_predictions')}")
        
        if accuracy_stats.get('accuracy') is not None:
            logger.info(f"  Accuracy: {accuracy_stats.get('accuracy'):.2%}")
            logger.info(f"  Correct: {accuracy_stats.get('correct_predictions')}")
            logger.info(f"  Incorrect: {accuracy_stats.get('incorrect_predictions')}")
            logger.info(f"  UP Predictions: {accuracy_stats.get('up_predictions')} (accuracy: {accuracy_stats.get('up_accuracy'):.2%})")
            logger.info(f"  DOWN Predictions: {accuracy_stats.get('down_predictions')} (accuracy: {accuracy_stats.get('down_accuracy'):.2%})")
            logger.info(f"  Avg Confidence: {accuracy_stats.get('avg_confidence'):.3f}")
            logger.info(f"  Avg Confidence (Correct): {accuracy_stats.get('avg_confidence_when_correct'):.3f}")
            logger.info(f"  Avg Confidence (Incorrect): {accuracy_stats.get('avg_confidence_when_incorrect'):.3f}")
            logger.info("✅ Accuracy calculation successful")
        else:
            logger.warning(f"⚠️  {accuracy_stats.get('message', 'No accuracy data available')}")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False


def test_get_statistics():
    """Test getting overall statistics"""
    logger = get_logger(__name__)
    logger.info("\n" + "="*60)
    logger.info("TEST 5: Get Overall Statistics")
    logger.info("="*60)
    
    try:
        prediction_logger = PredictionLogger()
        
        stats = prediction_logger.get_prediction_statistics()
        
        logger.info("Overall Statistics:")
        logger.info(f"  Total Predictions: {stats.get('total_predictions')}")
        logger.info(f"  Predictions with Outcomes: {stats.get('predictions_with_outcomes')}")
        logger.info(f"  Correct Predictions: {stats.get('correct_predictions')}")
        
        if stats.get('overall_accuracy') is not None:
            logger.info(f"  Overall Accuracy: {stats.get('overall_accuracy'):.2%}")
        else:
            logger.info("  Overall Accuracy: Not available (no outcomes yet)")
            
        logger.info(f"  VADER Predictions: {stats.get('vader_predictions')}")
        logger.info(f"  FinBERT Predictions: {stats.get('finbert_predictions')}")
        
        if stats.get('avg_response_time_ms') is not None:
            logger.info(f"  Avg Response Time: {stats.get('avg_response_time_ms'):.2f}ms")
            
        logger.info(f"  Pending Outcomes: {stats.get('pending_outcomes')}")
        logger.info("✅ Statistics retrieval successful")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False


def test_multiple_predictions():
    """Test logging multiple predictions for better statistics"""
    logger = get_logger(__name__)
    logger.info("\n" + "="*60)
    logger.info("TEST 6: Log Multiple Predictions")
    logger.info("="*60)
    
    try:
        prediction_logger = PredictionLogger()
        
        # Create sample predictions with different outcomes
        test_cases = [
            # (feature_set, model_type, prediction, actual, bitcoin_price_start, bitcoin_price_end)
            ('vader', 'random_forest', 1, 1, 43000, 43200),      # Correct UP
            ('vader', 'random_forest', 0, 0, 43200, 43100),      # Correct DOWN
            ('vader', 'random_forest', 1, 0, 43100, 43050),      # Incorrect (predicted UP, went DOWN)
            ('finbert', 'random_forest', 0, 1, 43050, 43150),    # Incorrect (predicted DOWN, went UP)
            ('finbert', 'random_forest', 1, 1, 43150, 43300),    # Correct UP
        ]
        
        prediction_ids = []
        
        for i, (feature_set, model_type, pred, actual, price_start, price_end) in enumerate(test_cases):
            # Sample features
            features = {
                'price_usd': price_start,
                f'{feature_set}_compound': 0.5 if pred == 1 else -0.3,
                'sma_7': price_start * 0.99,
                'test_case': i
            }
            
            # Log prediction
            pred_id = prediction_logger.log_prediction(
                feature_set=feature_set,
                model_type=model_type,
                model_version='20251003_211954',
                prediction=pred,
                probability_down=0.4 if pred == 1 else 0.6,
                probability_up=0.6 if pred == 1 else 0.4,
                confidence=0.6,
                features=features,
                response_time_ms=50.0 + i * 5,
                cached_features=True,
                bitcoin_price=price_start
            )
            
            if pred_id > 0:
                # Update with outcome
                prediction_logger.update_prediction_outcome(
                    prediction_id=pred_id,
                    actual_direction=actual,
                    bitcoin_price_1h_later=price_end
                )
                prediction_ids.append(pred_id)
        
        logger.info(f"✅ Successfully logged and updated {len(prediction_ids)} predictions")
        return len(prediction_ids) == len(test_cases)
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False


def main():
    """Run all tests"""
    setup_logging()
    logger = get_logger(__name__)
    
    logger.info("="*60)
    logger.info("PREDICTION LOGGING SYSTEM TESTS")
    logger.info("="*60)
    
    # Create table
    if not create_prediction_logs_table():
        logger.error("Failed to create table, aborting tests")
        return False
    
    # Run tests
    results = []
    
    # Test 1: Log single prediction
    prediction_id = test_log_prediction()
    results.append(("Log Prediction", prediction_id is not None))
    
    # Test 2: Update outcome (only if test 1 succeeded)
    if prediction_id:
        results.append(("Update Outcome", test_update_outcome(prediction_id)))
    else:
        results.append(("Update Outcome", False))
    
    # Test 3: Get recent predictions
    results.append(("Get Recent Predictions", test_get_recent_predictions()))
    
    # Test 4: Get model accuracy
    results.append(("Get Model Accuracy", test_get_model_accuracy()))
    
    # Test 5: Get overall statistics
    results.append(("Get Statistics", test_get_statistics()))
    
    # Test 6: Multiple predictions
    results.append(("Multiple Predictions", test_multiple_predictions()))
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("TEST SUMMARY")
    logger.info("="*60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    logger.info("="*60)
    if all_passed:
        logger.info("✅ ALL TESTS PASSED")
    else:
        logger.info("❌ SOME TESTS FAILED")
    logger.info("="*60)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)