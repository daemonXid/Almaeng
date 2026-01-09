import json
import re
from pathlib import Path

# --- Configuration ---
BASE_DIR = Path(__file__).resolve().parent.parent
PYPROJECT_PATH = BASE_DIR / "pyproject.toml"
PACKAGE_JSON_PATH = BASE_DIR / "package.json"
DOCKER_COMPOSE_PATH = BASE_DIR / "docker-compose.yml"
DOCKER_PROD_PATH = BASE_DIR / "docker-compose.prod.yml"
README_PATH = BASE_DIR / "README.md"
DOMAINS_DIR = BASE_DIR / "backend" / "domains"


def get_project_slug():
    """Extract project slug from pyproject.toml or folder name."""
    if PYPROJECT_PATH.exists():
        content = PYPROJECT_PATH.read_text(encoding="utf-8")
        match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)
    return BASE_DIR.name.lower().replace(" ", "-")


def get_active_domains():
    """Scan backend/domains/ for active Django apps."""
    domains = []
    if not DOMAINS_DIR.exists():
        return domains

    # Recursive scan similar to settings.py
    def scan(directory, prefix=""):
        for item in directory.iterdir():
            if not item.is_dir() or item.name.startswith("_"):
                continue
            if (item / "apps.py").exists():
                domains.append(f"{prefix}{item.name}")
            else:
                # One level deeper only for clarity
                if prefix == "":
                    scan(item, f"{item.name} > ")

    scan(DOMAINS_DIR)
    return sorted(domains)


def sync_package_json(slug):
    """Update package.json name to match slug."""
    if not PACKAGE_JSON_PATH.exists():
        return

    try:
        data = json.loads(PACKAGE_JSON_PATH.read_text(encoding="utf-8"))
        data["name"] = f"{slug}-frontend"
        PACKAGE_JSON_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        print(f"✅ Synced package.json (name: {data['name']})")
    except Exception as e:
        print(f"❌ Error syncing package.json: {e}")


def sync_docker_compose(slug):
    """Update container names in docker-compose files."""
    slug_snake = slug.replace("-", "_")

    files = [DOCKER_COMPOSE_PATH, DOCKER_PROD_PATH]
    for file_path in files:
        if not file_path.exists():
            continue

        content = file_path.read_text(encoding="utf-8")
        # Replace container_name: ...
        content = re.sub(r"container_name:\s*[^\s]+", f"container_name: {slug_snake}_app", content, count=1)
        # Handle db/redis if present in the same file
        content = re.sub(r"container_name:\s*[^\s]+_postgres", f"container_name: {slug_snake}_postgres", content)
        content = re.sub(r"container_name:\s*[^\s]+_redis", f"container_name: {slug_snake}_redis", content)

        file_path.write_text(content, encoding="utf-8")
        print(f"✅ Synced {file_path.name} container names")


def sync_readme_inventory(domains):
    """Update README.md with an inventory of active domains."""
    if not README_PATH.exists():
        return

    content = README_PATH.read_text(encoding="utf-8")

    # Define markers
    start_marker = "<!-- DOMAINS_START -->"
    end_marker = "<!-- DOMAINS_END -->"

    inventory_text = f"\n\n### 📦 Active Domains ({len(domains)})\n\n"
    for d in domains:
        inventory_text += f"- **{d}**\n"
    inventory_text += "\n"

    if start_marker in content and end_marker in content:
        pattern = re.compile(f"{re.escape(start_marker)}.*?{re.escape(end_marker)}", re.DOTALL)
        new_content = pattern.sub(f"{start_marker}{inventory_text}{end_marker}", content)
        README_PATH.write_text(new_content, encoding="utf-8")
        print("✅ Updated README.md domain inventory")
    else:
        # If markers don't exist, append them to the Architecture section or end of file
        marker_block = f"\n\n{start_marker}{inventory_text}{end_marker}\n"
        if "## 🏗️ v5.0 Architecture" in content:
            # Insert after the architecture tree
            content = content.replace("```\n\n---", f"```\n{marker_block}\n---")
        else:
            content += marker_block
        README_PATH.write_text(content, encoding="utf-8")
        print("✅ Added domain inventory markers to README.md")


def main():
    print("😈 DAEMON Project Synchronization...")
    slug = get_project_slug()
    domains = get_active_domains()

    print(f"Slug: {slug}")
    print(f"Active Domains: {', '.join(domains)}")

    sync_package_json(slug)
    sync_docker_compose(slug)
    sync_readme_inventory(domains)
    print("✨ Sync complete!")


if __name__ == "__main__":
    main()
