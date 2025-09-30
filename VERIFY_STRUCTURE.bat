@echo off
echo Verifying Directory Structure...
echo.

set ERROR=0

REM Check critical directories
if not exist ".github\workflows" (
    echo ✗ Missing: .github\workflows
    set ERROR=1
) else (
    echo ✓ .github\workflows
)

if not exist "src\data_collection\collectors" (
    echo ✗ Missing: src\data_collection\collectors
    set ERROR=1
) else (
    echo ✓ src\data_collection\collectors
)

if not exist "src\data_processing\validation" (
    echo ✗ Missing: src\data_processing\validation
    set ERROR=1
) else (
    echo ✓ src\data_processing\validation
)

if not exist "src\models\sentiment" (
    echo ✗ Missing: src\models\sentiment
    set ERROR=1
) else (
    echo ✓ src\models\sentiment
)

if not exist "src\serving" (
    echo ✗ Missing: src\serving
    set ERROR=1
) else (
    echo ✓ src\serving
)

if not exist "src\mlops" (
    echo ✗ Missing: src\mlops
    set ERROR=1
) else (
    echo ✓ src\mlops
)

if not exist "tests\unit" (
    echo ✗ Missing: tests\unit
    set ERROR=1
) else (
    echo ✓ tests\unit
)

if not exist "frontend\src" (
    echo ✗ Missing: frontend\src
    set ERROR=1
) else (
    echo ✓ frontend\src
)

echo.
if %ERROR%==0 (
    echo ✓ All critical directories present!
) else (
    echo ✗ Some directories missing. Run CREATE_DIRECTORY_STRUCTURE.bat
)
echo.
pause