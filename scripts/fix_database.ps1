# PostgreSQL 데이터베이스 문제 해결 스크립트 (PowerShell)

Write-Host "🔍 Docker 컨테이너 상태 확인..." -ForegroundColor Cyan
docker ps -a --filter "name=almaeng"

Write-Host ""
Write-Host "🛑 컨테이너 중지 및 볼륨 삭제..." -ForegroundColor Yellow
docker compose down -v

Write-Host ""
Write-Host "🧹 남은 볼륨 확인..." -ForegroundColor Cyan
docker volume ls | Select-String "almaeng"

Write-Host ""
Write-Host "🚀 컨테이너 재시작..." -ForegroundColor Green
docker compose up -d postgres redis

Write-Host ""
Write-Host "⏳ PostgreSQL이 준비될 때까지 대기 (최대 30초)..." -ForegroundColor Yellow
$maxWait = 30
$waited = 0
while ($waited -lt $maxWait) {
    $result = docker compose exec -T postgres pg_isready -U almaeng_user 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ PostgreSQL이 준비되었습니다!" -ForegroundColor Green
        break
    }
    Write-Host "   대기 중... ($($waited + 1)/$maxWait)" -ForegroundColor Gray
    Start-Sleep -Seconds 1
    $waited++
}

Write-Host ""
Write-Host "📊 컨테이너 상태:" -ForegroundColor Cyan
docker compose ps

Write-Host ""
Write-Host "✅ 완료! 이제 'just migrate'를 실행하세요." -ForegroundColor Green
