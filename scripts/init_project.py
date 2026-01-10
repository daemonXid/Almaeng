import argparse
import os
import random
import secrets
import shutil
import stat
import subprocess
from pathlib import Path


def setup_argparse():
    parser = argparse.ArgumentParser(description="Initialize a new project from the DAEMON template")
    parser.add_argument("new_name", help="The name of your new project (kebab-case recommended)")
    parser.add_argument(
        "--template-name", default="almaeng", help="The name of the template being used (default: almaeng)"
    )
    parser.add_argument("--skip-git", action="store_true", help="Skip Git initialization")
    parser.add_argument(
        "--reset-git", action="store_true", help="Delete existing .git and reinitialize (default: keep existing)"
    )
    return parser.parse_args()


def get_variants(name):
    """Generate kebab-case, snake_case, and UPPER-CASE-KEBAB variants."""
    kebab = name.lower().replace("_", "-")
    snake = name.lower().replace("-", "_")
    upper = name.upper().replace("_", "-")
    return kebab, snake, upper


def generate_secret_key():
    """Generate a secure Django SECRET_KEY."""
    chars = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"
    return "".join(secrets.choice(chars) for _ in range(50))


def generate_password():
    """Generate a secure random password."""
    return secrets.token_urlsafe(32)


def get_random_port(start, end, exclude=None):
    """Generate a random port within range, avoiding excluded ports."""
    if exclude is None:
        exclude = set()

    available = [p for p in range(start, end + 1) if p not in exclude]
    if not available:
        raise ValueError(f"No available ports in range {start}-{end}")

    return random.choice(available)


def replace_in_file(file_path, replacements):
    """Read a file and replace the strings."""
    if not file_path.exists():
        print(f"⚠️  Skipping: {file_path} (not found)")
        return

    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content

        for old, new in replacements.items():
            content = content.replace(old, new)

        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            print(f"✅ Updated: {file_path}")
        else:
            print(f"ℹ️  No changes: {file_path}")
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")


def create_env_file(base_dir, project_name, ports, secrets_dict):
    """Create .env file from .env.example with auto-generated values."""
    env_example = base_dir / ".env.example"
    env_file = base_dir / ".env"

    if not env_example.exists():
        print("⚠️  .env.example not found, skipping .env creation")
        return

    # Backup existing .env if it exists
    if env_file.exists():
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = base_dir / f".env.backup.{timestamp}"
        shutil.copy2(env_file, backup)
        print(f"📦 Backed up existing .env to {backup.name}")

    # Copy and update .env file
    shutil.copy2(env_example, env_file)

    env_replacements = {
        # Ports
        "APP_PORT=3500": f"APP_PORT={ports['app']}",
        "POSTGRES_PORT=5474": f"POSTGRES_PORT={ports['db']}",
        "REDIS_PORT=6436": f"REDIS_PORT={ports['redis']}",
        # Database
        "almaeng_db": f"{project_name}_db",
        "almaeng_user": f"{project_name}_user",
        # Secrets
        **secrets_dict,
    }

    replace_in_file(env_file, env_replacements)
    print("✅ Created .env with auto-generated ports and secrets")


def handle_remove_readonly(func, path, excinfo):
    """
    Error handler for shutil.rmtree that handles read-only files on Windows.
    Changes file permissions and retries deletion.
    """
    # Clear the read-only bit and retry the removal
    os.chmod(path, stat.S_IWRITE)
    func(path)


def update_readme(base_dir, project_name):
    """Clear README.md and add only project name."""
    readme = base_dir / "README.md"

    if not readme.exists():
        print("⚠️  README.md not found, skipping")
        return

    readme.write_text(f"# {project_name}\n", encoding="utf-8")
    print("✅ Updated README.md with project name")


