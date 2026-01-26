"""
Update PostgreSQL password to match .env file

This script connects to PostgreSQL using the old password (if known)
and updates it to match the new password in .env file.

Usage:
    uv run python scripts/update_db_password.py [old_password]

If old_password is not provided, it will try common default passwords.
"""

import os
import sys
from pathlib import Path

# Add backend to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "backend"))

# Set Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

import psycopg
from django.conf import settings


def update_postgres_password(old_password: str | None = None):
    """Update PostgreSQL password to match .env"""
    db_config = settings.DATABASES["default"]
    new_password = db_config["PASSWORD"]
    user = db_config["USER"]
    host = db_config["HOST"]
    port = db_config["PORT"]
    db_config["NAME"]

    # Try to connect with old password or common defaults
    old_passwords_to_try = []
    if old_password:
        old_passwords_to_try.append(old_password)
    else:
        # Common default passwords
        old_passwords_to_try.extend(
            [
                "almaeng_password",
                "almaeng",
                "password",
                "postgres",
                "",  # No password
            ]
        )

    connection = None
    for old_pwd in old_passwords_to_try:
        try:
            print(f"Trying to connect with password: {'*' * len(old_pwd) if old_pwd else '(empty)'}...")
            connection = psycopg.connect(
                host=host,
                port=port,
                user=user,
                password=old_pwd,
                dbname="postgres",  # Connect to postgres database to change password
            )
            print("Connected to PostgreSQL!")
            break
        except Exception as e:
            error_str = str(e)
            if "password authentication failed" not in error_str and "no password supplied" not in error_str:
                print(f"Connection error: {e}")
                break
            continue

    if not connection:
        print("Could not connect to PostgreSQL with any known password.")
        print("   You may need to:")
        print("   1. Restart Docker containers: just down-v && just up")
        print("   2. Or manually update the password in PostgreSQL")
        sys.exit(1)

    try:
        # Update password
        with connection.cursor() as cur:
            cur.execute(f"ALTER USER {user} WITH PASSWORD %s", (new_password,))
            connection.commit()
        print(f"Password updated for user '{user}'!")
        print("   New password matches .env file")
    except Exception as e:
        print(f"Failed to update password: {e}")
        sys.exit(1)
    finally:
        connection.close()


if __name__ == "__main__":
    old_password = sys.argv[1] if len(sys.argv) > 1 else None
    update_postgres_password(old_password)
