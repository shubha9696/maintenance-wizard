# Maintenance Wizard - Startup Script
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Maintenance Wizard - Tata Steel AI" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "backend/main.py")) {
    Write-Host "ERROR: Please run this script from the hackathon root directory." -ForegroundColor Red
    exit 1
}

# Generate data if not present
if (-not (Test-Path "backend/data/generated/equipment.json")) {
    Write-Host "[1/3] Generating synthetic data..." -ForegroundColor Yellow
    python -X utf8 backend/data/generate_synthetic_data.py
} else {
    Write-Host "[1/3] Synthetic data already exists." -ForegroundColor Green
}

# Start Backend
Write-Host "[2/3] Starting FastAPI backend on http://localhost:8000 ..." -ForegroundColor Yellow
$backend = Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "backend.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000" -PassThru -NoNewWindow

Start-Sleep -Seconds 3

# Start Frontend
Write-Host "[3/3] Starting Next.js frontend on http://localhost:3000 ..." -ForegroundColor Yellow
Push-Location frontend
$frontend = Start-Process -FilePath "npm.cmd" -ArgumentList "run", "dev" -PassThru -NoNewWindow
Pop-Location

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Maintenance Wizard is running!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Frontend:  http://localhost:3000" -ForegroundColor White
Write-Host "  Backend:   http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs:  http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop all services." -ForegroundColor Gray
Write-Host ""

# Wait for either process to exit
try {
    Wait-Process -Id $backend.Id
} finally {
    Write-Host "Shutting down..." -ForegroundColor Yellow
    if ($frontend -and -not $frontend.HasExited) { Stop-Process -Id $frontend.Id -Force -ErrorAction SilentlyContinue }
    if ($backend -and -not $backend.HasExited) { Stop-Process -Id $backend.Id -Force -ErrorAction SilentlyContinue }
}
