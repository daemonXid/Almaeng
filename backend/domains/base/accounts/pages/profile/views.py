"""
🌐 Auth Views

Custom views for user profile.
"""

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render


@login_required
def profile(request: HttpRequest) -> HttpResponse:
    """User profile page with image upload."""
    if request.method == "POST":
        action = request.POST.get("action")

        if action == "update_image" and request.FILES.get("profile_image"):
            request.user.profile_image = request.FILES["profile_image"]
            request.user.save(update_fields=["profile_image"])
            return redirect("auth:profile")

    return render(request, "accounts/pages/profile/profile.html")
