"""
🧪 ALMAENG Tests

Test suite for core domains and AI providers.
"""

import pytest


@pytest.mark.django_db
class TestHealthModule:
    """Tests for health check endpoints."""

    def test_health_endpoint(self, client):
        """Test basic health endpoint."""
        response = client.get("/health/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

    def test_liveness_endpoint(self, client):
        """Test liveness probe."""
        response = client.get("/health/live/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"

    def test_readiness_endpoint(self, client):
        """Test readiness probe (checks DB + cache)."""
        response = client.get("/health/ready/")
        # May be 200 or 503 depending on services
        assert response.status_code in [200, 503]
        data = response.json()
        assert "checks" in data


@pytest.mark.django_db
class TestCoreModule:
    """Tests for core pages."""

    def test_home_page(self, client):
        """Test that home page loads."""
        response = client.get("/")
        assert response.status_code == 200

    def test_search_page(self, client):
        """Test search page."""
        response = client.get("/search/")
        assert response.status_code == 200


class TestAIProviders:
    """Tests for AI provider abstraction (Gemini only)."""

    def test_provider_imports(self):
        """Test that Gemini provider can be imported."""
        from domains.ai.service.providers.interface import PROVIDERS

        assert "gemini" in PROVIDERS
        assert len(PROVIDERS) == 1  # Only Gemini

    def test_gemini_provider_init(self):
        """Test Gemini provider initialization."""
        from domains.ai.service.providers.gemini import GeminiProvider

        provider = GeminiProvider()
        assert provider.provider_name == "gemini"
        # Without API key, should not be available
        if not provider.api_key:
            assert provider.is_available() is False

    def test_get_ai_client(self):
        """Test that get_ai_client returns Gemini provider."""
        from domains.ai.service.providers.interface import get_ai_client

        client = get_ai_client()
        assert hasattr(client, "complete")
        assert hasattr(client, "complete_structured")
        assert hasattr(client, "embed")
        assert client.provider_name == "gemini"


class TestHealthInterface:
    """Tests for health interface Pydantic schemas."""

    def test_health_interface_pydantic(self):
        """Test that health interface returns Pydantic model."""
        from domains.base.health.interface import HealthStatus, check_health

        result = check_health()
        assert isinstance(result, HealthStatus)
        assert "database" in result.checks
        assert "cache" in result.checks
