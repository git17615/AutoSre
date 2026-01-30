Write-Host "🔍 Checking AutoSRE Setup..." -ForegroundColor Cyan

# 1. Check Docker
Write-Host "`n1. Docker Status:" -ForegroundColor Yellow
docker version 2>&1 | Select-String -Pattern "Server:" -Context 0,2

# 2. Check containers
Write-Host "`n2. Running Containers:" -ForegroundColor Yellow
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# 3. Check port 8000
Write-Host "`n3. Checking Port 8000..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 3 -ErrorAction Stop
    Write-Host "✅ Backend is running on port 8000" -ForegroundColor Green
    Write-Host "   Response: $($response.Content)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Backend not reachable on port 8000" -ForegroundColor Red
}

# 4. Check port 3000
Write-Host "`n4. Checking Port 3000..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 3 -ErrorAction Stop
    Write-Host "✅ Frontend is running on port 3000" -ForegroundColor Green
} catch {
    Write-Host "❌ Frontend not reachable on port 3000" -ForegroundColor Red
}

# 5. Summary
Write-Host "`n📊 SUMMARY:" -ForegroundColor Cyan
Write-Host "   Dashboard: http://localhost:3000" -ForegroundColor White
Write-Host "   API: http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor White
