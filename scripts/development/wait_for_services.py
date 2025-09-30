"""
Wait for Docker services to be ready before proceeding
"""
import sys
import time
from typing import Tuple

import psycopg2
import redis
from dotenv import load_dotenv

load_dotenv('.env.dev')


def wait_for_postgres(max_retries: int = 30) -> bool:
    """Wait for PostgreSQL to be ready"""
    print("Waiting for PostgreSQL...")
    
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                user="bitcoin_user",
                password="bitcoin_password",
                database="bitcoin_sentiment_dev"
            )
            conn.close()
            print("✓ PostgreSQL is ready!")
            return True
        except psycopg2.OperationalError:
            print(f"  Attempt {attempt + 1}/{max_retries}: PostgreSQL not ready yet...")
            time.sleep(2)
    
    print("✗ PostgreSQL failed to start")
    return False


def wait_for_redis(max_retries: int = 30) -> bool:
    """Wait for Redis to be ready"""
    print("Waiting for Redis...")
    
    for attempt in range(max_retries):
        try:
            r = redis.Redis(host='localhost', port=6379, db=0)
            r.ping()
            print("✓ Redis is ready!")
            return True
        except redis.ConnectionError:
            print(f"  Attempt {attempt + 1}/{max_retries}: Redis not ready yet...")
            time.sleep(2)
    
    print("✗ Redis failed to start")
    return False


def main() -> int:
    """Main function"""
    postgres_ready = wait_for_postgres()
    redis_ready = wait_for_redis()
    
    if postgres_ready and redis_ready:
        print("\n✓ All services are ready!")
        return 0
    else:
        print("\n✗ Some services failed to start")
        return 1


if __name__ == "__main__":
    sys.exit(main())