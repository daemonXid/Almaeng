"""
🔗 Chatbot URL Patterns
"""

from django.urls import path

from .pages.chat import views

app_name = "chatbot"

urlpatterns = [
    path("", views.chat_page, name="chat"),
    path("send/", views.send_message, name="send"),
    path("stream/", views.stream_message, name="stream"),
    path("search/", views.search, name="search"),
]
