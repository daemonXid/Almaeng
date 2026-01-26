"""
ALMAENG - Granian Entry Point

Granian is a Rust-based HTTP server for Python ASGI/WSGI apps.
It provides better performance than uvicorn for high-concurrency scenarios.

Usage:
    # Development (uvicorn - default)
    just dev

    # Production with Granian
    granian --interface asgi main:app --host 0.0.0.0 --port 2020

    # Or via Python
    python main.py

Environment Variables:
    - WEB_SERVER: "granian" or "uvicorn" (default: uvicorn)
    - DJANGO_PORT: Port to listen on (default: 2020)
    - WORKERS: Number of workers (default: auto)
"""

import os
import sys
from pathlib import Path

# Add backend to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR / "backend"))

# Django setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from django.core.asgi import get_asgi_application

# ASGI application
app = get_asgi_application()


def run_server():
    """Run the appropriate server based on environment."""
    server = os.getenv("WEB_SERVER", "uvicorn").lower()
    host = os.getenv("DJANGO_HOST", "0.0.0.0")
    port = int(os.getenv("DJANGO_PORT", "2020"))
    workers = int(os.getenv("WORKERS", "0")) or None  # 0 = auto
    reload = os.getenv("DEBUG", "true").lower() == "true"

    print(f"[ALMAENG] Starting with {server}...")
    print(f"   URL: http://{host}:{port}")

    if server == "granian":
        try:
            from granian import Granian
            from granian.constants import Interfaces

            granian = Granian(
                "main:app",
                address=host,
                port=port,
                interface=Interfaces.ASGI,
                workers=workers or 2,
                reload=reload,
            )
            granian.serve()
        except ImportError:
            print("⚠️  Granian not installed. Install with: uv add granian")
            print("    Falling back to uvicorn...")
            run_uvicorn(host, port, reload)
    else:
        run_uvicorn(host, port, reload)


def run_uvicorn(host: str, port: int, reload: bool):
    """Run with uvicorn (default)."""
    try:
        import uvicorn

        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=reload,
            reload_dirs=["backend"] if reload else None,
        )
    except ImportError:
        print("❌ Neither granian nor uvicorn installed!")
        print("   Install with: uv add uvicorn")
        sys.exit(1)


if __name__ == "__main__":
    run_server()
