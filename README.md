# ALMAENG 🛒

> **AI 쇼핑 도우미 - 자연어로 검색하면 최저가를 찾아주는 서비스**
>
> "피로 회복에 좋은 거 추천해줘" → AI가 키워드 추출 → 쿠팡/네이버/11번가 최저가 비교

---

## 🎯 Core Features

| Feature | Description |
|:---|:---|
| 🔍 **Natural Language Search** | "겨울에 따뜻한 이어폰" → AI가 키워드 추출 |
| 🤖 **Gemini AI** | 자연어 → 검색 키워드 변환 (gemini-2.0-flash) |
| 💰 **Price Comparison** | 네이버, 11번가 실시간 최저가 비교 |
| ❤️ **Wishlist** | 세션 기반 찜 (로그인 불필요) |

---

## 🛠️ Tech Stack

| Layer | Technologies |
|:---|:---|
| **Backend** | Python 3.12+, Django Ninja, Pydantic |
| **Frontend** | HTMX + Alpine.js + Tailwind CSS (Mobile First) |
| **AI** | Google Gemini 2.0 Flash (google-genai SDK) |
| **Shopping APIs** | 쿠팡 파트너스, 11번가 Open API, 네이버 쇼핑 검색 API |
| **Payments** | Toss Payments V2 Widget SDK |
| **i18n** | 🇰🇷 Korean |

---

## 📁 Domain Structure (PRD v2)

```
backend/domains/
├── search/                 # 🔍 Natural Language Search (Core)
│   ├── state/              # DB Models (Search History)
│   ├── logic/              # Search Services
│   └── pages/              # Search UI
│       └── search/
│
├── compare/                # ⚖️ Product Comparison
│   ├── state/
│   ├── logic/
│   └── pages/
│       └── compare/
│
├── billing/                # 💳 Payment (Toss Pay)
│   ├── state/              # Order, Payment Models
│   ├── logic/
│   └── pages/
│       └── checkout/
│
├── integrations/           # 🔌 External API Clients
│   ├── gemini/             # Google Gemini AI
│   ├── coupang/            # Coupang Partners API
│   ├── naver/              # Naver Shopping API
│   ├── elevenst/           # 11st Open API
│   └── tosspayments/       # Toss Payments
│
└── base/                   # Base Domains
    ├── core/               # Home (→ Redirects to Search)
    ├── accounts/           # User Authentication
    └── health/             # Health Check
```

---

## 🚀 Quick Start

```bash
# Install dependencies
just setup

# Start development server
just dev
# → http://127.0.0.1:8000
```

---

## 🔗 Key URLs

| Path | Description |
|:---|:---|
| `/` | 🔍 Search Page (Home) |
| `/?q=비타민` | Search Results |
| `/wishlist/` | ❤️ Wishlist |
| `/chat/` | 🤖 AI Chatbot |
| `/admin/` | 🔧 Admin Panel |

---

## 🔧 Environment Variables

```env
# AI
GEMINI_API_KEY=your-gemini-api-key

# Shopping APIs
NAVER_CLIENT_ID=your-naver-client-id
NAVER_CLIENT_SECRET=your-naver-client-secret
ELEVENST_API_KEY=your-11st-api-key
COUPANG_ACCESS_KEY=your-coupang-access-key
COUPANG_SECRET_KEY=your-coupang-secret-key
```

---

## 🎨 UI Features

- 📱 **Mobile First** - Responsive design (19.5:9)
- ⚡ **HTMX** - Fast interactions with SPA-like feel
- 🎨 **Light Mode Only** - Toss Design System

---

## 🚀 Deployment (Infrastructure-First)

> **"Walking Skeleton"** — Build deployment infrastructure first, then fill in business logic

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
just status        # Check deployed server status
just deploy-info   # Print deployment pipeline info
just logs-remote   # Guide to Coolify log dashboard
```

---

## 📦 Active Domains (Minimal)

- **search** - 🔍 Natural Language Search (Core)
- **wishlist** - ❤️ Session-based Wishlist
- **ai/service/chatbot** - 🤖 AI Chatbot
- **integrations** - 🔌 External APIs
  - gemini (AI)
  - coupang (Manual DB)
  - naver (Shopping API)
  - elevenst (11st API)
- **base > core** - Policies
- **base > health** - Health Check
- **features > seo** - SEO

---

## 📜 License

MIT License © 2026 xid
