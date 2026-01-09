#!/usr/bin/env python3
"""
🏭 Domain Factory - Scaffolding Script

Creates a new domain with all the standard files following ALMAENG architecture (Flattened Domains).

Usage:
    python scripts/create_domain.py domain_name
    python scripts/create_domain.py shop --multi-feature product cart payment

Examples:
    python scripts/create_domain.py analytics
    python scripts/create_domain.py shop --multi-feature cart payment
"""

import argparse
import sys
from pathlib import Path

# Project paths
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DOMAINS_DIR = PROJECT_ROOT / "backend" / "domains"


def create_file(path: Path, content: str) -> None:
    """Create a file with content, creating parent directories if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")
    print(f"  ✅ Created: {path.relative_to(PROJECT_ROOT)}")


def create_single_feature_domain(domain_name: str) -> None:
    """Create a single-feature domain."""
    domain_dir = DOMAINS_DIR / domain_name

    if domain_dir.exists():
        print(f"❌ Domain '{domain_name}' already exists!")
        sys.exit(1)

    print(f"😈 Creating domain: {domain_name}")

    # __init__.py
    create_file(
        domain_dir / "__init__.py",
        f'''
"""
📦 {domain_name.title()} Domain

Copy this domain from DAEMON-ABYSS or create via:
    just new-domain {domain_name}
"""
''',
    )

    # apps.py
    class_name = domain_name.title().replace("_", "")
    create_file(
        domain_dir / "apps.py",
        f'''
"""
😈 {domain_name.title()} Domain - Django App Configuration
"""

from django.apps import AppConfig


class {class_name}Config(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "domains.{domain_name}"
    verbose_name = "{domain_name.replace("_", " ").title()}"

    def ready(self):
        """Import receivers to register signal handlers."""
        try:
            from . import receivers  # noqa: F401
        except ImportError:
            pass
''',
    )

    # interface.py with Pydantic
    create_file(
        domain_dir / "interface.py",
        f'''
"""
🔑 Public Interface - {domain_name.title()} Domain

Other domains should ONLY import from here, never from internal files.
Uses Pydantic schemas for type-safe inter-domain communication.

Usage:
    from domains.{domain_name}.interface import (
        # your exports here
    )
"""

from __future__ import annotations

from pydantic import BaseModel
from typing import Optional


# =============================================================================
# 📋 Pydantic Schemas
# =============================================================================

class {class_name}Schema(BaseModel):
    """Schema for {domain_name} data transfer."""
    id: int
    name: str
    # Add fields as needed

    class Config:
        from_attributes = True


# =============================================================================
# 📖 Read Operations (from selectors.py)
# =============================================================================

# from .selectors import (
#     # Export read functions here
# )


# =============================================================================
# 🔧 Write Operations (from services.py)
# =============================================================================

# from .services import (
#     # Export write functions here
# )


# =============================================================================
# 📋 Explicit Public API
# =============================================================================

__all__ = [
    "{class_name}Schema",
    # Add public functions
]
''',
    )

    # models.py
    create_file(
        domain_dir / "models.py",
        f'''
"""
📊 Models - {domain_name.title()} Domain
"""

from django.db import models
# from domains.base.core.interface import TimestampedModel, SoftDeleteModel


# class Example{class_name}(models.Model):
#     """Example model for {domain_name}."""
#
#     name = models.CharField(max_length=100)
#     description = models.TextField(blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         db_table = "{domain_name}_example"
#         verbose_name = "{domain_name.title()} Example"
''',
    )

    # services.py
    create_file(
        domain_dir / "services.py",
        f'''
"""
🔧 Services - Write Operations (CUD)

Business logic for creating, updating, deleting data.
Use @transaction.atomic for data consistency.

Usage:
    from domains.{domain_name}.services import create_example
