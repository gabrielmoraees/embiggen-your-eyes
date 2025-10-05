"""
Integration tests for catalog API endpoints (discovery only)
"""
import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self, client: TestClient):
        """Test GET /api/health returns healthy status"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
    
    def test_root_endpoint(self, client: TestClient):
        """Test GET / returns API info"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert data["version"] == "1.0.0"


class TestCategoriesEndpoint:
    """Test categories discovery"""
    
    def test_list_categories(self, client: TestClient):
        """Test GET /api/categories"""
        response = client.get("/api/categories")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        
        categories = data["categories"]
        category_ids = [c["id"] for c in categories]
        assert "planets" in category_ids
        assert "moons" in category_ids


class TestSourcesEndpoint:
    """Test map sources discovery"""
    
    def test_list_all_sources(self, client: TestClient):
        """Test GET /api/sources returns all sources"""
        response = client.get("/api/sources")
        assert response.status_code == 200
        data = response.json()
        assert "sources" in data
        
        sources = data["sources"]
        assert len(sources) > 0
        
        # Check source structure
        for source in sources:
            assert "id" in source
            assert "name" in source
            assert "attribution" in source
    
    def test_filter_sources_by_category(self, client: TestClient):
        """Test filtering sources by category"""
        response = client.get("/api/sources?subject=moon")
        assert response.status_code == 200
        data = response.json()
        sources = data["sources"]
        
        # Should have sources that provide moon data
        assert len(sources) > 0