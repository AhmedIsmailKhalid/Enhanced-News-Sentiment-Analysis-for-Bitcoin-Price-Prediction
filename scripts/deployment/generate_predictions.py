"""
Generate predictions by calling the API endpoint
More reliable than direct database access
"""
import os
import time

import requests

API_URL = os.getenv('API_URL', 'http://localhost:8000')

def generate_predictions(count=10):
    """Generate predictions via API"""
    
    print(f"Generating {count} predictions via API...")
    
    for i in range(count):
        try:
            # VADER prediction
            vader_response = requests.post(
                f"{API_URL}/predict",
                params={
                    "feature_set": "vader",
                    "model_type": "random_forest"
                }
            )
            
            # FinBERT prediction
            finbert_response = requests.post(
                f"{API_URL}/predict",
                params={
                    "feature_set": "finbert",
                    "model_type": "random_forest"
                }
            )
            
            if vader_response.status_code == 200 and finbert_response.status_code == 200:
                print(f"✓ Generated prediction pair {i+1}/{count}")
            else:
                print(f"✗ Failed: VADER={vader_response.status_code}, FinBERT={finbert_response.status_code}")
            
            time.sleep(1)  # Rate limiting
            
        except Exception as e:
            print(f"Error: {e}")
    
    print(f"\nGenerated {count} prediction pairs (total {count*2} predictions)")

if __name__ == "__main__":
    generate_predictions(count=500)