"""

from typing import Optional
from django.db import transaction


# @transaction.atomic
# def create_example(*, name: str, description: str = "") -> Example:
#     """
#     Create a new example.
#
#     Args:
#         name: Example name
#         description: Optional description
#
#     Returns:
#         Created Example instance
#     """
#     return Example.objects.create(name=name, description=description)
''',
    )

    # selectors.py
    create_file(
        domain_dir / "selectors.py",
        f'''
"""
📖 Selectors - Read Operations (R)

Query logic for reading data.
Optimize with select_related, prefetch_related.

Usage:
    from domains.{domain_name}.selectors import get_example_by_id
"""

from typing import List, Optional


# def get_example_by_id(*, example_id: int) -> Optional[Example]:
#     """
#     Get example by ID.
#
#     Args:
#         example_id: Example primary key
#
#     Returns:
#         Example instance or None
#     """
#     try:
#         return Example.objects.get(id=example_id)
#     except Example.DoesNotExist:
#         return None
''',
    )

    # pages/index/views.py (Vertical Slice)
    create_file(
        domain_dir / "pages" / "index" / "views.py",
        f'''
"""
🌐 Index Page - {domain_name.title()} Domain

HTMX-friendly views that return HTML fragments.
"""

from django.shortcuts import render
from django.http import HttpRequest, HttpResponse


def index(request: HttpRequest) -> HttpResponse:
    """Main page for {domain_name}."""
    return render(request, "{domain_name}/pages/index/index.html", {{}})
''',
    )

    # urls.py
    create_file(
        domain_dir / "urls.py",
        f'''
"""
🔗 URL Configuration - {domain_name.title()} Domain
"""

from django.urls import path
from .pages.index import views

app_name = "{domain_name}"

urlpatterns = [
    path("", views.index, name="index"),
]
''',
    )

    # admin.py
    create_file(
        domain_dir / "admin.py",
        f'''
"""
🔧 Admin Configuration - {domain_name.title()} Domain
"""

from django.contrib import admin

