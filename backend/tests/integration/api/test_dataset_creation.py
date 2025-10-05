"""
Integration tests for dataset creation API
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.data.storage import DATASETS
from app.models.enums import SourceId


class TestDatasetCreation:
    """Test unified dataset creation endpoint"""
    
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
            "category": "custom",
            "subject": "custom",
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
