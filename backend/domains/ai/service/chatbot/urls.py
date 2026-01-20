"""
🔗 Chatbot URL Patterns
"""

from django.urls import path

from .pages.chat import views

app_name = "ai_chatbot"

urlpatterns = [
    # Page Views
    path("", views.chat_page, name="chat_home"),
    path("new/", views.new_chat, name="new_chat"),
    path("<int:session_id>/", views.chat_page, name="chat_session"),
    
    # HTMX Actions
    path("send/", views.send_message, name="send_new"),
    path("send/<int:session_id>/", views.send_message, name="send_session"),
    path("delete/<int:session_id>/", views.delete_session, name="delete_session"),
]
