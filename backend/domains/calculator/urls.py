from django.urls import path

from .pages.calculator.views import calculator_view

app_name = "calculator"

urlpatterns = [
    path("", calculator_view, name="index"),
]
