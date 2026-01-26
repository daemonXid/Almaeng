# 알맹AI - AI 쇼핑 도우미

> **Mobile-First AI Shopping Assistant**  
> Toss 디자인 시스템 + DAEMON 아키텍처 + 앱인토스 준비

---

## 🎯 프로젝트 개요

**알맹AI**는 Gemini AI 기반 최저가 쇼핑 비교 서비스입니다.

### 핵심 기능
1. **AI 쇼핑 상담** - Gemini AI 기반 자연어 상품 추천
2. **가격 비교** - 쿠팡, 네이버, 11번가 실시간 연동
3. **바디 계산기** - BMR/TDEE 계산 및 영양소 추천
4. **찜하기** - 가격 알림 기능

### 비즈니스 모델
- 쿠팡 파트너스 수수료
- 앱인토스(Toss 미니앱) 출시 예정

---

## 🏗️ 아키텍처 특징 (DAEMON Pattern)

### 1. Vertical Slicing Architecture

**Feature-based, not Layer-based**

```
backend/domains/
├── calculator/              # 바디 계산기 도메인
│   ├── interface.py         # 🔑 Public API (외부 노출)
│   ├── logic/               # Stateless (순수 함수)
│   │   ├── schemas.py       # Pydantic (frozen=True)
│   │   └── services.py      # Pure functions
│   └── pages/calculator/    # Views + Templates (colocated)
│       ├── views.py
│       └── calculator.html
│
├── search/                  # 검색 도메인
│   ├── interface.py         # 🔑 Public API
│   ├── state/               # Stateful (DB Owner)
│   │   ├── models.py        # Django Models
│   │   ├── migrations/      # DB 마이그레이션
│   │   └── interface.py     # DB operations only
│   ├── logic/               # Stateless (순수 함수)
│   │   ├── schemas.py       # Pydantic (frozen=True)
│   │   └── services.py      # Transform, Aggregate
│   ├── pages/search/        # Views + Templates
│   └── admin.py             # Admin UI
│
└── ai/service/chatbot/      # AI 서비스 (독립)
    ├── interface.py         # 🔑 Public API
    ├── gemini_service.py    # Gemini Client (Singleton)
    └── prompts.py           # AI Prompts
```

### 2. Interface Pattern (Strict Modularity)

**모든 도메인 간 통신은 `interface.py`를 통해서만**

```python
# ✅ CORRECT: Interface 사용
from domains.calculator.interface import calculate_nutrition
from domains.search.interface import search_products
from domains.ai.service.chatbot.interface import ask_question

# ❌ FORBIDDEN: 직접 import
from domains.calculator.logic.services import calculate_nutrition
from domains.search.state.models import SearchHistory
```

**장점:**
- 🔒 도메인 간 결합도 최소화
- 🧪 테스트 용이 (Mock 쉬움)
- ♻️ 리팩토링 안전 (내부 변경해도 interface만 유지하면 OK)

### 3. Stateful/Stateless 분리

**Stateful (`state/`)** - DB Owner
- Django Models
- Migrations
- DB 조회/저장 함수

**Stateless (`logic/`)** - Processor
- Pydantic Schemas (frozen=True)
- Pure Functions (DB 의존 없음)
- 완전히 독립적, 삭제 후 재작성 가능

```python
# ✅ logic/services.py - 순수 함수
def calculate_bmr(body: BodyInput) -> int:
    """DB 조회 없음, Pydantic 입출력"""
    return int(10 * body.weight_kg + 6.25 * body.height_cm - 5 * body.age + 5)

# ✅ state/interface.py - DB 조회
def get_coupang_products_by_keywords(keywords: list[str]) -> list[CoupangManualProduct]:
    """DB 조회는 여기서만"""
    return CoupangManualProduct.objects.filter(...)
```

### 4. Immutability (Pydantic frozen=True)

**모든 logic/ 내부 데이터는 불변**

```python
# ✅ logic/schemas.py
class BodyInput(BaseModel):
    model_config = ConfigDict(frozen=True)  # 생성 후 수정 불가
    age: int
    weight_kg: float

# ❌ 수정 시도 시 에러
body.age = 30  # FrozenInstanceError!

# ✅ 수정이 필요하면 새 객체 생성
new_body = BodyInput(age=30, weight_kg=body.weight_kg)
```

**이점:**
- 🐛 Side-effect 제거
- 🔍 디버깅 용이
- 🤖 AI가 예측 가능한 코드 생성

### 5. No ForeignKey Across Domains

**도메인 간 참조는 IntegerField만**

```python
# ✅ CORRECT
class SearchHistory(models.Model):
    user_id = models.IntegerField(db_index=True)  # ID만 저장

# ❌ FORBIDDEN
class SearchHistory(models.Model):
    user = models.ForeignKey('accounts.User')  # 도메인 간 FK 금지
```

