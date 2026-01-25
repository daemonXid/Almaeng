# ALMAENG 🛒

> **AI Shopping Assistant - Natural Language Search Based Price Comparison Service**
>
> Search for products using natural language, AI extracts keywords,
> and finds real-time lowest prices from 11st + Naver Shopping

---

## 🎯 Core Features (PRD v2)

| Feature | Description |
|:---|:---|
| 🔍 **Natural Language Search** | "피로 회복에 좋은 영양제 추천해줘" → AI extracts search keywords |
| 🤖 **Gemini AI** | Keyword extraction using google-genai SDK (gemini-2.0-flash) |
| 💰 **Price Comparison** | Real-time lowest price comparison from 11st + Naver Shopping |
| ⚖️ **Product Comparison** | Compare up to 4 products specifications |
| 💳 **Toss Pay** | One-click payment (Toss Payments V2 Widget) |

---

## 🛠️ Tech Stack

| Layer | Technologies |
|:---|:---|
| **Backend** | Python 3.12+, Django Ninja, Pydantic |
| **Frontend** | HTMX + Alpine.js + Tailwind CSS (Mobile First) |
| **AI** | Google Gemini 2.0 Flash (google-genai SDK) |
| **Shopping APIs** | 11번가 Open API, 네이버 쇼핑 검색 API |
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

## 🔗 Key URLs (PRD v2)

| Path | Description |
|:---|:---|
| `/` | Home (Redirects to search page) |
| `/search/` | 🔍 Natural Language Search |
| `/search/?q=피로회복 영양제` | Search Results |
| `/compare/` | ⚖️ Product Comparison |
| `/checkout/` | 💳 Payment |
| `/checkout/success/` | Payment Success |
| `/checkout/fail/` | Payment Failed |

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

- 📱 **Mobile First** - Responsive design
- ⚡ **HTMX** - Fast interactions with SPA-like feel
- 🌙 **Dark/Light Mode** - Theme toggle

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

## 📦 Active Domains (PRD v2)

- **search** - 🔍 Natural Language Search
- **compare** - ⚖️ Product Comparison
- **billing** - 💳 Payment
- **integrations** - 🔌 External APIs
  - gemini (AI)
  - naver (Shopping API)
  - elevenst (11st API)
  - tosspayments (Payment)
- **base > core** - Home
- **base > accounts** - Authentication
- **base > health** - Health Check

---

## 📜 License

MIT License © 2026 xid
