# 🏗️ DAEMON Domain Architecture

> **Flattened Domain Structure with Module Composition**

## 📐 Architecture Philosophy

DAEMON uses a **"Domain > Module"** hierarchy where:
- **Domain**: A business boundary (Bounded Context in DDD terms)
- **Module**: A sub-feature within a domain

Each domain exposes its API through `interface.py` at the domain or module level.

## 📁 Directory Structure

```
domains/
├── ai/                          # 🤖 AI Domain
│   ├── __init__.py
│   ├── chatbot/                 # Module: Chatbot UI & Logic
│   │   ├── interface.py
│   │   ├── pages/chat/
│   │   └── ...
│   └── providers/               # Module: AI Provider Clients
│       ├── interface.py         # get_ai_client()
│       ├── gemini.py           # Google Gemini (Primary)
│       └── base.py
│
├── accounts/                    # 👤 User Accounts Domain
│   ├── interface.py
│   ├── models.py
│   ├── pages/profile/
│   └── templates/account/
│
├── core/                        # 🏛️ Core Application Domain
│   ├── interface.py
│   ├── pages/
│   │   ├── home/
│   │   ├── getting_started/
│   │   └── domains_list/
│   └── ...
│
├── health/                      # 🏥 System Health Domain
│   ├── interface.py
│   └── pages/status/
│
├── notifications/               # 🔔 Notifications Domain
│   ├── email/                   # Module: Email
│   │   └── interface.py
│   └── push/                    # Module: Push Notifications
│       └── interface.py
│
├── media/                       # 🎬 Media Domain
│   ├── images/                  # Module: Image Processing
│   │   └── interface.py
│   └── storage/                 # Module: Cloud Storage
│       └── interface.py
│
├── marketing/                   # 📣 Marketing Domain
│   ├── campaigns/               # Module: Campaign Management
│   │   └── interface.py
│   └── referrals/               # Module: Referral Program
│       └── interface.py
│
├── seo/                         # 🔍 SEO Domain
│   ├── meta/                    # Module: Meta Tags
│   │   └── interface.py
│   └── sitemap/                 # Module: Sitemap Generation
│       └── interface.py
│
├── analytics/                   # 📊 Analytics Domain
├── settings/                    # ⚙️ Site Settings Domain
└── ...                          # Other scaffold domains
```

## 🎯 The Interface Pattern

Every domain/module exposes its API through `interface.py`:

```python
# ✅ CORRECT: Import from interface
from domains.notifications.email.interface import send_email
from domains.ai.providers.interface import get_ai_client

# ❌ WRONG: Direct internal imports
from domains.notifications.email.services import EmailService
```

## 🔀 Domain vs Module

| Aspect | Domain | Module |
|:---|:---|:---|
| **Purpose** | Business boundary | Sub-feature |
| **Apps.py** | Required for Django | Not required |
| **interface.py** | Required | Required |
| **Models** | Can have | Usually no |
| **Pages** | Can have | Can have |
| **Example** | `ai/` | `ai/providers/` |

## 🚀 Quick Start

### Using a Module
```python
# Email notification
from domains.notifications.email.interface import send_email

send_email(to="user@example.com", subject="Welcome!", template="welcome")

# AI completion
from domains.ai.providers.interface import complete

response = complete("Explain HTMX")
print(response.text)
```

### Creating a New Module

1. Create module directory: `domains/{domain}/{module}/`
2. Add `__init__.py` with docstring
3. Add `interface.py` with public API
4. Import in domain's `__init__.py` if needed

## 📋 Domain Categories

| Category | Domains |
|:---|:---|
| **Core** | `core`, `accounts`, `health`, `settings` |
| **AI** | `ai` (chatbot, providers) |
| **Growth** | `analytics`, `marketing`, `seo` |
| **Infrastructure** | `notifications`, `media`, `tasks` |
| **Compliance** | `security`, `audit`, `legal`, `policy` |
