set shell := ["cmd.exe", "/c"]
export UV_LINK_MODE := "copy"

# 😈 ALMAENG Justfile

# Load environment variables (default APP_PORT=3265)
APP_PORT := env_var_or_default("APP_PORT", "8000")

# --- 🚀 Main Commands ---
# Initialize a new project (Rename all references)
init name:
    uv run python scripts/init_project.py {{name}}

# Sync project identity and document active domains
sync:
    @echo 😈 Syncing project metadata...
    uv run python scripts/sync_project.py
    @echo 📦 Updating dependencies...
    uv sync
    bun install
    @echo 🧹 Cleaning up code...
    -just lint
    -just format
    @echo ✅ Project synced and dependencies updated!

# Install all dependencies (Native: uv + bun | Docker: infra)
setup:
    @echo 😈 Setting up ALMAENG (Native Dev Drive Environment)...
    -uv sync
    bun install
    -just update-db
    just build-assets
    @echo ✅ Setup complete! Make sure 'just up' is running for DB/Cache.
    @echo 🚀 Run 'just dev' to start development.

# Start development (Django + Tailwind watch)
dev:
    -just up
    just build-assets
    uv run python backend/manage.py migrate
    @echo.
    @echo 😈 ===================================================
    @echo    ALMAENG Development Server
    @echo ======================================================
    @echo    📍 Home:     http://127.0.0.1:{{APP_PORT}}
    @echo    📍 API Docs: http://127.0.0.1:{{APP_PORT}}/api/docs
    @echo    📍 Admin:    http://127.0.0.1:{{APP_PORT}}/admin/
    @echo ======================================================
    @echo.
    start /b uv run python backend/manage.py runserver 127.0.0.1:{{APP_PORT}}
    bun run tailwind:watch

# Quick start without Docker (SQLite)
dev-lite:
    just build-assets
    @echo "😈 Starting ALMAENG (Lite Mode - SQLite)..."
    uv run python backend/manage.py migrate
    uv run python backend/manage.py runserver 127.0.0.1:{{APP_PORT}}

# --- 🚀 Production ---

# Start production server with Granian (Rust-based ASGI)
prod workers="4":
    @echo ""
    @echo "🦀 ═══════════════════════════════════════════════"
    @echo "   ALMAENG Production Server (Granian)"
    @echo "═══════════════════════════════════════════════════"
    @echo "   📍 http://0.0.0.0:{{APP_PORT}}"
    @echo "   👷 Workers: {{workers}}"
    @echo "═══════════════════════════════════════════════════"
    @echo ""
    uv run granian --interface asgi main:app --host 0.0.0.0 --port {{APP_PORT}} --workers {{workers}}

# Production with hot reload (for staging)
prod-reload:
    uv run granian --interface asgi main:app --host 0.0.0.0 --port {{APP_PORT}} --workers 2 --reload

# Benchmark server (single worker, no reload)
bench:
    @echo "⚡ Starting benchmark mode..."
    uv run granian --interface asgi main:app --host 0.0.0.0 --port {{APP_PORT}} --workers 1 --threading-mode workers

# --- 🐳 Docker Production ---

# Build production Docker image
build:
    @echo "🐳 Building production Docker image..."
    docker build -t almaeng:latest .
    @echo "✅ Image built: almaeng:latest"

# Deploy full production stack
deploy:
    @echo "🚀 Deploying ALMAENG production stack..."
    docker compose -f docker-compose.prod.yml up -d --build
    @echo "✅ Deployed! Check http://localhost:{{APP_PORT}}"

# Stop production stack
deploy-down:
    docker compose -f docker-compose.prod.yml down

# View production logs
deploy-logs:
    docker compose -f docker-compose.prod.yml logs -f

# --- 🐳 Infrastructure ---

# Start Docker infrastructure (Postgres, Redis)
up:
    docker compose up -d postgres redis
    @echo 🐋 Infrastructure started!
    @echo    🐘 Postgres: localhost:5432 (Docker)
    @echo    🔴 Redis:    localhost:6379 (Docker)
    @echo ✅ Docker containers are running in the background.

# Stop Docker containers
down:
    docker compose down

# Stop and remove volumes
down-v:
    docker compose down -v

# View logs
logs:
    docker compose logs -f

# --- 🗄️ Database ---

# Create and apply migrations
migrate:
    uv run python backend/manage.py makemigrations
    uv run python backend/manage.py migrate

# Create superuser (uses .env credentials)
superuser:
    @echo "📦 Creating superuser from .env..."
    uv run python backend/manage.py createsuperuser --noinput || echo "⚠️  Superuser may already exist"

# Create superuser interactively
superuser-interactive:
    uv run python backend/manage.py createsuperuser

# Django shell (shell_plus)
shell:
    uv run python backend/manage.py shell_plus

# Database shell (psql)
dbshell:
    docker compose exec postgres psql -U ${POSTGRES_USER:-almaeng_user} -d ${POSTGRES_DB:-almaeng_db}

# --- 🎨 Frontend ---

# Build all frontend assets (vendor bundle + CSS)
build-assets:
    @echo "📦 Building frontend assets..."
    bun run build
    @echo "✅ Assets built to backend/static/dist/ and backend/static/css/"

# Build vendor bundle only (htmx + alpine + pglite)
vendor:
    bun run vendor

# Build Tailwind CSS only
css-build:
    bun run tailwind:build

# Watch Tailwind CSS
css-watch:
    bun run tailwind:watch

# Update browserslist db
update-db:
    bunx update-browserslist-db@latest

# --- 🧪 Quality ---

# Run linters (ruff)
lint:
    uv run ruff check . --fix --unsafe-fixes
    @echo "✅ Lint check passed!"

# Run tests
test:
    uv run python -m pytest

# Run tests with coverage
test-cov:
    uv run python -m pytest --cov=backend --cov-report=html

# Format code
format:
    uv run ruff format .

# Check code without fixing
check:
    uv run ruff check .

# Static type check
analyze:
    uv run mypy .

# --- 🛠️ Utilities ---

# Show all registered URLs
show-urls:
    uv run python backend/manage.py show_urls

# Collect static files
static:
    uv run python backend/manage.py collectstatic --noinput

# Show all auto-discovered domains
domains:
    uv run python scripts/sync_project.py --list-domains

# Create a new domain
new-domain name:
    uv run python scripts/create_domain.py {{name}}

# Create a multi-feature domain
new-domain-multi name +features:
    uv run python scripts/create_domain.py {{name}} --multi-feature {{features}}

# --- 🧹 Clean ---

# Clean build artifacts (Windows & Unix compatible)
clean:
    -powershell -Command "Remove-Item -Recycle -Force -ErrorAction SilentlyContinue .venv, __pycache__, .pytest_cache, .mypy_cache, .ruff_cache, node_modules, target, static_root, htmlcov"
    -powershell -Command "Get-ChildItem -Recurse -Include __pycache__ | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"
    -powershell -Command "Get-ChildItem -Recurse -Include *.pyc | Remove-Item -Force -ErrorAction SilentlyContinue"
    @echo ✅ Cleaned build artifacts (Recycled where possible)

# Clean and reinstall
reset:
    just clean
    just setup
