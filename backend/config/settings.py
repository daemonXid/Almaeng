import sys
from pathlib import Path

import environ
import logfire

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# --- Environment Variables ---
env = environ.Env(
    DEBUG=(bool, True),
    LOGFIRE_TOKEN=(str, None),
    SENTRY_DSN=(str, None),
)

# Load .env file if it exists
env_file = BASE_DIR / ".env"
if env_file.exists():
    environ.Env.read_env(str(env_file))

# Add 'backend' and 'domains' to sys.path for easy imports
sys.path.append(str(BASE_DIR / "backend"))
sys.path.append(str(BASE_DIR / "backend" / "domains"))

# --- Logfire Observability ---
LOGFIRE_TOKEN = env("LOGFIRE_TOKEN")
if LOGFIRE_TOKEN:
    logfire.configure(token=LOGFIRE_TOKEN)
else:
    # In development, don't crash if not authenticated
    logfire.configure(send_to_logfire=False)

logfire.instrument_django()

# --- Core Django Settings ---
SECRET_KEY = env("SECRET_KEY", default="django-insecure-almaeng-local-dev-key")
DEBUG = env("DEBUG")

# --- Sentry Error Tracking ---
SENTRY_DSN = env("SENTRY_DSN")
if SENTRY_DSN and not DEBUG:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(
                transaction_style="url",
                middleware_spans=True,
                signals_spans=True,
                cache_spans=True,
            ),
            LoggingIntegration(level=None, event_level=None),
        ],
        traces_sample_rate=0.1,  # 10% of transactions
        profiles_sample_rate=0.1,  # 10% of transactions
        send_default_pii=False,  # Don't send user data
        environment="production" if not DEBUG else "development",
    )
# --- Production Security ---
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])

if not DEBUG:
    # Always allow local access for health checks
    ALLOWED_HOSTS.extend(["localhost", "127.0.0.1", "0.0.0.0"])

if not DEBUG:
    # HTTPS settings
    SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # HSTS
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# --- Ports ---
APP_PORT = env("APP_PORT", default="8000")
POSTGRES_PORT = env("POSTGRES_PORT", default="5432")
REDIS_PORT = env("REDIS_PORT", default="6379")

# --- AI Configuration ---
# Google Gemini Only
GEMINI_API_KEY = env("GEMINI_API_KEY", default="")

# --- External API Keys ---
# Naver Developers (Login & Search)
NAVER_CLIENT_ID = env("NAVER_CLIENT_ID", default="")
NAVER_CLIENT_SECRET = env("NAVER_CLIENT_SECRET", default="")

# 11번가 Open API
ELEVENST_API_KEY = env("ELEVENST_API_KEY", default="")

# Coupang Partners
COUPANG_ACCESS_KEY = env("COUPANG_ACCESS_KEY", default="")
COUPANG_SECRET_KEY = env("COUPANG_SECRET_KEY", default="")

# MFDS (식약처 공공데이터)
MFDS_API_KEY = env("MFDS_API_KEY", default="")


# =============================================================================
# 🔍 Auto-Discovery: Automatically find and register Django apps in domains/
# =============================================================================


def auto_discover_apps(domains_dir: Path) -> list[str]:
    """
    Scan the domains folder and discover all Django apps.

    Structure:
    - domains/core/apps.py → "domains.base.core"
    - domains/ai/apps.py → "domains.ai.service"
    - domains/custom/apps.py → "domains.custom"

    Supports up to 3 levels of nesting.

    Returns:
        List of app paths in dot notation
    """
    discovered_apps = []

    if not domains_dir.exists():
        return []

    def scan_directory(directory: Path, prefix: str) -> None:
        """Recursively scan directory for apps.py files."""
        for item in directory.iterdir():
            if not item.is_dir():
                continue
            if not (item / "__init__.py").exists():
                continue
            if item.name.startswith("_"):
                continue

            app_path = f"{prefix}.{item.name}"

            # If this directory has apps.py, it's a Django app
            if (item / "apps.py").exists():
                discovered_apps.append(app_path)
            else:
                # Otherwise, scan subdirectories
                scan_directory(item, app_path)

    scan_directory(domains_dir, "domains")
    return sorted(discovered_apps)


# Discover domains
DOMAINS_DIR = BASE_DIR / "backend" / "domains"
PROJECT_APPS = auto_discover_apps(DOMAINS_DIR)

# Debug: Print discovered apps on startup
if DEBUG:
    print(f"[DAEMON] Auto-discovered domains: {PROJECT_APPS}")


INSTALLED_APPS = [
    # --- Django Built-ins ---
    "unfold",  # Unfold Admin (Must be before admin)
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",  # For Allauth
    "django.contrib.humanize",
    # --- Domains (Auto-Discovered) ---
    # Must be BEFORE third-party apps for template overrides (e.g. allauth)
    *PROJECT_APPS,
    # --- Third Party ---
    "pgvector",  # Vector similarity search
    "ninja_extra",
    "django_components",
    "django_htmx",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    # Toss OpenID Connect (간편 로그인)
    "allauth.socialaccount.providers.openid_connect",
    "compressor",
    "storages",
]

