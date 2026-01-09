# 👤 DAEMON Module: Accounts (`base.accounts`)

> User Authentication and Identity Management.

## 🎯 Purpose

Handles user registration, login, profile management, and social authentication using `django-allauth`.

## ✨ Key Features

- **Custom User Model**: Extended with `profile_image` and `bio`.
- **Lifecycle Integration**: Uses `django-lifecycle` for post-creation hooks.
- **Social Login**: Ready-to-use OAuth integration.
- **HTMX Auth**: Login/Signup flows optimized for HTMX/Alpine.js.

## 🏗️ Portability

This module can be used in any DAEMON project. It depends on `base.core` for templates.

## 📂 Structure

- `models.py`: Custom `User` model inheriting from `LifecycleModel`.
- `interface.py`: Auth utilities and user getters.
- `views.py`: Profile and authentication views.

## 📝 Usage

```python
from modules.base.accounts.interface import get_user_profile

profile = get_user_profile(user_id)
```