def init_git(base_dir, skip_git=False, reset_git=False):
    """Initialize fresh Git repository or keep existing."""
    if skip_git:
        print("⏭️  Skipping Git initialization (--skip-git)")
        return

    git_dir = base_dir / ".git"

    try:
        if git_dir.exists():
            if reset_git:
                # Only remove .git if explicitly requested
                shutil.rmtree(git_dir, onexc=handle_remove_readonly)
                print("🗑️  Removed existing .git directory (--reset-git)")
                # Initialize new repository
                subprocess.run(["git", "init"], cwd=base_dir, check=True, capture_output=True)
                subprocess.run(["git", "add", "."], cwd=base_dir, check=True, capture_output=True)
                subprocess.run(
                    ["git", "commit", "-m", "Initial commit from ALMAENG template"],
                    cwd=base_dir,
                    check=True,
                    capture_output=True,
                )
                print("✅ Initialized fresh Git repository with initial commit")
            else:
                # Keep existing .git, just stage and commit changes
                print("📦 Keeping existing .git directory (use --reset-git to reinitialize)")
                subprocess.run(["git", "add", "."], cwd=base_dir, check=True, capture_output=True)
                subprocess.run(
                    ["git", "commit", "-m", "chore: initialize project with new name"],
                    cwd=base_dir,
                    check=False,  # May fail if no changes
                    capture_output=True,
                )
                print("✅ Staged and committed project changes")
        else:
            # No .git exists, create new
            subprocess.run(["git", "init"], cwd=base_dir, check=True, capture_output=True)
            subprocess.run(["git", "add", "."], cwd=base_dir, check=True, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", "Initial commit from ALMAENG template"],
                cwd=base_dir,
                check=True,
                capture_output=True,
            )
            print("✅ Initialized fresh Git repository with initial commit")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Git operation failed: {e}")
    except FileNotFoundError:
        print("⚠️  Git not found, skipping Git initialization")


