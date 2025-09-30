"""
Comprehensive environment setup verification
Tests all components: Docker services, databases, Redis, configurations
"""
# ruff: noqa E402
import os
import sys
from pathlib import Path
from typing import List, Tuple

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import psycopg2
import redis
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv('.env.dev')


class SetupVerifier:
    """Verify complete development environment setup"""
    
    def __init__(self):
        self.results: List[Tuple[str, bool, str]] = []
        self.critical_failures = 0
    
    def log_result(self, test_name: str, success: bool, message: str, critical: bool = False):
        """Log test result"""
        self.results.append((test_name, success, message))
        if not success and critical:
            self.critical_failures += 1
        
        status = "✓" if success else "✗"
        print(f"{status} {test_name}: {message}")
    
    def verify_env_file(self) -> bool:
        """Check .env.dev file exists and has required variables"""
        print("\n" + "=" * 60)
        print("1. Environment Configuration")
        print("=" * 60)
        
        env_file = Path('.env.dev')
        if not env_file.exists():
            self.log_result(
                "Environment File",
                False,
                ".env.dev not found",
                critical=True
            )
            return False
        
        self.log_result(
            "Environment File",
            True,
            ".env.dev exists"
        )
        
        # Check required variables
        required_vars = [
            'DATABASE_URL',
            'REDIS_HOST',
            'REDIS_PORT',
            'ENVIRONMENT'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            self.log_result(
                "Required Variables",
                False,
                f"Missing: {', '.join(missing_vars)}",
                critical=True
            )
            return False
        
        self.log_result(
            "Required Variables",
            True,
            "All required variables present"
        )
        
        return True
    
    def verify_local_postgres(self) -> bool:
        """Verify local PostgreSQL connection and tables"""
        print("\n" + "=" * 60)
        print("2. Local PostgreSQL")
        print("=" * 60)
        
        try:
            # Test connection
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                user="bitcoin_user",
                password="bitcoin_password",
                database="bitcoin_sentiment_dev"
            )
            
            self.log_result(
                "Connection",
                True,
                "Connected to local PostgreSQL",
                critical=True
            )
            
            # Check tables
            cursor = conn.cursor()
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema='public' 
                ORDER BY table_name
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = [
                'collection_metadata',
                'feature_data',
                'news_data',
                'price_data',
                'sentiment_data'
            ]
            
            missing_tables = set(expected_tables) - set(tables)
            
            if missing_tables:
                self.log_result(
                    "Database Tables",
                    False,
                    f"Missing tables: {', '.join(missing_tables)}",
                    critical=True
                )
                conn.close()
                return False
            
            self.log_result(
                "Database Tables",
                True,
                f"All {len(expected_tables)} tables present"
            )
            
            # Check table structure (sample one table)
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name='price_data' 
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()
            
            if len(columns) >= 10:  # Should have at least 10 columns
                self.log_result(
                    "Table Structure",
                    True,
                    f"price_data has {len(columns)} columns"
                )
            else:
                self.log_result(
                    "Table Structure",
                    False,
                    f"price_data has only {len(columns)} columns"
                )
            
            conn.close()
            return True
            
        except Exception as e:
            self.log_result(
                "Connection",
                False,
                f"Failed: {str(e)}",
                critical=True
            )
            return False
    
    def verify_neondb(self) -> bool:
        """Verify NeonDB connections and tables"""
        print("\n" + "=" * 60)
        print("3. NeonDB (Production & Backup)")
        print("=" * 60)
        
        prod_url = os.getenv('NEONDB_PRODUCTION_URL')
        backup_url = os.getenv('NEONDB_BACKUP_URL')
        
        if not prod_url:
            self.log_result(
                "Production Branch",
                False,
                "NEONDB_PRODUCTION_URL not configured",
                critical=False
            )
            return False
        
        # Test production branch
        try:
            engine = create_engine(prod_url)
            with engine.connect() as conn:
                result = conn.execute(text(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema='public'"
                ))
                tables = [row[0] for row in result]
                
                if len(tables) >= 5:
                    self.log_result(
                        "Production Branch",
                        True,
                        f"Connected, {len(tables)} tables present"
                    )
                else:
                    self.log_result(
                        "Production Branch",
                        False,
                        f"Connected but only {len(tables)} tables found"
                    )
        except Exception as e:
            self.log_result(
                "Production Branch",
                False,
                f"Connection failed: {str(e)[:50]}"
            )
        
        # Test backup branch
        if backup_url:
            try:
                engine = create_engine(backup_url)
                with engine.connect() as conn:
                    result = conn.execute(text(
                        "SELECT table_name FROM information_schema.tables "
                        "WHERE table_schema='public'"
                    ))
                    tables = [row[0] for row in result]
                    
                    if len(tables) >= 5:
                        self.log_result(
                            "Backup Branch",
                            True,
                            f"Connected, {len(tables)} tables present"
                        )
                    else:
                        self.log_result(
                            "Backup Branch",
                            False,
                            f"Connected but only {len(tables)} tables found"
                        )
            except Exception as e:
                self.log_result(
                    "Backup Branch",
                    False,
                    f"Connection failed: {str(e)[:50]}"
                )
        else:
            self.log_result(
                "Backup Branch",
                False,
                "NEONDB_BACKUP_URL not configured",
                critical=False
            )
        
        return True
    
    def verify_redis(self) -> bool:
        """Verify Redis connection and basic operations"""
        print("\n" + "=" * 60)
        print("4. Redis Cache")
        print("=" * 60)
        
        try:
            r = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                db=int(os.getenv('REDIS_DB', 0)),
                decode_responses=True
            )
            
            # Test connection
            r.ping()
            self.log_result(
                "Connection",
                True,
                "Connected to Redis",
                critical=True
            )
            
            # Test write/read
            test_key = "test:setup_verification"
            test_value = "verification_test"
            
            r.set(test_key, test_value, ex=10)
            retrieved = r.get(test_key)
            
            if retrieved == test_value:
                self.log_result(
                    "Read/Write",
                    True,
                    "Write and read operations successful"
                )
            else:
                self.log_result(
                    "Read/Write",
                    False,
                    "Value mismatch in read/write test"
                )
            
            # Clean up
            r.delete(test_key)
            
            # Check info
            info = r.info()
            memory_mb = info['used_memory'] / (1024 * 1024)
            
            self.log_result(
                "Server Info",
                True,
                f"Redis {info['redis_version']}, Memory: {memory_mb:.2f}MB"
            )
            
            return True
            
        except Exception as e:
            self.log_result(
                "Connection",
                False,
                f"Failed: {str(e)}",
                critical=True
            )
            return False
    
    def verify_docker_services(self) -> bool:
        """Verify Docker services are running"""
        print("\n" + "=" * 60)
        print("5. Docker Services")
        print("=" * 60)
        
        import subprocess
        
        try:
            # Check docker-compose ps
            result = subprocess.run(
                ['docker-compose', 'ps', '--format', 'json'],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Count running services
            output = result.stdout.strip()
            if output:
                lines = output.split('\n')
                running_count = sum(1 for line in lines if 'Up' in line or 'running' in line.lower())
                
                if running_count >= 2:  # postgres + redis
                    self.log_result(
                        "Services Running",
                        True,
                        f"{running_count} services running"
                    )
                else:
                    self.log_result(
                        "Services Running",
                        False,
                        f"Only {running_count} services running"
                    )
            else:
                self.log_result(
                    "Services Running",
                    False,
                    "No services found"
                )
            
            return True
            
        except subprocess.CalledProcessError:
            self.log_result(
                "Docker Compose",
                False,
                "docker-compose command failed"
            )
            return False
        except FileNotFoundError:
            self.log_result(
                "Docker Compose",
                False,
                "docker-compose not found in PATH"
            )
            return False
    
    def verify_project_structure(self) -> bool:
        """Verify project directory structure"""
        print("\n" + "=" * 60)
        print("6. Project Structure")
        print("=" * 60)
        
        required_dirs = [
            'src',
            'src/shared',
            'src/data_collection',
            'src/data_collection/collectors',
            'src/data_processing',
            'src/models',
            'src/serving',
            'src/mlops',
            'tests',
            'scripts',
            'config',
            'logs',
        ]
        
        missing_dirs = []
        for dir_path in required_dirs:
            if not Path(dir_path).exists():
                missing_dirs.append(dir_path)
        
        if missing_dirs:
            self.log_result(
                "Directory Structure",
                False,
                f"Missing: {', '.join(missing_dirs[:3])}..."
            )
        else:
            self.log_result(
                "Directory Structure",
                True,
                f"All {len(required_dirs)} required directories present"
            )
        
        # Check key files
        required_files = [
            'pyproject.toml',
            'docker-compose.yml',
            '.env.dev',
            'src/shared/database.py',
            'src/shared/models.py',
        ]
        
        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            self.log_result(
                "Key Files",
                False,
                f"Missing: {', '.join(missing_files)}"
            )
        else:
            self.log_result(
                "Key Files",
                True,
                f"All {len(required_files)} key files present"
            )
        
        return len(missing_dirs) == 0 and len(missing_files) == 0
    
    def print_summary(self):
        """Print verification summary"""
        print("\n" + "=" * 60)
        print("VERIFICATION SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for _, success, _ in self.results if success)
        failed_tests = total_tests - passed_tests
        
        print(f"\nTotal Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Critical Failures: {self.critical_failures}")
        
        if self.critical_failures > 0:
            print("\n✗ CRITICAL ISSUES FOUND - Fix before proceeding")
            print("\nFailed Tests:")
            for name, success, message in self.results:
                if not success:
                    print(f"  ✗ {name}: {message}")
        elif failed_tests > 0:
            print("\n⚠ Some non-critical issues found")
            print("\nFailed Tests:")
            for name, success, message in self.results:
                if not success:
                    print(f"  ✗ {name}: {message}")
        else:
            print("\n✓ ALL TESTS PASSED - Environment ready!")
        
        print("=" * 60)
    
    def run_all_verifications(self) -> bool:
        """Run all verification checks"""
        print("=" * 60)
        print("Bitcoin Sentiment MLOps - Setup Verification")
        print("=" * 60)
        
        self.verify_env_file()
        self.verify_project_structure()
        self.verify_docker_services()
        self.verify_local_postgres()
        self.verify_redis()
        self.verify_neondb()
        
        self.print_summary()
        
        return self.critical_failures == 0


def main():
    verifier = SetupVerifier()
    success = verifier.run_all_verifications()
    
    if success:
        print("\n✓ Ready to proceed with data collector development!")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())