# 알맹AI 배포 가이드

> **Coolify 배포 전용 가이드**

---

## 🚀 Coolify 환경변수 설정

### 📋 복사-붙여넣기용 (아래 전체 복사)

```env
# ============================================
# Django Core
# ============================================
DEBUG=false
SECRET_KEY=<50자_이상_랜덤_문자열>

# ============================================
# Production Security
# ============================================
ALLOWED_HOSTS=almaeng.yourdomain.com,yourdomain.com
CSRF_TRUSTED_ORIGINS=https://almaeng.yourdomain.com,https://yourdomain.com
SECURE_SSL_REDIRECT=true

# ============================================
# AI (Google Gemini)
# ============================================
GEMINI_API_KEY=

# ============================================
# 쇼핑 API (External)
# ============================================
# Coupang Partners (15만원 달성 후)
COUPANG_ACCESS_KEY=
COUPANG_SECRET_KEY=

# Naver Shopping
NAVER_CLIENT_ID=
NAVER_CLIENT_SECRET=

# 11번가
ELEVENST_API_KEY=

# ============================================
# OAuth (Toss Login)
# ============================================
TOSS_OPENID_CLIENT_ID=
TOSS_OPENID_CLIENT_SECRET=

# ============================================
# Payments (Toss Payments)
# ============================================
TOSS_CLIENT_KEY=
TOSS_SECRET_KEY=

# ============================================
# Monitoring (Optional)
# ============================================
SENTRY_DSN=
LOGFIRE_TOKEN=
```

---

## ⚠️ Coolify에서 설정하지 않는 것들

Coolify가 자동으로 연결하므로 **설정하지 마세요:**

- ❌ `POSTGRES_*` (PostgreSQL 관련)
- ❌ `REDIS_*` (Redis 관련)
- ❌ `APP_PORT` (Coolify가 자동 할당)
- ❌ `DJANGO_SUPERUSER_*` (로컬 개발용)

---

## 📝 설정 값 채우기

### 1. SECRET_KEY 생성
```python
# Python 터미널에서 실행
import secrets
print(secrets.token_urlsafe(50))
```

### 2. ALLOWED_HOSTS
```env
# 실제 도메인으로 변경
ALLOWED_HOSTS=almaeng.daemonx.cc
CSRF_TRUSTED_ORIGINS=https://almaeng.daemonx.cc
```

### 3. API 키 발급

| 서비스 | 발급 URL | 필수 여부 |
|:---|:---|:---:|
| **Gemini AI** | https://aistudio.google.com/apikey | ✅ 필수 |
| **Naver API** | https://developers.naver.com/apps/ | ✅ 필수 |
| **11번가 API** | https://openapi.11st.co.kr/ | ✅ 필수 |
| **Coupang Partners** | https://partners.coupang.com/ | 🔜 15만원 달성 후 |
| **Toss OpenID** | https://developers.toss.im/ | ✅ 필수 |
| **Toss Payments** | https://developers.tosspayments.com/ | 선택 |
| **Sentry** | https://sentry.io/ | 선택 |

---

## 🐳 Coolify 배포 절차

### 1. Coolify 프로젝트 생성
1. Coolify Dashboard → New Resource
2. **Docker Image** 선택
3. Image: `ghcr.io/yourusername/almaeng:latest`

### 2. 서비스 연결
1. **PostgreSQL** 추가
   - Coolify → Add Resource → PostgreSQL
   - Database: `almaeng_db`
   - User: 자동 생성

2. **Redis** 추가
   - Coolify → Add Resource → Redis
   - 기본 설정 사용

3. **앱과 연결**
   - App Settings → Environment Variables
   - Coolify가 자동으로 `DATABASE_URL`, `REDIS_URL` 주입

### 3. 환경변수 설정
1. App → Environment Variables
2. 위의 "복사-붙여넣기용" 섹션 전체 복사
3. 값 채우기

### 4. 배포
1. GitHub Push → `main` branch
2. GitHub Actions가 자동으로 빌드 → GHCR에 Push
3. Coolify Webhook 트리거 → 자동 배포
4. Health Check (`/health/`) 확인

---

## 🔍 배포 후 확인사항

### 필수 체크
- [ ] https://yourdomain.com/ 접속 확인
- [ ] https://yourdomain.com/admin/ 접속 확인
- [ ] https://yourdomain.com/health/ → `{"status": "ok"}`
- [ ] 검색 기능 작동 확인
- [ ] 계산기 기능 작동 확인

### API 연동 확인
- [ ] Gemini AI 챗봇 응답 확인
- [ ] Naver 쇼핑 검색 결과 확인
- [ ] 11번가 검색 결과 확인
- [ ] Toss 로그인 작동 확인

---

## 🆘 문제 해결

### "500 Internal Server Error"
1. Coolify Logs 확인
2. `SECRET_KEY` 설정 확인
3. `DATABASE_URL` 자동 주입 확인

### "403 Forbidden"
```env
# ALLOWED_HOSTS에 도메인 추가 확인
ALLOWED_HOSTS=yourdomain.com,*.yourdomain.com

# CSRF_TRUSTED_ORIGINS 확인
CSRF_TRUSTED_ORIGINS=https://yourdomain.com
```

### "Connection Refused (DB)"
- Coolify에서 PostgreSQL 서비스와 앱이 연결되었는지 확인
- Network 설정 확인

---

## 📊 성능 최적화 (배포 후)

### Static Files
```bash
# Collectstatic (Coolify 빌드 시 자동)
python main.py collectstatic --noinput
```

### DB 최적화
```sql
-- PostgreSQL 인덱스 확인
python main.py dbshell
\di
```

### Redis 캐싱
- 검색 결과: 5분 캐싱
- Rate Limiting: 1분 윈도우

---

**배포 준비 완료! 🚀**
