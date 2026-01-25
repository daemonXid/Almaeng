from django.urls import path
from .pages.search import views

app_name = "search"

urlpatterns = [
    path("", views.search_page, name="search"),
    path("autocomplete/", views.autocomplete, name="autocomplete"),
    path("track-click/", views.track_click, name="track_click"),
]
