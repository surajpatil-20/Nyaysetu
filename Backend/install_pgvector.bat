@echo off
echo ========================================================
echo Installing pgvector v0.8.6 into PostgreSQL 18 (x64)
echo ========================================================

net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] This script must be run as Administrator!
    echo Please right-click install_pgvector.bat and select "Run as administrator".
    pause
    exit /b 1
)

set "SOURCE_DIR=%~dp0vector-pg18"
set "PG_LIB=C:\Program Files\PostgreSQL\18\lib"
set "PG_EXT=C:\Program Files\PostgreSQL\18\share\extension"

echo Copying vector.dll to %PG_LIB%...
copy /Y "%SOURCE_DIR%\lib\vector.dll" "%PG_LIB%\"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to copy vector.dll
    pause
    exit /b 1
)

echo Copying extension files to %PG_EXT%...
copy /Y "%SOURCE_DIR%\share\extension\*" "%PG_EXT%\"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to copy extension files
    pause
    exit /b 1
)

echo ========================================================
echo pgvector binaries copied successfully!
echo Enabling extension in database 'nyaysetu'...
echo ========================================================

"%~dp0venv\Scripts\python.exe" -c "import psycopg2; conn = psycopg2.connect(dbname='nyaysetu', user='postgres', password='root', host='localhost', port=5432); conn.autocommit=True; cur=conn.cursor(); cur.execute('CREATE EXTENSION IF NOT EXISTS vector;'); print('SUCCESS: Extension vector is now active in nyaysetu!'); cur.close(); conn.close();"

echo ========================================================
echo Done! Please run 'python manage.py migrate' in Backend.
echo ========================================================
pause

