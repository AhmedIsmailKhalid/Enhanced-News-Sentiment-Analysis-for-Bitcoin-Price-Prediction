@echo off
echo Creating Bitcoin Sentiment MLOps Project Directory Structure...
echo.

REM Root level directories
mkdir .github\workflows 2>nul
mkdir config\settings 2>nul
mkdir data\collected 2>nul
mkdir data\ml_datasets 2>nul
mkdir docs 2>nul
mkdir frontend\public 2>nul
mkdir frontend\src\components\Dashboard 2>nul
mkdir frontend\src\components\Charts 2>nul
mkdir frontend\src\components\Common 2>nul
mkdir frontend\src\hooks 2>nul
mkdir frontend\src\services 2>nul
mkdir frontend\src\styles 2>nul
mkdir frontend\src\utils 2>nul
mkdir logs 2>nul
mkdir models\experiments 2>nul
mkdir models\saved_models\VADER 2>nul
mkdir models\saved_models\FinBERT 2>nul
mkdir models\saved_models\Ensemble 2>nul
mkdir monitoring\grafana_dashboards 2>nul
mkdir scripts\development 2>nul
mkdir scripts\data_collection 2>nul
mkdir scripts\model_training 2>nul
mkdir scripts\deployment 2>nul

REM Source code directories
mkdir src\api 2>nul
mkdir src\caching 2>nul
mkdir src\data_collection\collectors 2>nul
mkdir src\data_collection\processors 2>nul
mkdir src\data_collection\validators 2>nul
mkdir src\data_processing\feature_engineering 2>nul
mkdir src\data_processing\text_processing 2>nul
mkdir src\data_processing\validation 2>nul
mkdir src\models\sentiment 2>nul
mkdir src\models\ensemble 2>nul
mkdir src\models\evaluation 2>nul
mkdir src\models\persistence 2>nul
mkdir src\serving 2>nul
mkdir src\mlops 2>nul
mkdir src\monitoring 2>nul
mkdir src\shared 2>nul

REM Test directories
mkdir tests\unit 2>nul
mkdir tests\integration 2>nul
mkdir tests\performance 2>nul

echo.
echo ✓ Directory structure created successfully!
echo.
echo Next steps:
echo 1. Run this script: CREATE_DIRECTORY_STRUCTURE.bat
echo 2. Create __init__.py files in Python packages
echo 3. Set up configuration files
echo.
pause