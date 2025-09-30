"""
Master test runner - runs all verification and testing scripts
"""
import subprocess
import sys


def run_script(script_path: str, description: str) -> bool:
    """Run a Python script and return success status"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print('='*60)
    
    try:
        result = subprocess.run(
            ['poetry', 'run', 'python', script_path],
            check=True,
            capture_output=False
        )
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed with code {e.returncode}")
        return False
    except Exception as e:
        print(f"✗ {description} failed: {e}")
        return False


def main():
    print("="*60)
    print("Bitcoin Sentiment MLOps - Complete Test Suite")
    print("="*60)
    
    tests = [
        ('scripts/development/verify_setup.py', 'Environment Verification'),
        ('scripts/development/test_connections.py', 'Database Connection Tests'),
        ('scripts/development/test_redis.py', 'Redis Operations Tests'),
    ]
    
    results = {}
    
    for script_path, description in tests:
        results[description] = run_script(script_path, description)
    
    # Summary
    print("\n" + "="*60)
    print("COMPLETE TEST SUMMARY")
    print("="*60)
    
    for test_name, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("✓ ALL TESTS PASSED - Environment fully verified!")
        print("✓ Ready to proceed with data collector development")
    else:
        print("✗ SOME TESTS FAILED - Review errors above")
    print("="*60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())