def main():
    args = setup_argparse()
    new_name = args.new_name
    template_name = args.template_name

    # Generate variants for template and new name
    t_kebab, t_snake, t_upper = get_variants(template_name)
    n_kebab, n_snake, n_upper = get_variants(new_name)

    print(f"😈 Initializing new project: {n_kebab}")
    print(f"   (Template: {t_kebab})")
    print("-" * 60)

    # Clean up existing Docker infrastructure (if any) to avoid password mismatch in volumes
    base_dir = Path(__file__).resolve().parent.parent
    if (base_dir / "docker-compose.yml").exists():
        print("🐳 Cleaning up existing Docker infrastructure...")
        try:
            subprocess.run(["docker", "compose", "down", "-v"], cwd=base_dir, check=False, capture_output=True)
            print("✅ Docker volumes and containers cleaned up")
        except Exception:
            print("⚠️  Docker cleanup failed (is Docker running?), skipping...")
    print("-" * 60)

    # Generate random ports (넉넉한 범위로)
    used_ports = set()
    ports = {
        "app": get_random_port(3000, 9000, used_ports),  # App port
    }
    used_ports.add(ports["app"])

    ports["db"] = get_random_port(5430, 5530, used_ports)  # DB port (~100 range)
    used_ports.add(ports["db"])

    ports["redis"] = get_random_port(6370, 6470, used_ports)  # Redis port (~100 range)

    print("🎲 Generated random ports:")
    print(f"   App:   {ports['app']}")
    print(f"   DB:    {ports['db']}")
    print(f"   Redis: {ports['redis']}")
    print("-" * 60)

    # Generate secrets
    secret_key = generate_secret_key()
    db_password = generate_password()

    # We'll dynamically find and replace SECRET_KEY and POSTGRES_PASSWORD placeholders
    print("🔐 Generated secure secrets:")
    print(f"   Django SECRET_KEY: {secret_key[:20]}...")
    print(f"   DB Password: {db_password[:20]}...")
    print("-" * 60)

    # Name replacements
    replacements = {
        t_kebab: n_kebab,
        t_snake: n_snake,
        t_upper: n_upper,
    }

    # Port replacements (for all files) - update APP_PORT variable values
    port_replacements = {
        "APP_PORT=3500": f"APP_PORT={ports['app']}",
        ":3500": f":{ports['app']}",  # For URLs like http://127.0.0.1:3500
        "POSTGRES_PORT=5474": f"POSTGRES_PORT={ports['db']}",
        "REDIS_PORT=6436": f"REDIS_PORT={ports['redis']}",
    }

    # Database name replacements
    db_replacements = {
        "almaeng_db": f"{n_snake}_db",
        "almaeng_user": f"{n_snake}_user",
        "ALMAENG_DB": f"{n_upper.replace('-', '_')}_DB",
        "ALMAENG_USER": f"{n_upper.replace('-', '_')}_USER",
    }

    # Combine all replacements
    all_replacements = {**replacements, **port_replacements, **db_replacements}

    # Define files to process
    base_dir = Path(__file__).resolve().parent.parent
    files_to_process = [
        # Project Config
        "pyproject.toml",
        "package.json",
        "Justfile",
        ".env.example",
        "Dockerfile",
        "docker-compose.yml",
        "docker-compose.prod.yml",
        "main.py",
        # Scripts
        "scripts/create_domain.py",
        "scripts/init_project.py",
        # Backend Config
        "backend/config/settings.py",
        "backend/config/urls.py",
        "backend/tests.py",
        # Static Assets (Branding)
        "backend/static/sw.js",
        "backend/static/js/vendor-entry.js",
        "backend/static/manifest.json",
        # Templates (Branding)
        "backend/templates/base.html",
        "backend/templates/_header.html",
        "backend/templates/_footer.html",
        "backend/templates/_metadata.html",
        "backend/templates/404.html",
        "backend/templates/500.html",
        # Core & Health Domains
        "backend/domains/core/apps.py",
        "backend/domains/health/interface.py",
        "backend/domains/health/pages/status/views.py",
        "backend/domains/health/pages/status/status.html",
    ]

    print("📝 Updating project files...")
    for file_rel_path in files_to_process:
        replace_in_file(base_dir / file_rel_path, all_replacements)

    print("-" * 60)

    # Create .env file with secrets
    print("🔧 Creating .env file...")
    secrets_for_env = {}
    # Try to find SECRET_KEY and POSTGRES_PASSWORD placeholders in .env.example
    env_example = base_dir / ".env.example"
    if env_example.exists():
        content = env_example.read_text(encoding="utf-8")
        if "SECRET_KEY=" in content:
            # Find the placeholder value
            for line in content.split("\n"):
                if line.startswith("SECRET_KEY="):
                    old_key = line.split("=", 1)[1].strip()
                    if old_key:
                        secrets_for_env[old_key] = secret_key
                    break
        if "POSTGRES_PASSWORD=" in content:
            for line in content.split("\n"):
                if line.startswith("POSTGRES_PASSWORD="):
                    old_pwd = line.split("=", 1)[1].strip()
                    if old_pwd:
                        secrets_for_env[old_pwd] = db_password
                    break

    create_env_file(base_dir, n_snake, ports, secrets_for_env)

    print("-" * 60)

    # Update README.md
    print("📄 Updating README.md...")
    update_readme(base_dir, n_kebab)

    print("-" * 60)

    # Initialize Git
    print("🎯 Initializing Git repository...")
    init_git(base_dir, args.skip_git, args.reset_git)

    print("-" * 60)
    print("✨ Project initialization complete!")
    print()
    print(f"🚀 Your new project '{n_kebab}' is ready!")
    print()
    print("📋 Configuration Summary:")
    print(f"   • App Port:      {ports['app']}")
    print(f"   • Database Port: {ports['db']}")
    print(f"   • Redis Port:    {ports['redis']}")
    print(f"   • Database Name: {n_snake}_db")
    print(f"   • Database User: {n_snake}_user")
    print()
    print("🔐 Security:")
    print("   • Django SECRET_KEY: ✅ Generated")
    print("   • DB Password:       ✅ Generated")
    print("   • .env file:         ✅ Created")
    print()
    print("📌 Next steps:")
    print("   1. Review .env file for any additional configuration")
    print("   2. just setup")
    print("   3. just dev")
    print()


if __name__ == "__main__":
    main()
