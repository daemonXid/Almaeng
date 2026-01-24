# ALMAENG Architecture Guide 🏗️

> **Philosophy**: "Vertical Slicing" over "Layered Architecture".
> Functionality should be grouped by **Feature**, not by Technical Layer (Controller, Service, Repository).

---

## 1. Directory Structure (Vertical Slicing)

Each feature is a self-contained module in `backend/domains/`.

```
backend/domains/
├── features/
│   ├── supplements/          # 💊 [Domain: Supplements]
│   │   ├── api.py            # API Endpoints (Ninja)
│   │   ├── models.py         # Database Models
│   │   ├── schemas.py        # Pydantic Schemas
│   │   ├── services.py       # Business Logic
│   │   ├── vision_service.py # Feature-specific Service (OCR)
│   │   ├── urls.py           # Feature-specific URLs
│   │   ├── templates/        # 🎨 Local Templates !!
│   │   │   └── supplements/
│   │   │       ├── pages/    # Page Templates (search, detail, upload)
│   │   │       └── components/ # Local Components
│   │   └── pages/            # View Logic (render)
│   │       ├── search/       # Feature: Search
│   │       ├── detail/       # Feature: Detail
│   │       └── upload/       # Feature: Upload (OCR)
│   │           ├── views.py  # Local View
│   │           └── upload.html # Local Template (Colocated)
│   │
│   └── payments/             # 💳 [Domain: Payments]
│       ├── integrations/     # External API Clients (Toss)
│       └── pages/
│           └── checkout/
│
└── base/                     # 🏠 [Core Domains]
    ├── accounts/             # Auth, User Profile
    └── core/                 # Shared Utilities, Base Templates
```

---

## 2. Key Rules 📏

### ① Locality (Co-location)
- **Logic + Template + Style** should stay together.
- Example: `upload/views.py` and `upload/upload.html` should be as close as possible.

### ② Domain Isolation
- Domains should interact via **Public Interfaces** (Services/Selectors) where possible.
- Avoid raw SQL joins across domains.

### ③ Data Flow (Strict Typing)
- **Input**: Pydantic Schema
- **Logic**: Type-hinted Python Code
- **Output**: JSON-LD / Pydantic Schema / HTML (HTMX)
- **NO** untyped Dictionaries passed around in core logic.

---

## 3. Tech Stack Specifics 🛠️

- **Vision AI**: Uses `Gemini 2.0 Flash` via `google-genai` SDK. returns structured `LabelAnalysisResult` (Pydantic).
- **Frontend**: `HTMX` for server-driven UI, `Alpine.js` for client-side interactivity (payment widget, camera handling).
- **Deployment**: GHCR -> Hetzner (Docker).

---

## 4. Development Workflow

1.  **Create Domain**: `mkdir backend/domains/features/new_feature`
2.  **Add to Settings**: Auto-discovery will find it if it has `apps.py` (or manual add).
3.  **Build Vertical Slice**: Implement Model -> Schema -> Service -> View -> Template in that folder.
