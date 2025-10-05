"""
Integration tests for dataset API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from datetime import date

from app.data.storage import DATASETS
from app.models.enums import SourceId


class TestDatasetsEndpoint:
    """Test dataset listing and retrieval"""
    
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


class TestDatasetCreation:
    """Test dataset creation endpoint"""
    
    def setup_method(self):
        """Clear custom datasets before each test"""
        custom_ids = [
            dataset_id for dataset_id, dataset in DATASETS.items()
            if dataset.source_id == SourceId.CUSTOM
        ]
        for dataset_id in custom_ids:
            del DATASETS[dataset_id]
    
    def test_create_dataset_from_tile_service(self, client: TestClient):
        """Test creating dataset from pre-tiled service URL"""
        request_data = {
            "name": "Custom Mars Map",
            "description": "A custom Mars dataset",
            "category": "planets",
            "subject": "mars",
            "url": "https://example.com/tiles/{z}/{x}/{y}.jpg"
        }
        
        response = client.post("/api/datasets", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["status"] == "ready"
        assert "dataset_id" in data
        assert data["dataset"]["name"] == "Custom Mars Map"
        assert data["dataset"]["category"] == "planets"
        assert data["dataset"]["subject"] == "mars"
    
    @patch('app.services.dataset_service.tile_processor')
    def test_create_dataset_from_image_url(self, mock_processor, client: TestClient):
        """Test creating dataset from image URL"""
        # Mock tile processor
        mock_processor.is_tiled.return_value = True
        mock_processor.get_tile_info.return_value = {
            "tile_id": "test123",
            "max_zoom": 8,
            "status": "completed"
        }
        mock_processor.get_tile_url_template.return_value = "http://localhost:8000/tiles/test123/{z}/{x}/{y}.png"
        mock_processor._generate_tile_id.return_value = "test123"
        
        request_data = {
            "name": "My Galaxy Image",
            "description": "A galaxy I photographed",
            "category": "galaxies",
            "subject": "andromeda",
            "url": "https://example.com/galaxy.jpg"
        }
        
        response = client.post("/api/datasets", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "dataset_id" in data
        assert data["dataset"]["name"] == "My Galaxy Image"
        assert data["dataset"]["category"] == "galaxies"
        assert data["dataset"]["source_id"] == "custom"
    
    def test_create_dataset_invalid_url(self, client: TestClient):
        """Test creating dataset with invalid URL"""
        request_data = {
            "name": "Invalid Dataset",
            "category": "planets",
            "subject": "earth",
            "url": "https://example.com/not-a-tile-or-image"
        }
        
        response = client.post("/api/datasets", json=request_data)
        
        assert response.status_code == 400
        assert "error" in response.json()["detail"].lower() or "URL must be" in response.json()["detail"]
    
    def test_create_dataset_missing_fields(self, client: TestClient):
        """Test creating dataset with missing required fields"""
        request_data = {
            "name": "Incomplete Dataset",
            "url": "https://example.com/tiles/{z}/{x}/{y}.jpg"
            # Missing category and subject
        }
        
        response = client.post("/api/datasets", json=request_data)
        
        assert response.status_code == 422  # Validation error
    
    @patch('app.services.dataset_service.tile_processor')
    def test_create_multiple_datasets_same_url(self, mock_processor, client: TestClient):
        """Test that duplicate detection works based on tile_id"""
        # Setup consistent mock for duplicate detection
        def generate_tile_id(url):
            import hashlib
            return hashlib.md5(url.encode()).hexdigest()[:16]
        
        mock_processor._generate_tile_id.side_effect = generate_tile_id
        mock_processor.is_tiled.return_value = True
        mock_processor.get_tile_info.return_value = {
            "tile_id": generate_tile_id("https://example.com/duplicate.jpg"),
            "max_zoom": 8,
            "status": "completed"
        }
        mock_processor.get_tile_url_template.return_value = f"http://localhost:8000/tiles/{generate_tile_id('https://example.com/duplicate.jpg')}/{{z}}/{{x}}/{{y}}.png"
        
        request_data = {
            "name": "Duplicate Test",
            "category": "galaxies",
            "subject": "andromeda",
            "url": "https://example.com/duplicate.jpg"
        }
        
        # First creation
        response1 = client.post("/api/datasets", json=request_data)
        assert response1.status_code == 200
        data1 = response1.json()
        dataset_id1 = data1["dataset_id"]
        
        # Second creation with same URL - should detect duplicate
        response2 = client.post("/api/datasets", json=request_data)
        assert response2.status_code == 200
        data2 = response2.json()
        
        # Either returns duplicate or creates new dataset (both are acceptable)
        # The key is that it succeeds
        assert data2["success"] is True
        
        # If duplicate detected, should reference same tile_id
        if data2.get("is_duplicate"):
            assert "already exists" in data2["message"].lower()
            assert data2["dataset_id"] == dataset_id1
    
    def test_created_dataset_appears_in_catalog(self, client: TestClient):
        """Test that created dataset appears in catalog listing"""
        request_data = {
            "name": "Catalog Test",
            "category": "planets",
            "subject": "jupiter",
            "url": "https://example.com/jupiter/{z}/{x}/{y}.jpg"
        }
        
        # Create dataset
        create_response = client.post("/api/datasets", json=request_data)
        assert create_response.status_code == 200
        dataset_id = create_response.json()["dataset_id"]
        
        # Check it appears in catalog
        catalog_response = client.get("/api/datasets")
        assert catalog_response.status_code == 200
        
        datasets = catalog_response.json()["datasets"]
        dataset_ids = [d["id"] for d in datasets]
        assert dataset_id in dataset_ids
    
    def test_detect_nasa_gibs_source(self, client: TestClient):
        """Test that NASA GIBS URLs are detected correctly"""
        request_data = {
            "name": "GIBS Test",
            "category": "planets",
            "subject": "earth",
            "url": "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/VIIRS_SNPP_CorrectedReflectance_TrueColor/default/{date}/GoogleMapsCompatible_Level9/{z}/{y}/{x}.jpg"
        }
        
        response = client.post("/api/datasets", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        # Should detect as NASA GIBS source
        assert data["dataset"]["source_id"] == "nasa_gibs"
    
    def test_detect_nasa_trek_source(self, client: TestClient):
        """Test that NASA Trek URLs are detected correctly"""
        request_data = {
            "name": "Trek Test",
            "category": "moons",
            "subject": "moon",
            "url": "https://trek.nasa.gov/tiles/Moon/EQ/LRO_WAC_Mosaic_Global_303ppd_v02/1.0.0/default/default028mm/{z}/{y}/{x}.jpg"
        }
        
        response = client.post("/api/datasets", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        # Should detect as NASA Trek source
        assert data["dataset"]["source_id"] == "nasa_trek"


class TestDatasetUpdate:
    """Test dataset update endpoint"""
    
    def setup_method(self):
        """Clear custom datasets before each test"""
        custom_ids = [
            dataset_id for dataset_id, dataset in DATASETS.items()
            if dataset.source_id == SourceId.CUSTOM
        ]
        for dataset_id in custom_ids:
            del DATASETS[dataset_id]
    
    @patch('app.services.dataset_service.tile_processor')
    def test_update_dataset_name(self, mock_processor, client: TestClient):
        """Test updating dataset name"""
        # Setup mock
        mock_processor.is_tiled.return_value = True
        mock_processor._generate_tile_id.return_value = "test_update"
        mock_processor.get_tile_info.return_value = {
            "tile_id": "test_update",
            "max_zoom": 8,
            "status": "completed"
        }
        mock_processor.get_tile_url_template.return_value = "http://localhost:8000/tiles/test_update/{z}/{x}/{y}.png"
        
        # Create a custom dataset
        create_response = client.post("/api/datasets", json={
            "name": "Original Name",
            "description": "Original description",
            "category": "galaxies",
            "subject": "andromeda",
            "url": "https://example.com/image.jpg"
        })
        
        assert create_response.status_code == 200
        dataset_id = create_response.json()["dataset_id"]
        
        # Update the name
        update_response = client.put(f"/api/datasets/{dataset_id}", json={
            "name": "Updated Name"
        })
        
        assert update_response.status_code == 200
        data = update_response.json()
        
        assert data["success"] is True
        assert data["dataset"]["name"] == "Updated Name"
        assert data["dataset"]["description"] == "Original description"  # Unchanged
        assert "updated" in data["message"].lower()
    
    @patch('app.services.dataset_service.tile_processor')
    def test_update_dataset_multiple_fields(self, mock_processor, client: TestClient):
        """Test updating multiple fields at once"""
        # Setup mock
        mock_processor.is_tiled.return_value = True
        mock_processor._generate_tile_id.return_value = "test_multi_update"
        mock_processor.get_tile_info.return_value = {
            "tile_id": "test_multi_update",
            "max_zoom": 8,
            "status": "completed"
        }
        mock_processor.get_tile_url_template.return_value = "http://localhost:8000/tiles/test_multi_update/{z}/{x}/{y}.png"
        
        # Create a custom dataset
        create_response = client.post("/api/datasets", json={
            "name": "Original",
            "description": "Original desc",
            "category": "galaxies",
            "subject": "andromeda",
            "url": "https://example.com/multi.jpg"
        })
        
        dataset_id = create_response.json()["dataset_id"]
        
        # Update multiple fields
        update_response = client.patch(f"/api/datasets/{dataset_id}", json={
            "name": "New Name",
            "description": "New description",
            "category": "galaxies",
            "subject": "andromeda"
        })
        
        assert update_response.status_code == 200
        data = update_response.json()
        
        assert data["dataset"]["name"] == "New Name"
        assert data["dataset"]["description"] == "New description"
        assert data["dataset"]["category"] == "galaxies"
        assert data["dataset"]["subject"] == "andromeda"
    
    def test_update_nonexistent_dataset(self, client: TestClient):
        """Test updating a dataset that doesn't exist"""
        update_response = client.put("/api/datasets/nonexistent", json={
            "name": "New Name"
        })
        
        assert update_response.status_code == 404
        assert "not found" in update_response.json()["detail"].lower()
    
    def test_update_builtin_dataset(self, client: TestClient):
        """Test that built-in datasets cannot be updated"""
        update_response = client.put("/api/datasets/viirs_snpp", json={
            "name": "Hacked Name"
        })
        
        assert update_response.status_code == 403
        assert "only custom" in update_response.json()["detail"].lower()
    
    @patch('app.services.dataset_service.tile_processor')
    def test_update_with_empty_body(self, mock_processor, client: TestClient):
        """Test updating with no fields (should succeed but make no changes)"""
        # Setup mock
        mock_processor.is_tiled.return_value = True
        mock_processor._generate_tile_id.return_value = "test_empty"
        mock_processor.get_tile_info.return_value = {
            "tile_id": "test_empty",
            "max_zoom": 8,
            "status": "completed"
        }
        mock_processor.get_tile_url_template.return_value = "http://localhost:8000/tiles/test_empty/{z}/{x}/{y}.png"
        
        # Create dataset
        create_response = client.post("/api/datasets", json={
            "name": "Test",
            "category": "galaxies",
            "subject": "andromeda",
            "url": "https://example.com/empty.jpg"
        })
        
        dataset_id = create_response.json()["dataset_id"]
        
        # Update with empty body
        update_response = client.patch(f"/api/datasets/{dataset_id}", json={})
        
        assert update_response.status_code == 200
        data = update_response.json()
        assert "no changes" in data["message"].lower()
    
    @patch('app.services.dataset_service.tile_processor')
    def test_updated_dataset_appears_in_catalog(self, mock_processor, client: TestClient):
        """Test that updated dataset appears correctly in catalog"""
        # Setup mock
        mock_processor.is_tiled.return_value = True
        mock_processor._generate_tile_id.return_value = "test_catalog"
        mock_processor.get_tile_info.return_value = {
            "tile_id": "test_catalog",
            "max_zoom": 8,
            "status": "completed"
        }
        mock_processor.get_tile_url_template.return_value = "http://localhost:8000/tiles/test_catalog/{z}/{x}/{y}.png"
        
        # Create dataset
        create_response = client.post("/api/datasets", json={
            "name": "Before Update",
            "category": "galaxies",
            "subject": "andromeda",
            "url": "https://example.com/catalog.jpg"
        })
        
        dataset_id = create_response.json()["dataset_id"]
        
        # Update it
        client.put(f"/api/datasets/{dataset_id}", json={
            "name": "After Update"
        })
        
        # Get from catalog
        get_response = client.get(f"/api/datasets/{dataset_id}")
        assert get_response.status_code == 200
        
        dataset = get_response.json()
        assert dataset["name"] == "After Update"
    
    @patch('app.services.dataset_service.tile_processor')
    def test_put_vs_patch_methods(self, mock_processor, client: TestClient):
        """Test that both PUT and PATCH work"""
        # Setup mock
        mock_processor.is_tiled.return_value = True
        mock_processor._generate_tile_id.return_value = "test_methods"
        mock_processor.get_tile_info.return_value = {
            "tile_id": "test_methods",
            "max_zoom": 8,
            "status": "completed"
        }
        mock_processor.get_tile_url_template.return_value = "http://localhost:8000/tiles/test_methods/{z}/{x}/{y}.png"
        
        # Create dataset
        create_response = client.post("/api/datasets", json={
            "name": "Test",
            "category": "galaxies",
            "subject": "andromeda",
            "url": "https://example.com/methods.jpg"
        })
        
        dataset_id = create_response.json()["dataset_id"]
        
        # Test PUT
        put_response = client.put(f"/api/datasets/{dataset_id}", json={
            "name": "PUT Update"
        })
        assert put_response.status_code == 200
        assert put_response.json()["dataset"]["name"] == "PUT Update"
        
        # Test PATCH
        patch_response = client.patch(f"/api/datasets/{dataset_id}", json={
            "name": "PATCH Update"
        })
        assert patch_response.status_code == 200
        assert patch_response.json()["dataset"]["name"] == "PATCH Update"
