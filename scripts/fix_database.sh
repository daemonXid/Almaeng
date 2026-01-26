#!/bin/bash
# PostgreSQL 데이터베이스 문제 해결 스크립트

echo "🔍 Docker 컨테이너 상태 확인..."
docker ps -a --filter "name=almaeng"

echo ""
echo "🛑 컨테이너 중지 및 삭제..."
docker compose down -v

echo ""
echo "🧹 남은 볼륨 확인..."
docker volume ls | grep almaeng

echo ""
echo "🚀 컨테이너 재시작..."
docker compose up -d postgres redis

echo ""
echo "⏳ PostgreSQL이 준비될 때까지 대기 (최대 30초)..."
for i in {1..30}; do
    if docker compose exec -T postgres pg_isready -U almaeng_user > /dev/null 2>&1; then
        echo "✅ PostgreSQL이 준비되었습니다!"
        break
    fi
    echo "   대기 중... ($i/30)"
    sleep 1
done

echo ""
echo "📊 컨테이너 상태:"
docker compose ps

echo ""
echo "✅ 완료! 이제 'just migrate'를 실행하세요."
