# 🤖 DAEMON Module: AI Providers (`ai.providers`)

> AI Abstraction Layer & Multi-Provider Strategy.

## 🎯 Purpose

Decouple the application from specific AI vendors. Provides a unified interface to HuggingFace, DeepSeek, and OpenRouter.

## ✨ Key Features

- **Strategy Chain**: HuggingFace (Free) → DeepSeek (Quality) → OpenRouter (Multi-Model).
- **Pydantic AI Integration**: Modern agent framework support.
- **Structured Output**: Built-in support for Pydantic schema validation.

## 🏗️ Portability

Requires `openai` and `pydantic-ai` libraries.

## 📝 Usage

```python
from modules.ai.providers.interface import get_ai_client

client = get_ai_client()
response = client.complete("Hello!")
```

### Agents (v4.4)

```python
from modules.ai.providers.interface import architect_agent

result = await architect_agent.run("How do I add a module?")
```
