"""
🎯 AI Recommendations URL Configuration
"""

from django.urls import path

from .pages.recommend.views import quiz_page, quiz_result, recommend_page

app_name = "recommendations"

urlpatterns = [
    path("", recommend_page, name="home"),
    path("quiz/", quiz_page, name="quiz"),
    path("quiz/result/", quiz_result, name="quiz_result"),
]
