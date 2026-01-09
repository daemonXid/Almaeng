# 😈 DAEMON Module: Core (`base.core`)

> The foundation of the DAEMON-ONE template.

## 🎯 Purpose

`base.core` provides the shared infrastructure for all other modules. It contains the landing page, base HTML templates, and abstract model patterns (`TimestampedModel`, etc.).

## ✨ Key Features

- **Base Templates**: `base.html` and common UI layouts.
- **Abstract Patterns**: ULID-based models, soft-delete, and timestamp tracking.
- **Landing Page**: The entry point of the application.
- **HTMX Utilities**: Common htmx endpoints and patterns.

## 🏗️ Portability

This module is the **anchor** of DAEMON-ONE. Other modules depend on the base templates and model patterns defined here.

## 📂 Structure

- `interface.py`: Public API (Base models, core templates).
- `models.py`: Abstract base classes.
- `views.py`: Home and documentation views.
- `templates/`: Global and core-specific templates.

## 📝 Usage

```python
from modules.base.core.interface import TimestampedModel

class MyModel(TimestampedModel):
    name = models.CharField(max_length=100)
```
