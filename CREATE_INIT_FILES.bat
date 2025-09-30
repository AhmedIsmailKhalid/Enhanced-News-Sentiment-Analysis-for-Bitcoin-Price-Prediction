@echo off
echo Creating __init__.py files for Python packages...
echo.

REM Root src
type nul > src\__init__.py

REM API
type nul > src\api\__init__.py

REM Caching
type nul > src\caching\__init__.py

REM Data collection
type nul > src\data_collection\__init__.py
type nul > src\data_collection\collectors\__init__.py
type nul > src\data_collection\processors\__init__.py
type nul > src\data_collection\validators\__init__.py

REM Data processing
type nul > src\data_processing\__init__.py
type nul > src\data_processing\feature_engineering\__init__.py
type nul > src\data_processing\text_processing\__init__.py
type nul > src\data_processing\validation\__init__.py

REM Models
type nul > src\models\__init__.py
type nul > src\models\sentiment\__init__.py
type nul > src\models\ensemble\__init__.py
type nul > src\models\evaluation\__init__.py
type nul > src\models\persistence\__init__.py

REM Serving
type nul > src\serving\__init__.py

REM MLOps
type nul > src\mlops\__init__.py

REM Monitoring
type nul > src\monitoring\__init__.py

REM Shared
type nul > src\shared\__init__.py

REM Tests
type nul > tests\__init__.py
type nul > tests\unit\__init__.py
type nul > tests\integration\__init__.py
type nul > tests\performance\__init__.py

echo.
echo ✓ All __init__.py files created!
echo.
pause