# Add dev-only apps if DEBUG is True
if DEBUG:
    INSTALLED_APPS += [
        "django_extensions",
        "django_browser_reload",
    ]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Static Files
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",  # HTMX
    "allauth.account.middleware.AccountMiddleware",  # Allauth
]

if DEBUG:
    MIDDLEWARE.append("django_browser_reload.middleware.BrowserReloadMiddleware")

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "backend" / "templates",  # Global templates (base.html, 404.html)
            BASE_DIR / "backend" / "domains",  # Domain-specific templates (Vertical Slicing)
            BASE_DIR / "backend" / "domains" / "base",
            BASE_DIR / "backend" / "domains" / "features",
            BASE_DIR / "backend" / "domains" / "ai" / "service",
            # PRD v2 신규 도메인
            BASE_DIR / "backend" / "domains" / "search",
            BASE_DIR / "backend" / "domains" / "billing",
            BASE_DIR / "backend" / "domains" / "calculator",
            BASE_DIR / "backend" / "domains" / "integrations",
        ],
        "APP_DIRS": False,  # Loader 활용 예정 (django-components 등)
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "loaders": [
                (
                    "django.template.loaders.cached.Loader",
                    [
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader",
                        "django_components.template_loader.Loader",  # Component Loader
                    ],
                )
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database
DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default=f"postgres://{env('POSTGRES_USER', default='almaeng_user')}:{env('POSTGRES_PASSWORD', default='almaeng_password')}@{env('POSTGRES_HOST', default='localhost')}:{POSTGRES_PORT}/{env('POSTGRES_DB', default='almaeng_db')}",
    )
}

# Redis (for caching and Taskiq)
REDIS_URL = f"redis://{env('REDIS_HOST', default='localhost')}:{REDIS_PORT}/0"

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

# Static & Media
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static_root"
STATICFILES_DIRS = [
    BASE_DIR / "backend" / "static",
]

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "backend" / "media"

# Ninja Extra
NINJA_EXTRA = {
    "PAGINATION_CLASS": "ninja_extra.pagination.PageNumberPagination",
}

SITE_ID = 1  # For Allauth

# ============================================
# 🔐 Django Allauth Settings
# ============================================

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# Login/Logout redirects
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"
LOGIN_URL = "/accounts/login/"

# Email settings (Allauth v0.60+ format)
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "optional"  # "mandatory" for production
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True

# For development, print emails to console
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ============================================
# 🌐 Social Login (Google, Kakao, Naver)
# ============================================
SOCIALACCOUNT_PROVIDERS = {
    "openid_connect": {
        "APPS": [
            {
                "provider_id": "toss",
                "name": "Toss",
                "client_id": env("TOSS_OPENID_CLIENT_ID", default=""),
                "secret": env("TOSS_OPENID_CLIENT_SECRET", default=""),
                "settings": {
                    "server_url": "https://oauth2.toss.im/.well-known/openid-configuration",
                },
            }
        ],
        "OAUTH_PKCE_ENABLED": True,
    },
}

# Auto-signup: 소셜 로그인 시 자동 가입
SOCIALACCOUNT_AUTO_SIGNUP = True

# 소셜 로그인 중간 페이지 제거 (바로 OAuth provider로 리다이렉트)
SOCIALACCOUNT_LOGIN_ON_GET = True  # GET 요청으로 바로 로그인 시작
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_EMAIL_REQUIRED = False
SOCIALACCOUNT_EMAIL_VERIFICATION = "none"  # 소셜 로그인은 이메일 인증 불필요

# 👤 Identity
AUTH_USER_MODEL = "daemon_auth.User"

# 📦 Storages & Compression
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        # WhiteNoise for production, default for development
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
        if not DEBUG
        else "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
]

COMPRESS_ENABLED = True

# ============================================
# 🌐 Internationalization (i18n)
# ============================================

LANGUAGE_CODE = "ko"
TIME_ZONE = "Asia/Seoul"
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ("ko", "한국어"),
    ("en", "English"),
]

LOCALE_PATHS = [
    BASE_DIR / "backend" / "locale",
]

# ============================================
# 📝 Logging Configuration
# ============================================

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "json": {
            "()": "structlog.stdlib.ProcessorFormatter",
            "processor": "structlog.dev.ConsoleRenderer",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose" if DEBUG else "json",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO" if not DEBUG else "DEBUG",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "domains": {
            "handlers": ["console"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
    },
}

# ============================================
# 🔒 Security Settings (django-axes)
# ============================================

AXES_ENABLED = not DEBUG
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1  # 1 hour
AXES_LOCKOUT_CALLABLE = "axes.lockout.database_lockout"
AXES_LOCKOUT_TEMPLATE = "account/lockout.html"
AXES_RESET_ON_SUCCESS = True

# ============================================
# 💳 Toss Payments
# ============================================

TOSS_CLIENT_KEY = env("TOSS_CLIENT_KEY", default="")
TOSS_SECRET_KEY = env("TOSS_SECRET_KEY", default="")
