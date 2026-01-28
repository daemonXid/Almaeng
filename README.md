# ALMAENG 🛒

> **AI 쇼핑 도우미 - 자연어로 검색하면 최저가를 찾아주는 서비스**
>
> "피로 회복에 좋은 거 추천해줘" → AI가 키워드 추출 → 쿠팡/네이버/11번가 최저가 비교

**🌐 배포된 사이트**: [almaeng.daemonx.cc](https://almaeng.daemonx.cc)

---

## 🎯 핵심 기능

| Feature | Description |
|:---|:---|
| 🔍 **자연어 검색** | "겨울에 따뜻한 이어폰" → AI가 키워드 추출 |
| 🤖 **Gemini AI** | 자연어 → 검색 키워드 변환 (gemini-2.0-flash) |
| 💰 **가격 비교** | 네이버, 11번가 실시간 최저가 비교 |
| ❤️ **찜하기** | 세션 기반 위시리스트 (로그인 불필요) |
| 💬 **AI 챗봇** | 상품 추천 및 상담 |

---

## 🛠️ 기술 스택

| Layer | Technologies |
|:---|:---|
| **Backend** | Python 3.12, Django 5.1, Django Ninja Extra |
| **Frontend** | HTMX + Alpine.js + Tailwind CSS (Mobile First) |
| **AI** | Google Gemini 2.0 Flash (google-genai SDK) |
| **Shopping APIs** | 쿠팡 파트너스, 11번가 Open API, 네이버 쇼핑 검색 API |
| **Database** | PostgreSQL + Redis |
| **Server** | Granian (Prod), Uvicorn (Dev) |

---

## 📁 도메인 구조 (DAEMON 아키텍처)

```
backend/domains/
├── search/                 # 🔍 자연어 검색 (핵심)
│   ├── interface.py        # Public API
│   ├── state/              # DB Models (검색 이력, 상품 캐시)
│   ├── logic/              # 검색 서비스 (순수 함수)
│   └── pages/search/       # 검색 UI
│
├── wishlist/               # ❤️ 찜하기
│   ├── interface.py        # Public API
│   ├── models.py           # 찜 목록, 가격 알림
│   ├── services.py         # 찜 로직
│   └── pages/index/        # 찜 목록 UI
│
├── ai/service/chatbot/     # 🤖 AI 챗봇
│   ├── interface.py        # Public API
│   ├── gemini_service.py   # Gemini 클라이언트
│   ├── models.py           # 채팅 이력
│   └── pages/chat/         # 챗봇 UI
│
├── integrations/           # 🔌 외부 API 클라이언트
│   ├── gemini/             # Google Gemini AI
│   ├── coupang/            # 쿠팡 파트너스 API
│   ├── naver/              # 네이버 쇼핑 API
│   └── elevenst/           # 11번가 Open API
│
├── features/               # 🎨 기능 도메인
│   └── seo/                # SEO (메타태그, 사이트맵)
│
└── base/                   # 기본 도메인
    ├── core/               # 홈, 정책 페이지
    └── health/             # 헬스체크
```

---

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# .env 파일 생성
cp .env.example .env

# API 키 설정 (.env 파일 편집)
# - GEMINI_API_KEY (필수)
# - NAVER_CLIENT_ID, NAVER_CLIENT_SECRET (필수)
# - ELEVENST_API_KEY (선택)
# - COUPANG_ACCESS_KEY, COUPANG_SECRET_KEY (선택)
```

### 2. 개발 서버 실행

```bash
# 의존성 설치 + DB 마이그레이션 + 서버 실행
just setup

# 개발 서버 시작
just dev
# → http://127.0.0.1:8000
```

### 3. 주요 명령어

```bash
just dev          # 개발 서버 실행
just test         # 테스트 실행
just lint         # 코드 검사
just migrate      # DB 마이그레이션
just shell        # Django Shell Plus
```

---

## 🔗 주요 URL

| Path | Description |
|:---|:---|
| `/` | 🔍 검색 페이지 (홈) |
| `/?q=비타민` | 검색 결과 |
| `/wishlist/` | ❤️ 찜 목록 |
| `/chat/` | 🤖 AI 챗봇 |
| `/admin/` | 🔧 관리자 패널 |
| `/health/status/` | 📊 헬스체크 |

---

## 🔧 환경 변수

### 필수 설정

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=True

# AI (필수)
GEMINI_API_KEY=your-gemini-api-key

# 쇼핑 API (필수)
NAVER_CLIENT_ID=your-naver-client-id
NAVER_CLIENT_SECRET=your-naver-client-secret
```

### 선택 설정

```env
# 11번가 API (선택)
ELEVENST_API_KEY=your-11st-api-key

# 쿠팡 파트너스 (선택 - 수동 DB 사용 중)
COUPANG_ACCESS_KEY=your-coupang-access-key
COUPANG_SECRET_KEY=your-coupang-secret-key
COUPANG_PARTNER_ID=your-partner-id

# Database (선택 - 기본값: SQLite)
DATABASE_URL=postgresql://user:pass@localhost:5432/almaeng

# Redis (선택 - 기본값: 캐시 비활성화)
REDIS_URL=redis://localhost:6379/0
```

---

## 🎨 UI 특징

- 📱 **모바일 우선** - 반응형 디자인 (19.5:9 비율)
- ⚡ **HTMX** - SPA 같은 빠른 인터랙션
- 🎨 **Toss 디자인 시스템** - 라이트 모드 전용
- 🧭 **하단 네비게이션** - 모바일 최적화
- 🎯 **Progressive Web App** - 오프라인 지원

---

## 🏗️ DAEMON 아키텍처 원칙

### 1. Vertical Slicing
- 기능별 도메인 분리 (레이어 기반 X)
- 각 도메인은 독립적으로 배포 가능

### 2. Interface Pattern
- 모든 도메인 간 통신은 `interface.py`를 통해서만
- 내부 구현 변경 시 외부 영향 최소화

### 3. Stateful/Stateless 분리
- `state/`: DB Owner (Django Models, Migrations)
- `logic/`: Processor (순수 함수, Pydantic Schemas)

### 4. Immutability
- 모든 `logic/` 내부 데이터는 불변 (frozen=True)
- Side-effect 제거, 디버깅 용이

### 5. No ForeignKey Across Domains
- 도메인 간 참조는 IntegerField만 사용
- 독립적 배포 및 마이그레이션 충돌 방지

---

## 🚀 배포 구조

### 파이프라인

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

### 인프라 스택

| Component | Service |
|:---|:---|
| **컨테이너 레지스트리** | GitHub Container Registry (GHCR) |
| **CI/CD** | GitHub Actions (빌드) → Coolify (배포) |
| **서버** | Hetzner CPX32 (4 vCPU, 8GB RAM) |
| **CDN/DNS** | Cloudflare |

### 배포 명령어

```bash
just status        # 배포된 서버 상태 확인
just deploy-info   # 배포 파이프라인 정보 출력
just logs-remote   # Coolify 로그 대시보드 안내
```

---

## 📦 활성 도메인

| 도메인 | 설명 | 상태 |
|:---|:---|:---|
| **search** | 🔍 자연어 검색 (핵심) | ✅ 활성 |
| **wishlist** | ❤️ 세션 기반 찜하기 | ✅ 활성 |
| **ai/service/chatbot** | 🤖 AI 챗봇 | ✅ 활성 |
| **integrations** | 🔌 외부 API 클라이언트 | ✅ 활성 |
| **features/seo** | 📊 SEO (메타태그, 사이트맵) | ✅ 활성 |
| **base/core** | 🏠 홈, 정책 페이지 | ✅ 활성 |
| **base/health** | 💚 헬스체크 | ✅ 활성 |

---

## 🧪 테스트

```bash
# 전체 테스트 실행
just test

# 특정 도메인 테스트
pytest backend/domains/search/

# 커버리지 확인
pytest --cov=backend
```

---

## 🔐 앱인토스 정책 준수

### ✅ 외부 링크 허용 (예외 조항 4-2-③)
> "각 제품을 소개·추천 후 최저가 구매 플랫폼으로 이동"

**구현 사항:**
- ℹ️ 홈페이지에 "실제 구매는 외부 쇼핑몰에서 진행" 명시
- 💰 쿠팡 파트너스 수수료 고지
- ↗ 상품 링크에 외부 이동 아이콘

### ✅ 생성형 AI 고지
- ✨ "Powered by Gemini AI" 배지
- ⚠️ "생성형 AI 기반 추천 시스템" 명시
- 📜 인공지능기본법 제15조 준수

---

## 📊 프로젝트 통계

| 항목 | 수치 |
|:---|:---|
| **Python 버전** | 3.12 |
| **Django 버전** | 5.1 |
| **활성 도메인** | 7개 |
| **API 통합** | 4개 (Gemini, Naver, 11st, Coupang) |
| **인증 시스템** | 세션 기반 (로그인 불필요) |

---

## 🛒 쿠팡 파트너스 전략

### 현재: 수동 DB 관리
- Admin 패널에서 수동으로 상품 등록
- `CoupangManualProduct` 모델 사용
- 파트너스 링크 직접 관리

### 향후: API 자동화 (15만원 달성 후)
- 쿠팡 파트너스 API 연동
- 실시간 상품 검색 및 가격 업데이트
- HMAC SHA256 인증

---

## 📚 참고 문서

- [PROJECT_OVERVIEW.md](./PROJECT_OVERVIEW.md) - 프로젝트 상세 설명
- [.env.example](./.env.example) - 환경 변수 예시
- [Justfile](./Justfile) - 개발 명령어 모음

---

## 📜 라이선스

MIT License © 2026 xid

---

## 🤝 기여

이슈 및 PR 환영합니다!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
