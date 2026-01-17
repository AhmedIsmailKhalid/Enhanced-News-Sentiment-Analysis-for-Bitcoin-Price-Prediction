"""
Test FastAPI with Prediction Logging Integration
Tests all endpoints including new MLOps monitoring endpoints
"""

import os
import sys
import time

import requests

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.shared.logging import get_logger, setup_logging

# API configuration
API_BASE_URL = "http://localhost:8000"


def test_health_check():
    """Test health check endpoint"""
    logger = get_logger(__name__)
    logger.info("\n" + "=" * 60)
    logger.info("TEST 1: Health Check")
    logger.info("=" * 60)

    try:
        response = requests.get(f"{API_BASE_URL}/health")

        if response.status_code == 200:
            data = response.json()
            logger.info(f"Status: {data.get('status')}")
            logger.info(f"Loaded Models: {data.get('loaded_models')}")
            logger.info("✅ Health check passed")
            return True
        else:
            logger.error(f"❌ Health check failed with status {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"❌ Health check error: {e}")
        return False


def test_single_prediction_with_logging():
    """Test single prediction endpoint with logging"""
    logger = get_logger(__name__)
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: Single Prediction with Logging (VADER)")
    logger.info("=" * 60)

    try:
        response = requests.post(
            f"{API_BASE_URL}/predict",
            params={
                "feature_set": "vader",
                "model_type": "random_forest",
                "use_cached_features": True,
            },
        )

        if response.status_code == 200:
            data = response.json()

            logger.info("Prediction Result:")
            logger.info(f"  Direction: {data['prediction']['direction']}")
            logger.info(f"  Confidence: {data['prediction']['confidence']:.3f}")
            logger.info(f"  Probability UP: {data['prediction']['probability']['up']:.3f}")
            logger.info(f"  Probability DOWN: {data['prediction']['probability']['down']:.3f}")
            logger.info(f"  Response Time: {data['performance']['response_time_ms']:.2f}ms")

            # Check if prediction was logged
            if "prediction_id" in data:
                logger.info(f"  Prediction ID: {data['prediction_id']}")
                logger.info("✅ Prediction logged successfully")
                return data["prediction_id"]
            else:
                logger.warning("⚠️  Prediction not logged (prediction_id missing)")
                return None
        else:
            logger.error(f"❌ Prediction failed with status {response.status_code}")
            logger.error(f"Response: {response.text}")
            return None

    except Exception as e:
        logger.error(f"❌ Prediction error: {e}")
        return None


def test_dual_prediction_with_logging():
    """Test dual prediction endpoint with logging"""
    logger = get_logger(__name__)
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: Dual Prediction with Logging (VADER + FinBERT)")
    logger.info("=" * 60)

    try:
        response = requests.post(
            f"{API_BASE_URL}/predict/both", params={"use_cached_features": True}
        )

        if response.status_code == 200:
            data = response.json()

            logger.info("VADER Prediction:")
            logger.info(f"  Direction: {data['vader']['prediction']['direction']}")
            logger.info(f"  Confidence: {data['vader']['prediction']['confidence']:.3f}")
            logger.info(f"  Prediction ID: {data['vader'].get('prediction_id', 'Not logged')}")

            logger.info("\nFinBERT Prediction:")
            logger.info(f"  Direction: {data['finbert']['prediction']['direction']}")
            logger.info(f"  Confidence: {data['finbert']['prediction']['confidence']:.3f}")
            logger.info(f"  Prediction ID: {data['finbert'].get('prediction_id', 'Not logged')}")

            logger.info(f"\nAgreement: {data.get('agreement')}")
            logger.info(
                f"Total Response Time: {data['performance']['total_response_time_ms']:.2f}ms"
            )

            # Check if both predictions were logged
            vader_logged = "prediction_id" in data["vader"]
            finbert_logged = "prediction_id" in data["finbert"]

            if vader_logged and finbert_logged:
                logger.info("✅ Both predictions logged successfully")
                return True
            else:
                logger.warning(
                    f"⚠️  Logging incomplete - VADER: {vader_logged}, FinBERT: {finbert_logged}"
                )
                return False
        else:
            logger.error(f"❌ Dual prediction failed with status {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False

    except Exception as e:
        logger.error(f"❌ Dual prediction error: {e}")
        return False


def test_get_recent_predictions():
    """Test getting recent predictions"""
    logger = get_logger(__name__)
    logger.info("\n" + "=" * 60)
    logger.info("TEST 4: Get Recent Predictions")
    logger.info("=" * 60)

    try:
        response = requests.get(f"{API_BASE_URL}/predictions/recent", params={"limit": 10})

        if response.status_code == 200:
            data = response.json()

            logger.info(f"Success: {data.get('success')}")
            logger.info(f"Count: {data.get('count')}")

            if data.get("predictions"):
                logger.info("\nSample Recent Prediction:")
                pred = data["predictions"][0]
                logger.info(f"  ID: {pred['id']}")
                logger.info(f"  Feature Set: {pred['feature_set']}")
                logger.info(f"  Model: {pred['model_type']}")
                logger.info(f"  Prediction: {'UP' if pred['prediction'] == 1 else 'DOWN'}")
                logger.info(f"  Confidence: {pred['confidence']:.3f}")
                logger.info(f"  Predicted At: {pred['predicted_at']}")

                if pred["prediction_correct"] is not None:
                    logger.info(f"  Actual: {'UP' if pred['actual_direction'] == 1 else 'DOWN'}")
                    logger.info(f"  Correct: {pred['prediction_correct']}")
                else:
                    logger.info("  Outcome: Not yet recorded")

            logger.info("✅ Recent predictions retrieved successfully")
            return True
        else:
            logger.error(f"❌ Failed with status {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False


def test_get_model_accuracy():
    """Test getting model accuracy"""
    logger = get_logger(__name__)
    logger.info("\n" + "=" * 60)
    logger.info("TEST 5: Get Model Accuracy")
    logger.info("=" * 60)

    try:
        response = requests.get(
            f"{API_BASE_URL}/predictions/accuracy",
            params={"feature_set": "vader", "model_type": "random_forest", "days": 7},
        )

        if response.status_code == 200:
            data = response.json()

            logger.info(f"Success: {data.get('success')}")

            stats = data.get("accuracy_stats", {})
            logger.info(f"\nModel: {stats.get('feature_set')}/{stats.get('model_type')}")
            logger.info(f"Period: {stats.get('period_days')} days")
            logger.info(f"Total Predictions: {stats.get('total_predictions')}")

            if stats.get("accuracy") is not None:
                logger.info(f"Accuracy: {stats.get('accuracy'):.2%}")
                logger.info(f"Correct: {stats.get('correct_predictions')}")
                logger.info(f"Incorrect: {stats.get('incorrect_predictions')}")
                logger.info(f"Avg Confidence: {stats.get('avg_confidence'):.3f}")
            else:
                logger.info(f"Message: {stats.get('message', 'No accuracy data available')}")

            logger.info("✅ Model accuracy retrieved successfully")
            return True
        else:
            logger.error(f"❌ Failed with status {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False


def test_get_statistics():
    """Test getting overall statistics"""
    logger = get_logger(__name__)
    logger.info("\n" + "=" * 60)
    logger.info("TEST 6: Get Overall Statistics")
    logger.info("=" * 60)

    try:
        response = requests.get(f"{API_BASE_URL}/predictions/statistics")

        if response.status_code == 200:
            data = response.json()

            logger.info(f"Success: {data.get('success')}")

            stats = data.get("statistics", {})
            logger.info(f"\nTotal Predictions: {stats.get('total_predictions')}")
            logger.info(f"Predictions with Outcomes: {stats.get('predictions_with_outcomes')}")
            logger.info(f"Correct Predictions: {stats.get('correct_predictions')}")

            if stats.get("overall_accuracy") is not None:
                logger.info(f"Overall Accuracy: {stats.get('overall_accuracy'):.2%}")

            logger.info(f"VADER Predictions: {stats.get('vader_predictions')}")
            logger.info(f"FinBERT Predictions: {stats.get('finbert_predictions')}")

            if stats.get("avg_response_time_ms") is not None:
                logger.info(f"Avg Response Time: {stats.get('avg_response_time_ms'):.2f}ms")

            logger.info(f"Pending Outcomes: {stats.get('pending_outcomes')}")

            logger.info("✅ Statistics retrieved successfully")
            return True
        else:
            logger.error(f"❌ Failed with status {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False


def test_filtered_recent_predictions():
    """Test getting recent predictions with filters"""
    logger = get_logger(__name__)
    logger.info("\n" + "=" * 60)
    logger.info("TEST 7: Get Recent Predictions (Filtered by VADER)")
    logger.info("=" * 60)

    try:
        response = requests.get(
            f"{API_BASE_URL}/predictions/recent", params={"feature_set": "vader", "limit": 5}
        )

        if response.status_code == 200:
            data = response.json()

            logger.info(f"Count (VADER only): {data.get('count')}")
            logger.info(f"Filters Applied: {data.get('filters')}")

            logger.info("✅ Filtered predictions retrieved successfully")
            return True
        else:
            logger.error(f"❌ Failed with status {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False


def test_multiple_predictions():
    """Test making multiple predictions to build up statistics"""
    logger = get_logger(__name__)
    logger.info("\n" + "=" * 60)
    logger.info("TEST 8: Make Multiple Predictions")
    logger.info("=" * 60)

    try:
        prediction_ids = []

        # Make 5 predictions (alternating VADER and FinBERT)
        for i in range(5):
            feature_set = "vader" if i % 2 == 0 else "finbert"

            response = requests.post(
                f"{API_BASE_URL}/predict",
                params={
                    "feature_set": feature_set,
                    "model_type": "random_forest",
                    "use_cached_features": True,
                },
            )

            if response.status_code == 200:
                data = response.json()
                if "prediction_id" in data:
                    prediction_ids.append(data["prediction_id"])
                    logger.info(f"  Prediction {i+1} ({feature_set}): ID {data['prediction_id']}")

            time.sleep(0.5)  # Small delay between requests

        logger.info(f"\n✅ Made {len(prediction_ids)} predictions successfully")
        return len(prediction_ids) == 5

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False


def main():
    """Run all tests"""
    setup_logging()
    logger = get_logger(__name__)

    logger.info("=" * 60)
    logger.info("API WITH PREDICTION LOGGING - COMPREHENSIVE TESTS")
    logger.info("=" * 60)
    logger.info("\nIMPORTANT: Make sure the API server is running!")
    logger.info("Run: poetry run python scripts/deployment/run_api.py")
    logger.info("=" * 60)

    # Wait a moment for user to confirm
    input("\nPress Enter when API server is ready...")

    # Run tests
    results = []

    results.append(("Health Check", test_health_check()))
    results.append(
        ("Single Prediction with Logging", test_single_prediction_with_logging() is not None)
    )
    results.append(("Dual Prediction with Logging", test_dual_prediction_with_logging()))
    results.append(("Get Recent Predictions", test_get_recent_predictions()))
    results.append(("Get Model Accuracy", test_get_model_accuracy()))
    results.append(("Get Statistics", test_get_statistics()))
    results.append(("Filtered Recent Predictions", test_filtered_recent_predictions()))
    results.append(("Multiple Predictions", test_multiple_predictions()))

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)

    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        logger.info(f"{test_name}: {status}")

    all_passed = all(result[1] for result in results)

    logger.info("=" * 60)
    if all_passed:
        logger.info("✅ ALL TESTS PASSED")
        logger.info("\nPrediction logging is fully integrated!")
        logger.info("New MLOps endpoints are working:")
        logger.info("  - GET /predictions/recent")
        logger.info("  - GET /predictions/accuracy")
        logger.info("  - GET /predictions/statistics")
    else:
        logger.info("❌ SOME TESTS FAILED")
    logger.info("=" * 60)

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
