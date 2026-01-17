"""
Test API performance and response times
"""
import statistics
import time

import requests

BASE_URL = "http://localhost:8000"


def measure_response_time(endpoint: str, method: str = "GET", **kwargs) -> float:
    """Measure single request response time"""
    start = time.time()

    if method == "GET":
        response = requests.get(f"{BASE_URL}{endpoint}", **kwargs)
    else:
        response = requests.post(f"{BASE_URL}{endpoint}", **kwargs)

    elapsed = (time.time() - start) * 1000  # Convert to ms

    return elapsed, response.status_code


def run_performance_test(n_requests: int = 20):
    """Run performance test with multiple requests"""

    print("=" * 60)
    print(f"API Performance Test ({n_requests} requests)")
    print("=" * 60)

    endpoints = [
        ("Health Check", "/health", "GET", {}),
        (
            "VADER Prediction",
            "/predict",
            "POST",
            {"params": {"feature_set": "vader", "model_type": "random_forest"}},
        ),
        (
            "FinBERT Prediction",
            "/predict",
            "POST",
            {"params": {"feature_set": "finbert", "model_type": "random_forest"}},
        ),
        ("Both Models", "/predict/both", "POST", {}),
    ]

    results = {}

    for name, endpoint, method, kwargs in endpoints:
        print(f"\n→ Testing {name}...")
        times = []
        errors = 0

        for i in range(n_requests):
            try:
                elapsed, status_code = measure_response_time(endpoint, method, **kwargs)

                if status_code == 200:
                    times.append(elapsed)
                else:
                    errors += 1

            except Exception as e:
                errors += 1
                print(f"  Request {i+1} failed: {e}")

        if times:
            results[name] = {
                "min": min(times),
                "max": max(times),
                "mean": statistics.mean(times),
                "median": statistics.median(times),
                "stdev": statistics.stdev(times) if len(times) > 1 else 0,
                "successful": len(times),
                "errors": errors,
            }
        else:
            results[name] = {"errors": errors}

    # Print results
    print("\n" + "=" * 60)
    print("Performance Results")
    print("=" * 60)

    for name, metrics in results.items():
        print(f"\n{name}:")
        if "mean" in metrics:
            print(f"  Min:       {metrics['min']:.2f}ms")
            print(f"  Max:       {metrics['max']:.2f}ms")
            print(f"  Mean:      {metrics['mean']:.2f}ms")
            print(f"  Median:    {metrics['median']:.2f}ms")
            print(f"  Std Dev:   {metrics['stdev']:.2f}ms")
            print(f"  Success:   {metrics['successful']}/{n_requests}")

            # Check if meets target
            if metrics["mean"] < 200:
                print("  Status:    ✓ PASS (target: <200ms)")
            else:
                print("  Status:    ✗ SLOW (target: <200ms)")

        if metrics.get("errors", 0) > 0:
            print(f"  Errors:    {metrics['errors']}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    try:
        run_performance_test(n_requests=20)
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to API")
        print("Make sure the API is running: poetry run python scripts/deployment/run_api.py")
    except Exception as e:
        print(f"Test failed: {e}")
