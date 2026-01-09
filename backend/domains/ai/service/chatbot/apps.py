from django.apps import AppConfig


class ChatbotConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "domains.ai.service.chatbot"
    label = "ai_chatbot"
    verbose_name = "🤖 Chatbot"
