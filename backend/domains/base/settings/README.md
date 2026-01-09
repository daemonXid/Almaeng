# ⚙️ DAEMON Module: Settings (`base.settings`)

> Runtime Dynamic Site Configuration.

## 🎯 Purpose

Manage site-wide settings (name, logo, maintenance mode) via the database without code changes.

## ✨ Key Features

- **Singleton Pattern**: Only one `SiteSettings` instance exists.
- **Context Processor**: Settings automatically available in all templates as `{{ site }}`.
- **Feature Flags**: Toggle registration, AI features, etc., from the admin panel.

## 🏗️ Portability

Dependencies: `base.core` (for base classes).

## 📝 Usage

**In Python:**

```python
from modules.base.settings.interface import get_settings
site = get_settings()
```

**In Templates:**

```html
<h1>{{ site.name }}</h1>
```
