# ALMAENG 🧬

> **AI-Driven Nutrient Ingredient Comparison & Price Tracker**
>
> 영양제 성분을 AI로 분석하고, 동일 성분 구성의 가성비 제품을 찾아주는 서비스

---

## 🎯 Core Features

| Feature | Description |
|:---|:---|
| 💊 **성분 비교** | 두 영양제의 성분을 비교하여 일치율 표시 |
| 📷 **Vision AI OCR** | 라벨 사진 → 성분 자동 추출 |
| 💰 **가격 추적** | 멀티 플랫폼 실시간 가격 비교 + 히스토리 |
| 🎯 **AI 추천** | 건강 설문 기반 맞춤 영양제 추천 |
| 🛒 **장바구니** | HTMX 실시간 업데이트 |
| 💳 **Toss 결제** | 토스페이먼츠 연동 |

---

## 🛠️ Tech Stack

| Layer | Technologies |
|:---|:---|
| **Backend** | Python 3.12+, Django Ninja, Pydantic |
| **Frontend** | HTMX + Alpine.js + Tailwind CSS |
| **AI** | Google Gemini API |
| **Payments** | Toss Payments |
| **i18n** | 🇰🇷 한국어, 🇺🇸 English |

---

## 📁 Domain Structure

```
backend/domains/
├── ai/
│   ├── service/              # 🐤 AI 챗봇 (캐치)
│   └── recommendations/      # 🎯 AI 추천 + 건강 설문
│
├── base/
│   ├── accounts/             # 👤 사용자 인증
│   ├── core/                 # 🏠 홈
│   └── ...                   # health, analytics, settings 등
│
└── features/
    ├── supplements/          # 💊 영양제 (핵심)
    │   └── pages/            # search, compare, upload
    ├── prices/               # 💰 가격 추적
    ├── cart/                 # 🛒 장바구니
    ├── wishlist/             # ❤️ 찜 목록
    └── payments/             # 💳 Toss 결제
        └── integrations/     # toss.py
```

---

## 🚀 Quick Start

```bash
just setup    # 의존성 설치
just dev      # 개발 서버 → http://127.0.0.1:8000
```

---

## 🔗 Key URLs

| Path | Description |
|:---|:---|
| `/supplements/` | 영양제 검색 |
| `/supplements/compare/` | 성분 비교 |
| `/supplements/upload/` | 라벨 OCR |
| `/recommend/` | AI 추천 |
| `/recommend/quiz/` | 건강 설문 |
| `/cart/` | 장바구니 |
| `/wishlist/` | 찜 목록 |
| `/payments/checkout/` | 결제 |
| `/faq/` | 자주 묻는 질문 |
| `/terms/` | 이용약관 |
| `/privacy/` | 개인정보처리방침 |

---

## 🎨 UI Features

- 🌙 **다크/라이트 모드** - 테마 토글 (좌측 하단)
- 🐤 **AI 챗봇 (캐치)** - 사이드바 팝업 (우측 하단)
- 📱 **반응형 디자인** - 모바일 우선
- ⚡ **HTMX** - SPA 느낌의 빠른 인터랙션

---

## 🔧 Environment Variables

```env
# Toss Payments
TOSS_CLIENT_KEY=test_ck_xxx
TOSS_SECRET_KEY=test_sk_xxx

# AI
GEMINI_API_KEY=xxx
```

---

## 🚀 Deployment (Infrastructure-First)

> **"Walking Skeleton"** — 배포 인프라를 먼저 구축하고, 비즈니스 로직을 채워넣는 전략

### Pipeline Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  git push   │ -> │   GitHub    │ -> │    GHCR     │
│   (main)    │    │   Actions   │    │   (image)   │
└─────────────┘    └─────────────┘    └─────────────┘
                                              │
                                              v
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Cloudflare │ <- │   Hetzner   │ <- │   Coolify   │
│  (CDN/SSL)  │    │   CPX32     │    │   (Deploy)  │
└─────────────┘    └─────────────┘    └─────────────┘
```

### Infrastructure Stack

| Component | Service |
|:---|:---|
| **Registry** | GitHub Container Registry (GHCR) |
| **CI/CD** | GitHub Actions (Build) → Coolify (Deploy) |
| **Server** | Hetzner CPX32 (4 vCPU, 8GB RAM) |
| **CDN/DNS** | Cloudflare |

### Deployment Commands

```bash
just status        # 배포된 서버 상태 확인
just deploy-info   # 배포 파이프라인 정보 출력
just logs-remote   # Coolify 로그 대시보드 안내
```

### Coolify Environment Variables

Coolify Dashboard에서 설정해야 할 필수 환경 변수:

```env
# Production Security
DEBUG=false
SECRET_KEY=<strong-random-key>
ALLOWED_HOSTS=almaeng.daemonxid.com
CSRF_TRUSTED_ORIGINS=https://almaeng.daemonxid.com

# Database (Coolify Internal Network)
POSTGRES_HOST=postgres
DATABASE_URL=postgresql://user:pass@postgres:5432/almaeng

# Redis (Coolify Internal Network)
REDIS_HOST=redis

# External APIs
GEMINI_API_KEY=<your-key>
```

---

<!-- DOMAINS_START -->

### 📦 Active Domains (15)

- **ai > recommendations**
- **base > accounts**
- **base > analytics**
- **base > core**
- **base > health**
- **base > media**
- **base > notifications**
- **base > settings**
- **features > cart**
- **features > marketing**
- **features > payments**
- **features > prices**
- **features > seo**
- **features > supplements**
- **features > wishlist**

<!-- DOMAINS_END -->