**이유:**
- 📦 각 도메인이 독립적으로 배포 가능
- 🔧 DB 마이그레이션 충돌 방지
- ♻️ 도메인 교체/삭제 용이

---

## 📱 모바일 최적화 (19.5:9)

### 화면 비율
- **타겟**: 최신 스마트폰 (19.5:9 ~ 20:9)
- **해상도**: 360px ~ 430px (width)
- **디자인**: Mobile-First, Progressive Enhancement

### Tailwind Breakpoints
```css
/* Mobile First */
.container { max-width: 100%; }

/* Tablet: 768px+ */
@media (min-width: 768px) { ... }

/* Desktop: 1024px+ */
@media (min-width: 1024px) { ... }
```

### UI 구성
- **Bottom Navigation** (모바일) - 5탭
- **Sidebar** (데스크톱) - 확장 가능
- **Safe Area** - iOS notch 대응

---

## 🎨 디자인 시스템 (Toss Style)

### 색상
- **Primary**: `#3182F6` (Toss Blue)
- **Secondary**: `#0066FF` (Toss Blue Dark)
- **Success**: `#00C471`
- **Error**: `#F04452`

### 컴포넌트
- `.btn-toss` - 네온 glow 효과 버튼
- `.card-toss` - hover 시 네온 테두리
- `.input-toss` - Toss 스타일 입력창
- `.chip-toss` - 빠른 액션 칩
- `.ai-badge` - AI 표시 배지

### 테마
- **Light Mode** - 기본값
- **Dark Mode** - 사용자 선택

---

## 🤖 Gemini AI 독립 서비스

### 구조
```python
# domains/ai/service/chatbot/
├── interface.py          # Public API
├── gemini_service.py     # Singleton AI Service
└── prompts.py           # System Prompts

# 사용 예시 (어느 도메인에서든)
from domains.ai.service.chatbot.interface import ask_question

response = ask_question(
    question="20만원대 이어폰 추천해줘",
    context="쿠팡 상품 목록: ...",  # 호출자가 제공
    system_instruction="쇼핑 도우미",
)
```

### 특징
- 🔌 플러그인 패턴 (독립적)
- 🚫 도메인 의존성 없음
- ♻️ 컨텍스트는 호출자가 제공
- ⚡ Singleton (메모리 효율)

---

## 🛒 쿠팡 파트너스 전략

### 2단계 전략

**Phase 1: 수동 DB (현재)**
```python
class CoupangManualProduct(models.Model):
    """Admin에서 수동 등록"""
    product_id = CharField(unique=True)
    affiliate_url = URLField()  # 파트너스 링크
    # ...
```

**Phase 2: API 자동화 (15만원 달성 후)**
```python
class CoupangPartnersClient:
    """API 자동 연동"""
    async def search_products(keyword: str):
        # HMAC SHA256 인증
        # 실시간 상품 검색
```

### 검색 비율
- 쿠팡: 70% (수동 DB + API)
- 네이버: 20%
- 11번가: 10%

---

## 📊 기술 스택

### Backend
- **Python 3.12+** - Type Hints, Match-Case
- **Django 5.2** - ORM, Admin, Templates
- **Pydantic** - Schema Validation (frozen=True)
- **Google Gemini AI** - 2.0 Flash
- **PostgreSQL** - Main DB
- **Redis** - Cache

### Frontend
- **HTMX** - Hypermedia-Driven
- **Alpine.js** - Client State
- **Tailwind CSS** - Utility-First
- **Mobile-First** - 19.5:9 비율

### DevOps
- **uv** - Python 패키지 관리
- **bun** - JS 빌드
- **Docker** - PostgreSQL, Redis
- **Just** - Task Runner

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

## 🧪 품질 지표

| 항목 | 결과 |
|:---|:---|
| **테스트** | 10/10 통과 |
| **Linter** | 0 오류 |
| **DAEMON 준수율** | 83% |
| **코드 라인** | ~2,500줄 |
| **Tailwind 클래스** | 8,449개 |

---

## 🚀 배포 구조

```
GitHub → GitHub Actions (Build) → GHCR
                                    ↓
                              Coolify (Deploy)
                                    ↓
                         Hetzner VPS (CPX32)
                                    ↓
                         Cloudflare (DNS + CDN + SSL)
```

---

## 📁 프로젝트 통계

- **총 도메인**: 13개
- **interface.py**: 5개
- **Pydantic Schemas**: 8개
- **Pure Functions**: 15개
- **Django Models**: 10개
- **API Integrations**: 3개 (Naver, 11st, Coupang)

---

**Simple > Complex, Vertical Slicing, Interface Pattern** 🎯
