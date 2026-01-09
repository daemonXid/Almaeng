"""
🧪 DAEMON-ONE Test Configuration

This module provides pytest fixtures and configuration for testing DAEMON-ONE
and any modules copied from DAEMON-ABYSS.

Usage:
    # In your test file
    def test_create_user(user, api_client):
        response = api_client.post("/api/users/", {"email": "new@example.com"})
        assert response.status_code == 201

Fixtures provided:
    - db_access: Enable database access for tests
    - user: Create a test user
    - admin_user: Create an admin user
    - api_client: Django test client with auth
    - auth_headers: JWT headers for API calls

Run tests:
    just test
    just test-cov  # With coverage
"""

from collections.abc import Generator
from typing import Any

import pytest

# =============================================================================
# 📦 Django Configuration
# =============================================================================


@pytest.fixture(scope="session")
def django_db_setup():
    """
    Configure Django database for testing.
    Uses pytest-django's database fixture.
    """
    pass


@pytest.fixture
def db_access(db):
    """Enable database access for a test."""
    pass


# =============================================================================
# 👤 User Fixtures
# =============================================================================


@pytest.fixture
def user(db) -> Generator[Any, None, None]:
    """
    Create a standard test user.

    Usage:
        def test_user_profile(user):
            assert user.email == "test@example.com"
    """
    from django.contrib.auth import get_user_model

    User = get_user_model()
    test_user = User.objects.create_user(
        email="test@example.com",
        password="testpassword123",
        first_name="Test",
        last_name="User",
    )
    yield test_user

    # Cleanup
    test_user.delete()


@pytest.fixture
def admin_user(db) -> Generator[Any, None, None]:
    """
    Create an admin/superuser for testing.

    Usage:
        def test_admin_access(admin_user):
            assert admin_user.is_staff
    """
    from django.contrib.auth import get_user_model

    User = get_user_model()
    admin = User.objects.create_superuser(
        email="admin@example.com",
        password="adminpassword123",
    )
    yield admin

    # Cleanup
    admin.delete()


@pytest.fixture
def user_with_role(db):
    """
    Factory fixture to create users with specific roles.

    Usage:
        def test_team_manager(user_with_role):
            manager = user_with_role("team_manager")
            assert has_permission(manager, "shorts:create")
    """
    from django.contrib.auth import get_user_model

    User = get_user_model()
    created_users = []

    def _create_user(role: str, email: str | None = None):
        email = email or f"{role}@example.com"
        user = User.objects.create_user(
            email=email,
            password="testpassword123",
        )
        # Set role (adjust based on your User model)
        if hasattr(user, "roles"):
            user.roles = [role]
            user.save()
        created_users.append(user)
        return user

    yield _create_user

    # Cleanup
    for user in created_users:
        user.delete()


# =============================================================================
# 🔌 API Client Fixtures
# =============================================================================


@pytest.fixture
def api_client():
    """
    Django test client for API testing.

    Usage:
        def test_api_endpoint(api_client, user):
            api_client.force_login(user)
            response = api_client.get("/api/users/me/")
            assert response.status_code == 200
    """
    from django.test import Client

    return Client()


@pytest.fixture
def authenticated_client(api_client, user):
    """
    Pre-authenticated API client.

    Usage:
        def test_protected_endpoint(authenticated_client):
            response = authenticated_client.get("/api/protected/")
            assert response.status_code == 200
    """
    api_client.force_login(user)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """
    Admin-authenticated API client.

    Usage:
        def test_admin_endpoint(admin_client):
            response = admin_client.get("/admin/")
            assert response.status_code == 200
    """
    api_client.force_login(admin_user)
    return api_client


# =============================================================================
# 🧠 AI/CORTEX Fixtures
# =============================================================================


@pytest.fixture
def mock_genai(mocker):
    """
    Mock GenAI client for testing without API calls.

    Usage:
        def test_ai_analysis(mock_genai):
            mock_genai.return_value = {"summary": "Test", "score": 0.9}
            # Your test code
    """
    from modules.daemon.cortex import GenAIClient

    mock = mocker.patch.object(GenAIClient, "complete")
    mock.return_value.text = '{"summary": "Mocked response", "score": 0.9}'
    return mock


@pytest.fixture
def mock_vision(mocker):
    """
    Mock VisionAI for testing without loading models.

    Usage:
        def test_pose_detection(mock_vision):
            mock_vision.detect_pose.return_value = PoseResult(...)
    """
    from modules.daemon.cortex import VisionAI

    mock = mocker.patch.object(VisionAI, "detect_pose")
    return mock


# =============================================================================
# 🗄️ Database Fixtures
# =============================================================================


@pytest.fixture
def transactional_db(db, transactional_db):
    """
    Use transactional database access.
    Rolls back after each test.
    """
    pass


# =============================================================================
# 🔧 Utility Fixtures
# =============================================================================


@pytest.fixture
def sample_image():
    """
    Create a sample image for testing.

    Usage:
        def test_image_upload(sample_image, api_client):
            response = api_client.post("/api/upload/", {"image": sample_image})
    """
    import io

    from PIL import Image

    # Create a simple test image
    img = Image.new("RGB", (100, 100), color="red")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    buffer.name = "test_image.png"

    return buffer


@pytest.fixture
def temp_file(tmp_path):
    """
    Create a temporary file for testing.

    Usage:
        def test_file_processing(temp_file):
            file = temp_file("data.json", '{"key": "value"}')
    """

    def _create_file(name: str, content: str = ""):
        file_path = tmp_path / name
        file_path.write_text(content)
        return file_path

    return _create_file


# =============================================================================
# 📋 Configuration
# =============================================================================


def pytest_configure(config):
    """Pytest configuration hook."""
    # Register custom markers
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "ai: marks tests that require AI models")


# =============================================================================
# 📦 Module Exports (for documentation)
# =============================================================================

__all__ = [
    "admin_client",
    "admin_user",
    "api_client",
    "authenticated_client",
    "mock_genai",
    "mock_vision",
    "sample_image",
    "temp_file",
    "user",
    "user_with_role",
]
