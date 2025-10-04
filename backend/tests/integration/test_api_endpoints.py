"""
Integration tests for API endpoints
Tests the API endpoints with the test client
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


class TestCelestialBodiesEndpoint:
    """Test celestial bodies discovery"""
    
    def test_list_categories(self, client: TestClient):
        """Test GET /api/categories"""
        response = client.get("/api/categories")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        
        bodies = data["categories"]
        body_ids = [b["id"] for b in bodies]
        assert "planets" in body_ids
        assert "planets" in body_ids  # Mars is a planet
        assert "moons" in body_ids
        assert "planets" in body_ids  # Mercury is a planet


class TestSourcesEndpoint:
    """Test map sources discovery"""
    
    def test_list_all_sources(self, client: TestClient):
        """Test GET /api/sources"""
        response = client.get("/api/sources")
        assert response.status_code == 200
        data = response.json()
        assert "sources" in data
        
        sources = data["sources"]
        assert len(sources) > 0
        
        # Check first source has required fields
        source = sources[0]
        assert "id" in source
        assert "name" in source
        assert "description" in source
        assert "attribution" in source
    
    def test_filter_sources_by_category(self, client: TestClient):
        """Test filtering sources by celestial body"""
        response = client.get("/api/sources?subject=earth")
        assert response.status_code == 200
        data = response.json()
        
        # Should return sources that have Earth datasets
        sources = data["sources"]
        assert len(sources) > 0


class TestMapsEndpoint:
    """Test datasets discovery and details"""
    
    def test_list_all_datasets(self, client: TestClient):
        """Test GET /api/datasets"""
        response = client.get("/api/datasets")
        assert response.status_code == 200
        data = response.json()
        assert "datasets" in data
        assert "count" in data
        assert data["count"] > 0
        
        # Check first map has required fields
        dataset = data["datasets"][0]
        assert "id" in dataset
        assert "name" in dataset
        assert "source_id" in dataset
        assert "category" in dataset
        assert "variants" in dataset
        assert len(dataset["variants"]) > 0
    
    def test_filter_datasets_by_category(self, client: TestClient):
        """Test filtering datasets by celestial body"""
        response = client.get("/api/datasets?subject=moon")
        assert response.status_code == 200
        data = response.json()
        
        datasets = data["datasets"]
        assert len(datasets) == 2  # We have 2 Moon datasets
        
        for dataset in datasets:
            assert dataset["subject"] == "moon"
    
    def test_filter_datasets_by_source(self, client: TestClient):
        """Test filtering datasets by source"""
        response = client.get("/api/datasets?source_id=nasa_gibs")
        assert response.status_code == 200
        data = response.json()
        
        datasets = data["datasets"]
        for dataset in datasets:
            assert dataset["source_id"] == "nasa_gibs"
    
    def test_filter_datasets_by_time_series(self, client: TestClient):
        """Test filtering datasets by time-series support"""
        response = client.get("/api/datasets?supports_time_series=true")
        assert response.status_code == 200
        data = response.json()
        
        datasets = data["datasets"]
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
    """Test map variants endpoints"""
    
    def test_get_map_variants(self, client: TestClient):
        """Test GET /api/datasets/{dataset_id}/variants"""
        response = client.get("/api/datasets/viirs_snpp/variants")
        assert response.status_code == 200
        data = response.json()
        
        assert "dataset_id" in data
        assert "dataset_name" in data
        assert "variants" in data
        assert len(data["variants"]) == 2
        
        # Check variant structure
        variant = data["variants"][0]
        assert "id" in variant
        assert "name" in variant
        assert "tile_url_template" in variant
        assert "thumbnail_url" in variant
    
    def test_get_specific_variant(self, client: TestClient):
        """Test GET /api/datasets/{dataset_id}/variants/{variant_id}"""
        response = client.get("/api/datasets/viirs_snpp/variants/true_color")
        assert response.status_code == 200
        data = response.json()
        
        assert "dataset_id" in data
        assert "variant" in data
        variant = data["variant"]
        assert variant["id"] == "true_color"
        assert "tile_url" in variant
        assert "selected_date" in variant
    
    def test_get_variant_with_date(self, client: TestClient):
        """Test getting variant with specific date"""
        response = client.get("/api/datasets/viirs_snpp/variants/true_color?date_param=2025-10-04")
        assert response.status_code == 200
        data = response.json()
        
        variant = data["variant"]
        assert variant["selected_date"] == "2025-10-04"
        # Date should be resolved in URLs
        assert "2025-10-04" in variant["tile_url"]
        assert "2025-10-04" in variant["thumbnail_url"]
    
    def test_get_static_map_variant(self, client: TestClient):
        """Test getting variant for static (non-time-series) map"""
        response = client.get("/api/datasets/moon_opm_basemap/variants/default")
        assert response.status_code == 200
        data = response.json()
        
        variant = data["variant"]
        assert variant["selected_date"] is None  # Static datasets don't have dates


class TestViewsEndpoint:
    """Test user-saved map views"""
    
    def test_create_map_view(self, client: TestClient, sample_map_view_data):
        """Test POST /api/views"""
        response = client.post("/api/views", json=sample_map_view_data)
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert data["name"] == sample_map_view_data["name"]
        assert data["dataset_id"] == sample_map_view_data["dataset_id"]
        assert data["variant_id"] == sample_map_view_data["variant_id"]
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_list_map_views(self, client: TestClient, sample_map_view_data):
        """Test GET /api/views"""
        # Create a view first
        client.post("/api/views", json=sample_map_view_data)
        
        response = client.get("/api/views")
        assert response.status_code == 200
        data = response.json()
        
        assert "views" in data
        assert "count" in data
        assert data["count"] > 0
    
    def test_get_specific_view(self, client: TestClient, sample_map_view_data):
        """Test GET /api/views/{view_id}"""
        # Create a view
        create_response = client.post("/api/views", json=sample_map_view_data)
        view_id = create_response.json()["id"]
        
        # Get the view
        response = client.get(f"/api/views/{view_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == view_id
    
    def test_update_map_view(self, client: TestClient, sample_map_view_data):
        """Test PUT /api/views/{view_id}"""
        # Create a view
        create_response = client.post("/api/views", json=sample_map_view_data)
        view_id = create_response.json()["id"]
        
        # Update the view
        updated_data = sample_map_view_data.copy()
        updated_data["name"] = "Updated Name"
        updated_data["zoom_level"] = 10
        
        response = client.put(f"/api/views/{view_id}", json=updated_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["zoom_level"] == 10
    
    def test_delete_map_view(self, client: TestClient, sample_map_view_data):
        """Test DELETE /api/views/{view_id}"""
        # Create a view
        create_response = client.post("/api/views", json=sample_map_view_data)
        view_id = create_response.json()["id"]
        
        # Delete the view
        response = client.delete(f"/api/views/{view_id}")
        assert response.status_code == 200
        
        # Verify it's deleted
        get_response = client.get(f"/api/views/{view_id}")
        assert get_response.status_code == 404


class TestAnnotationsEndpoint:
    """Test annotations endpoint"""
    
    def test_create_annotation(self, client: TestClient, sample_annotation_data):
        """Test POST /api/annotations"""
        response = client.post("/api/annotations", json=sample_annotation_data)
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert data["map_view_id"] == sample_annotation_data["map_view_id"]
        assert data["type"] == sample_annotation_data["type"]
    
    def test_get_annotations(self, client: TestClient, sample_annotation_data):
        """Test GET /api/annotations"""
        # Create an annotation
        client.post("/api/annotations", json=sample_annotation_data)
        
        response = client.get("/api/annotations")
        assert response.status_code == 200
        data = response.json()
        assert "annotations" in data
    
    def test_filter_annotations_by_view(self, client: TestClient, sample_annotation_data):
        """Test filtering annotations by map view"""
        # Create an annotation
        client.post("/api/annotations", json=sample_annotation_data)
        
        response = client.get(f"/api/annotations?map_view_id={sample_annotation_data['map_view_id']}")
        assert response.status_code == 200
        data = response.json()
        
        for annotation in data["annotations"]:
            assert annotation["map_view_id"] == sample_annotation_data["map_view_id"]
    
    def test_update_annotation(self, client: TestClient, sample_annotation_data):
        """Test PUT /api/annotations/{annotation_id}"""
        # Create annotation
        create_response = client.post("/api/annotations", json=sample_annotation_data)
        annotation_id = create_response.json()["id"]
        
        # Update it
        updated_data = sample_annotation_data.copy()
        updated_data["text"] = "Updated text"
        
        response = client.put(f"/api/annotations/{annotation_id}", json=updated_data)
        assert response.status_code == 200
        data = response.json()
        assert data["text"] == "Updated text"
    
    def test_delete_annotation(self, client: TestClient, sample_annotation_data):
        """Test DELETE /api/annotations/{annotation_id}"""
        # Create annotation
        create_response = client.post("/api/annotations", json=sample_annotation_data)
        annotation_id = create_response.json()["id"]
        
        # Delete it
        response = client.delete(f"/api/annotations/{annotation_id}")
        assert response.status_code == 200
        
        # Verify deleted
        get_response = client.get(f"/api/annotations/{annotation_id}")
        assert get_response.status_code == 404


class TestCollectionsEndpoint:
    """Test collections endpoint"""
    
    def test_create_collection(self, client: TestClient, sample_collection_data):
        """Test POST /api/collections"""
        response = client.post("/api/collections", json=sample_collection_data)
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert data["name"] == sample_collection_data["name"]
        assert len(data["view_ids"]) == len(sample_collection_data["view_ids"])
    
    def test_get_collections(self, client: TestClient, sample_collection_data):
        """Test GET /api/collections"""
        # Create a collection
        client.post("/api/collections", json=sample_collection_data)
        
        response = client.get("/api/collections")
        assert response.status_code == 200
        data = response.json()
        assert "collections" in data
    
    def test_update_collection(self, client: TestClient, sample_collection_data):
        """Test PUT /api/collections/{collection_id}"""
        # Create collection
        create_response = client.post("/api/collections", json=sample_collection_data)
        collection_id = create_response.json()["id"]
        
        # Update it
        updated_data = sample_collection_data.copy()
        updated_data["name"] = "Updated Collection"
        updated_data["view_ids"].append("view_004")
        
        response = client.put(f"/api/collections/{collection_id}", json=updated_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Collection"
        assert len(data["view_ids"]) == 4
    
    def test_delete_collection(self, client: TestClient, sample_collection_data):
        """Test DELETE /api/collections/{collection_id}"""
        # Create collection
        create_response = client.post("/api/collections", json=sample_collection_data)
        collection_id = create_response.json()["id"]
        
        # Delete it
        response = client.delete(f"/api/collections/{collection_id}")
        assert response.status_code == 200
        
        # Verify deleted
        get_response = client.get(f"/api/collections/{collection_id}")
        assert get_response.status_code == 404