# 💬 DAEMON Module: Chatbot (`ai.chatbot`)

> Project-Aware AI Assistant.

## 🎯 Purpose

A self-contained chatbot that understands the DAEMON codebase and helps the user navigate through it.

## ✨ Key Features

- **Codebase Indexing**: Scans project files to provide context-aware answers.
- **HTMX Overlay**: Integrated into `base.html` via a non-blocking sidebar.
- **Contextual Search**: Finds relevant code fragments.

## 🏗️ Portability

Dependencies: `ai.providers`.

## 📝 Usage

Include in any template using:

```html
{% include "chatbot/sidebar.html" %}
```
