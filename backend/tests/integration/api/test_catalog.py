"""
Integration tests for catalog API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from datetime import date


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


class TestDatasetsEndpoint:
    """Test dataset discovery"""
    
    def test_list_all_datasets(self, client: TestClient):
        """Test GET /api/datasets returns all datasets"""
        response = client.get("/api/datasets")
        assert response.status_code == 200
        data = response.json()
        assert "datasets" in data
        assert "count" in data
        
        datasets = data["datasets"]
        assert len(datasets) > 0
        assert data["count"] == len(datasets)
    
    def test_filter_datasets_by_category(self, client: TestClient):
        """Test filtering datasets by category"""
        response = client.get("/api/datasets?subject=moon")
        assert response.status_code == 200
        data = response.json()
        datasets = data["datasets"]
        
        # All returned datasets should be for moon
        for dataset in datasets:
            assert dataset["subject"] == "moon"
    
    def test_filter_datasets_by_source(self, client: TestClient):
        """Test filtering datasets by source"""
        response = client.get("/api/datasets?source_id=nasa_gibs")
        assert response.status_code == 200
        data = response.json()
        datasets = data["datasets"]
        
        # All returned datasets should be from NASA GIBS
        for dataset in datasets:
            assert dataset["source_id"] == "nasa_gibs"
    
    def test_filter_datasets_by_time_series(self, client: TestClient):
        """Test filtering datasets by time series support"""
        response = client.get("/api/datasets?supports_time_series=true")
        assert response.status_code == 200
        data = response.json()
        datasets = data["datasets"]
        
        # All returned datasets should support time series
        for dataset in datasets:
            assert dataset["supports_time_series"] is True
    
    def test_get_specific_map(self, client: TestClient):
        """Test GET /api/datasets/{dataset_id}"""
        response = client.get("/api/datasets/viirs_snpp")
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == "viirs_snpp"
        assert data["name"] == "VIIRS SNPP"
        assert data["category"] == "planets"
        assert data["subject"] == "earth"
        assert data["supports_time_series"] is True
        assert len(data["variants"]) == 2  # True color and false color
    
    def test_get_nonexistent_map(self, client: TestClient):
        """Test getting a map that doesn't exist"""
        response = client.get("/api/datasets/nonexistent_map")
        assert response.status_code == 404


class TestVariantsEndpoint:
    """Test variant endpoints"""
    
    def test_get_map_variants(self, client: TestClient):
        """Test GET /api/datasets/{id}/variants"""
        response = client.get("/api/datasets/viirs_snpp/variants")
        assert response.status_code == 200
        data = response.json()
        
        assert "variants" in data
        assert "dataset_id" in data
        assert len(data["variants"]) == 2
    
    def test_get_specific_variant(self, client: TestClient):
        """Test GET /api/datasets/{id}/variants/{variant_id}"""
        response = client.get("/api/datasets/viirs_snpp/variants/true_color")
        assert response.status_code == 200
        data = response.json()
        
        assert "variant" in data
        variant = data["variant"]
        assert variant["id"] == "true_color"
        assert "tile_url" in variant
        assert "thumbnail_url" in variant
    
    def test_get_variant_with_date(self, client: TestClient):
        """Test getting variant with date parameter"""
        response = client.get("/api/datasets/viirs_snpp/variants/true_color?date_param=2025-10-04")
        assert response.status_code == 200
        data = response.json()
        
        variant = data["variant"]
        assert "2025-10-04" in variant["tile_url"]
        assert variant["selected_date"] == "2025-10-04"
    
    def test_get_static_map_variant(self, client: TestClient):
        """Test getting variant for static (non-time-series) map"""
        response = client.get("/api/datasets/mars_viking/variants/colorized")
        assert response.status_code == 200
        data = response.json()
        
        variant = data["variant"]
        assert variant["id"] == "colorized"
        assert variant["selected_date"] is None  # No date for static maps
