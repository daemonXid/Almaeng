"""
Create superuser from .env file

Usage:
    uv run python scripts/create_superuser.py
"""

import os
import sys
from pathlib import Path

# Add backend to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "backend"))

# Load environment variables from .env

# Set Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


def create_superuser_from_env():
    """Create superuser from .env file"""
    try:
        username = getattr(settings, "DJANGO_SUPERUSER_USERNAME", None) or os.getenv("DJANGO_SUPERUSER_USERNAME", "")
        email = getattr(settings, "DJANGO_SUPERUSER_EMAIL", None) or os.getenv("DJANGO_SUPERUSER_EMAIL", "")
        password = getattr(settings, "DJANGO_SUPERUSER_PASSWORD", None) or os.getenv("DJANGO_SUPERUSER_PASSWORD", "")

        if not username or not email or not password:
            print("❌ Missing superuser credentials in .env file")
            print("   Required: DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_PASSWORD")
            sys.exit(1)

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            print(f"⚠️  Superuser '{username}' already exists. Updating password...")
            user = User.objects.get(username=username)
            user.set_password(password)
            user.email = email
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.save()
            print(f"✅ Superuser '{username}' password updated!")
        else:
            # Create new superuser
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
            )
            print(f"✅ Superuser '{username}' created successfully!")
    except Exception as e:
        error_msg = str(e)
        if "password authentication failed" in error_msg or "OperationalError" in error_msg:
            print("❌ Database connection failed!")
            print("   This usually means the database password in .env doesn't match the actual database.")
            print("   Solutions:")
            print("   1. Restart Docker containers: just down-v && just up")
            print("   2. Or update database password to match .env")
            print(f"\n   Error: {error_msg}")
        elif "does not exist" in error_msg or "relation" in error_msg.lower():
            print("❌ Database tables not found!")
            print("   You need to run migrations first:")
            print("   just migrate")
            print(f"\n   Error: {error_msg}")
        else:
            print(f"❌ Error: {error_msg}")
        sys.exit(1)


if __name__ == "__main__":
    create_superuser_from_env()
