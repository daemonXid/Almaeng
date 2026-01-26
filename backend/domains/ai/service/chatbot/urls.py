"""
🔗 Chatbot URL Patterns
"""

from django.urls import path

from .pages.chat import views

app_name = "ai_chatbot"

urlpatterns = [
    # Simple Chat Page (앱인토스용)
    path("", views.simple_chat_page, name="chat_home"),
    # HTMX Actions
    path("send/", views.simple_chat_send, name="send_new"),
    # 기존 복잡한 chat (주석처리)
    # path("new/", views.new_chat, name="new_chat"),
    # path("<int:session_id>/", views.chat_page, name="chat_session"),
]
