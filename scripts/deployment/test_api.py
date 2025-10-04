"""
Test FastAPI endpoints
"""
import json

import requests

BASE_URL = "http://localhost:8000"


def print_response(endpoint: str, response: requests.Response):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"Endpoint: {endpoint}")
    print(f"Status: {response.status_code}")
    print(f"{'='*60}")
    print(json.dumps(response.json(), indent=2))


def test_root():
    """Test root endpoint"""
    response = requests.get(f"{BASE_URL}/")
    print_response("GET /", response)
    assert response.status_code == 200


def test_health():
    """Test health check"""
    response = requests.get(f"{BASE_URL}/health")
    print_response("GET /health", response)
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_list_models():
    """Test list available models"""
    response = requests.get(f"{BASE_URL}/models")
    print_response("GET /models", response)
    assert response.status_code == 200


def test_predict_vader():
    """Test prediction with VADER features"""
    response = requests.post(
        f"{BASE_URL}/predict",
        params={
            "feature_set": "vader",
            "model_type": "random_forest",
            "use_cached_features": True
        }
    )
    print_response("POST /predict (VADER)", response)
    
    if response.status_code == 200:
        data = response.json()
        if data["success"]:
            print(f"\nPrediction: {data['prediction']['direction'].upper()}")
            print(f"Confidence: {data['prediction']['confidence']:.2%}")
            print(f"Response time: {data['performance']['response_time_ms']:.2f}ms")
        else:
            print(f"\nError: {data['error']}")


def test_predict_finbert():
    """Test prediction with FinBERT features"""
    response = requests.post(
        f"{BASE_URL}/predict",
        params={
            "feature_set": "finbert",
            "model_type": "random_forest",
            "use_cached_features": True
        }
    )
    print_response("POST /predict (FinBERT)", response)
    
    if response.status_code == 200:
        data = response.json()
        if data["success"]:
            print(f"\nPrediction: {data['prediction']['direction'].upper()}")
            print(f"Confidence: {data['prediction']['confidence']:.2%}")
            print(f"Response time: {data['performance']['response_time_ms']:.2f}ms")


def test_predict_both():
    """Test prediction with both models"""
    response = requests.post(f"{BASE_URL}/predict/both")
    print_response("POST /predict/both", response)
    
    if response.status_code == 200:
        data = response.json()
        
        if data['vader']['success'] and data['finbert']['success']:
            print("\nVADER Prediction:", data['vader']['prediction']['direction'].upper())
            print("FinBERT Prediction:", data['finbert']['prediction']['direction'].upper())
            print("Agreement:", "YES" if data['agreement'] else "NO")


def test_invalid_feature_set():
    """Test error handling with invalid feature set"""
    response = requests.post(
        f"{BASE_URL}/predict",
        params={
            "feature_set": "invalid",
            "model_type": "random_forest"
        }
    )
    print_response("POST /predict (invalid feature_set)", response)
    assert response.status_code == 422  # Validation error


def main():
    print("="*60)
    print("Bitcoin Prediction API Tests")
    print("="*60)
    
    try:
        # Basic endpoints
        test_root()
        test_health()
        test_list_models()
        
        # Prediction endpoints
        test_predict_vader()
        test_predict_finbert()
        test_predict_both()
        
        # Error handling
        test_invalid_feature_set()
        
        print("\n" + "="*60)
        print("All tests passed!")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to API")
        print("Make sure the API is running: poetry run python scripts/deployment/run_api.py")
    except AssertionError as e:
        print(f"\nTest failed: {e}")
    except Exception as e:
        print(f"\nUnexpected error: {e}")


if __name__ == "__main__":
    main()