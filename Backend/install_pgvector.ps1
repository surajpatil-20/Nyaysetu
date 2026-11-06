# PowerShell script to install pgvector for PostgreSQL 18
# Run in Administrator PowerShell window

$ErrorActionPreference = "Stop"
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Installing pgvector v0.8.6 into PostgreSQL 18" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

$sourceDir = "$PSScriptRoot\vector-pg18"
$pgLib = "C:\Program Files\PostgreSQL\18\lib"
$pgExt = "C:\Program Files\PostgreSQL\18\share\extension"

Copy-Item "$sourceDir\lib\vector.dll" $pgLib -Force
Write-Host "✓ Copied vector.dll -> $pgLib" -ForegroundColor Green

Copy-Item "$sourceDir\share\extension\*" $pgExt -Force
Write-Host "✓ Copied extension files -> $pgExt" -ForegroundColor Green

Write-Host "`nEnabling extension in PostgreSQL database 'nyaysetu'..." -ForegroundColor Cyan
& "$PSScriptRoot\venv\Scripts\python.exe" -c "import psycopg2; conn = psycopg2.connect(dbname='nyaysetu', user='postgres', password='root', host='localhost', port=5432); conn.autocommit=True; cur=conn.cursor(); cur.execute('CREATE EXTENSION IF NOT EXISTS vector;'); print('SUCCESS: Extension vector is active in nyaysetu!'); cur.close(); conn.close();"

Write-Host "`nDone! Run: python manage.py migrate" -ForegroundColor Green

