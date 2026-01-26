"""
🤖 AI Chatbot Interface

Public API for Gemini AI chatbot functionality.
External domains should only import from this file.

✅ DAEMON Rule: This is the ONLY file external domains can import from.
"""

from .gemini_service import ChatResponse, ask_question, generate_text, get_gemini_service

__all__ = [
    # Types
    "ChatResponse",
    # Services
    "ask_question",
    "generate_text",
    "get_gemini_service",
]