# from .models import Example{class_name}
#
# @admin.register(Example{class_name})
# class Example{class_name}Admin(admin.ModelAdmin):
#     list_display = ["id", "name", "created_at"]
#     search_fields = ["name"]
#     list_filter = ["created_at"]
''',
    )

    # migrations/__init__.py
    create_file(domain_dir / "migrations" / "__init__.py", "")

    # pages/index/index.html (Vertical Slice)
    create_file(
        domain_dir / "pages" / "index" / "index.html",
        f"""
{{% extends "base.html" %}}

{{% block title %}}{domain_name.replace("_", " ").title()} | ALMAENG{{% endblock %}}

{{% block content %}}
<section style="padding: 4rem 0;">
    <div class="container" style="max-width: 800px;">
        <div class="glass-panel" style="padding: 3rem; text-align: center;">
            <span style="color: var(--accent); font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.1em;">
                Domain Context
            </span>
            <h1 class="gradient-text" style="font-size: 3rem; margin-top: 1rem; margin-bottom: 1.5rem;">
                {domain_name.replace("_", " ").title()}
            </h1>
            <p style="color: var(--muted); line-height: 1.8;">
                Welcome to the <strong>{domain_name}</strong> domain.
                This self-contained vertical slice is ready for business logic.
            </p>
        </div>
    </div>
</section>
{{% endblock %}}
""",
    )

    # HTMX fragment template
    create_file(
        domain_dir / "pages" / "index" / "_list.html",
        f'''
{{# HTMX Fragment - Use with hx-target #}}
<div id="{domain_name}-list">
    {{% for item in items %}}
    <div class="glass-panel" style="padding: 1rem; margin-bottom: 0.5rem;">
        {{{{ item.name }}}}
    </div>
    {{% empty %}}
    <p style="color: var(--muted);">No items yet.</p>
    {{% endfor %}}
</div>
''',
    )

    # static
    create_file(
        domain_dir / "static" / domain_name / "css" / "style.css",
        f"""
/* {domain_name.title()} Domain Styles */

.{domain_name}-container {{
    /* Domain-specific styles */
}}
""",
    )

    create_file(
        domain_dir / "static" / domain_name / "js" / "main.js",
        f"""
// {domain_name.title()} Domain JavaScript

document.addEventListener('DOMContentLoaded', function() {{
    console.log('😈 {domain_name} domain loaded');
}});
""",
    )

    print(f"\n✨ Domain '{domain_name}' created successfully!")
    print(f"📁 Location: {domain_dir.relative_to(PROJECT_ROOT)}")
    print("\n📋 Next steps:")
    print("  1. Restart server: just dev")
    print("  2. Add URL to config/urls.py:")
    print(f'     path("{domain_name}/", include("domains.{domain_name}.urls")),')
    print("  3. Run migrations: just mig")


def create_multi_feature_domain(domain_name: str, features: list[str]) -> None:
    """Create a multi-feature domain with sub-apps."""
    domain_dir = DOMAINS_DIR / domain_name

    if domain_dir.exists():
        print(f"❌ Domain '{domain_name}' already exists!")
        sys.exit(1)

    print(f"😈 Creating multi-feature domain: {domain_name}")
    print(f"   Features: {', '.join(features)}")

    # Root __init__.py
    create_file(
        domain_dir / "__init__.py",
        f'''
"""
📦 {domain_name.title()} Domain (Multi-Feature)

Features: {", ".join(features)}

Copy this domain from DAEMON-ABYSS.
"""
''',
    )

    # Root interface.py
    interface_imports = "\n".join([f"# from .{feat}.services import ..." for feat in features])
    create_file(
        domain_dir / "interface.py",
        f'''
"""
🔑 Public Interface - {domain_name.title()} Domain

Aggregates public APIs from all features.
"""

{interface_imports}

__all__ = [
    # List all public functions from all features
]
''',
    )

    # Create each feature
    for feature in features:
        feature_dir = domain_dir / feature
        class_name = feature.title().replace("_", "")

        create_file(feature_dir / "__init__.py", "")

        create_file(
            feature_dir / "apps.py",
            f'''
from django.apps import AppConfig


class {class_name}Config(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "domains.{domain_name}.{feature}"
    verbose_name = "{domain_name.title()} - {feature.title()}"
''',
        )

        create_file(
            feature_dir / "models.py",
            """
from django.db import models
""",
        )

        create_file(
            feature_dir / "services.py",
            """
from django.db import transaction
""",
        )

        create_file(
            feature_dir / "selectors.py",
            """
from typing import List, Optional
""",
        )

        create_file(feature_dir / "migrations" / "__init__.py", "")

        create_file(
            feature_dir / "templates" / domain_name / feature / "index.html",
            f"""
{{% extends "base.html" %}}
{{% block content %}}<h1 class="gradient-text">{feature.title()}</h1>{{% endblock %}}
""",
        )

    print(f"\n✨ Multi-feature domain '{domain_name}' created!")
    print("\n📋 Add to INSTALLED_APPS (auto-discovered):")
    for feature in features:
        print(f"    domains.{domain_name}.{feature}")


def main():
    parser = argparse.ArgumentParser(description="🏭 Create a new ALMAENG domain")
    parser.add_argument("domain_name", help="Name of the domain (snake_case)")
    parser.add_argument(
        "--multi-feature",
        "-m",
        nargs="+",
        metavar="FEATURE",
        help="Create multi-feature domain with specified features",
    )

    args = parser.parse_args()

    # Validate domain name
    if not args.domain_name.replace("_", "").isalnum():
        print("❌ Invalid domain name. Use snake_case (e.g., my_domain)")
        sys.exit(1)

    # Reserved names
    if args.domain_name in ["domains", "core", "common", "config"]:
        print(f"❌ '{args.domain_name}' is a reserved domain name.")
        sys.exit(1)

    if args.multi_feature:
        create_multi_feature_domain(args.domain_name, args.multi_feature)
    else:
        create_single_feature_domain(args.domain_name)


if __name__ == "__main__":
    main()
