# ALMAENG 🛒

> **AI 쇼핑 도우미 - 자연어 검색 기반 가격 비교 서비스**
>
> 자연어로 원하는 상품을 검색하면 AI가 키워드를 추출하고,
> 11번가 + 네이버 쇼핑에서 실시간 최저가를 찾아주는 서비스

---

## 🎯 Core Features (PRD v2)

| Feature | Description |
|:---|:---|
| 🔍 **자연어 검색** | "피로 회복에 좋은 영양제 추천해줘" → AI가 검색 키워드 추출 |
| 🤖 **Gemini AI** | google-genai SDK (gemini-2.0-flash) 기반 키워드 추출 |
| 💰 **가격 비교** | 11번가 + 네이버 쇼핑 실시간 최저가 비교 |
| ⚖️ **상품 비교** | 최대 4개 상품 사양 비교 |
| 💳 **Toss Pay** | 원클릭 결제 (Toss Payments V2 Widget) |

---

## 🛠️ Tech Stack

| Layer | Technologies |
|:---|:---|
| **Backend** | Python 3.12+, Django Ninja, Pydantic |
| **Frontend** | HTMX + Alpine.js + Tailwind CSS (Mobile First) |
| **AI** | Google Gemini 2.0 Flash (google-genai SDK) |
| **Shopping APIs** | 11번가 Open API, 네이버 쇼핑 검색 API |
| **Payments** | Toss Payments V2 Widget SDK |
| **i18n** | 🇰🇷 한국어 |

---

## 📁 Domain Structure (PRD v2)

```
backend/domains/
├── search/                 # 🔍 자연어 검색 (핵심)
│   ├── state/              # DB 모델 (검색 기록)
│   ├── logic/              # 검색 서비스
│   └── pages/              # 검색 UI
│       └── search/
│
├── compare/                # ⚖️ 상품 비교
│   ├── state/
│   ├── logic/
│   └── pages/
│       └── compare/
│
├── billing/                # 💳 결제 (Toss Pay)
│   ├── state/              # Order, Payment 모델
│   ├── logic/
│   └── pages/
│       └── checkout/
│
├── integrations/           # 🔌 외부 API 클라이언트
│   ├── gemini/             # Google Gemini AI
│   ├── naver/              # 네이버 쇼핑 API
│   ├── elevenst/           # 11번가 Open API
│   └── tosspayments/       # Toss Payments
│
└── base/                   # 기본 도메인
    ├── core/               # 홈 (→ 검색으로 리다이렉트)
    ├── accounts/           # 사용자 인증
    └── health/             # 헬스체크
```

---

## 🚀 Quick Start

```bash
# 의존성 설치
just setup

# 개발 서버 시작
just dev
# → http://127.0.0.1:8000
```

---

## 🔗 Key URLs (PRD v2)

| Path | Description |
|:---|:---|
| `/` | 홈 (검색 페이지로 리다이렉트) |
| `/search/` | 🔍 자연어 검색 |
| `/search/?q=피로회복 영양제` | 검색 결과 |
| `/compare/` | ⚖️ 상품 비교 |
| `/checkout/` | 💳 결제 |
| `/checkout/success/` | 결제 성공 |
| `/checkout/fail/` | 결제 실패 |

---

## 🔧 Environment Variables

```env
# AI (google-genai SDK)
GEMINI_API_KEY=your-gemini-api-key

# 11번가 Open API
ELEVENST_API_KEY=your-11st-api-key

# 네이버 쇼핑 API
NAVER_CLIENT_ID=your-naver-client-id
NAVER_CLIENT_SECRET=your-naver-client-secret

# Toss Payments
TOSS_CLIENT_KEY=test_ck_xxx
TOSS_SECRET_KEY=test_sk_xxx
```

---

## 🎨 UI Features

- 📱 **모바일 퍼스트** - 반응형 디자인
- ⚡ **HTMX** - SPA 느낌의 빠른 인터랙션
- 🌙 **다크/라이트 모드** - 테마 토글

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

---

## 📦 Active Domains (PRD v2)

- **search** - 🔍 자연어 검색
- **compare** - ⚖️ 상품 비교
- **billing** - 💳 결제
- **integrations** - 🔌 외부 API
  - gemini (AI)
  - naver (쇼핑 API)
  - elevenst (11번가 API)
  - tosspayments (결제)
- **base > core** - 홈
- **base > accounts** - 인증
- **base > health** - 헬스체크

---

## 📜 License

MIT License © 2026 xid
