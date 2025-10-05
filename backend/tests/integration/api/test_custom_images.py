"""
Integration tests for custom images API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.data.storage import DATASETS
from app.models.enums import SourceId


class TestCustomImagesEndpoint:
    """Test custom image upload endpoints"""
    
    def setup_method(self):
        """Clear custom datasets before each test"""
        custom_ids = [
            dataset_id for dataset_id, dataset in DATASETS.items()
            if dataset.source_id == SourceId.CUSTOM
        ]
        for dataset_id in custom_ids:
            del DATASETS[dataset_id]
    
    @patch('app.services.custom_image_service.tile_processor')
    def test_upload_custom_image_success(self, mock_processor, client: TestClient):
        """Test POST /api/custom-images with successful upload"""
        # Mock tile processor
        mock_processor.is_tiled.return_value = True
        mock_processor.get_tile_info.return_value = {
            "tile_id": "test123",
            "max_zoom": 8,
            "status": "completed"
        }
        mock_processor.get_tile_url_template.return_value = "http://localhost:8000/tiles/test123/{z}/{x}/{y}.png"
        
        # Upload image
        upload_data = {
            "image_url": "https://example.com/test-image.jpg",
            "name": "Test Image",
            "description": "A test image"
        }
        
        response = client.post("/api/custom-images", json=upload_data)
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "dataset_id" in data
        assert data["dataset_id"].startswith("custom_")
        assert data["status"] == "ready"
        assert "dataset" in data
        assert data["dataset"]["name"] == "Test Image"
        assert data["dataset"]["source_id"] == "custom"
    
    @patch('app.services.custom_image_service.tile_processor')
    def test_upload_custom_image_with_category(self, mock_processor, client: TestClient):
        """Test uploading image with custom category"""
        # Mock tile processor
        mock_processor.is_tiled.return_value = True
        mock_processor.get_tile_info.return_value = {
            "tile_id": "test456",
            "max_zoom": 8,
            "status": "completed"
        }
        mock_processor.get_tile_url_template.return_value = "http://localhost:8000/tiles/test456/{z}/{x}/{y}.png"
        
        # Upload image with category
        upload_data = {
            "image_url": "https://example.com/galaxy.jpg",
            "name": "My Galaxy",
            "category": "galaxies",
            "subject": "andromeda"
        }
        
        response = client.post("/api/custom-images", json=upload_data)
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        assert data["dataset"]["category"] == "galaxies"
        assert data["dataset"]["subject"] == "andromeda"
    
    def test_upload_custom_image_invalid_url(self, client: TestClient):
        """Test uploading with invalid URL"""
        upload_data = {
            "image_url": "not-a-valid-url",
            "name": "Test Image"
        }
        
        response = client.post("/api/custom-images", json=upload_data)
        
        # Should fail validation
        assert response.status_code == 422
    
    def test_upload_custom_image_missing_name(self, client: TestClient):
        """Test uploading without required name field"""
        upload_data = {
            "image_url": "https://example.com/test.jpg"
        }
        
        response = client.post("/api/custom-images", json=upload_data)
        
        # Should fail validation
        assert response.status_code == 422
    
    @patch('app.services.custom_image_service.tile_processor')
    def test_upload_custom_image_processing(self, mock_processor, client: TestClient):
        """Test uploading image that needs processing"""
        # Mock tile processor for processing state
        mock_processor.is_tiled.return_value = False
        mock_processor._generate_tile_id.return_value = "test_processing"
        mock_processor.process_image.side_effect = Exception("Processing")
        mock_processor.get_tile_url_template.side_effect = ValueError("Not ready")
        
        upload_data = {
            "image_url": "https://example.com/large-image.jpg",
            "name": "Large Image"
        }
        
        response = client.post("/api/custom-images", json=upload_data)
        
        # Should still succeed but with processing status
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["status"] == "processing"
        assert "processing" in data["message"].lower()
    
    @patch('app.services.custom_image_service.tile_processor')
    def test_list_custom_images_empty(self, mock_processor, client: TestClient):
        """Test GET /api/custom-images when no images exist"""
        response = client.get("/api/custom-images")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "datasets" in data
        assert "count" in data
        assert data["count"] == 0
    
    @patch('app.services.custom_image_service.tile_processor')
    def test_list_custom_images_with_data(self, mock_processor, client: TestClient):
        """Test GET /api/custom-images with uploaded images"""
        # Mock tile processor
        mock_processor.is_tiled.return_value = True
        mock_processor.get_tile_info.return_value = {
            "tile_id": "test1",
            "max_zoom": 8,
            "status": "completed"
        }
        mock_processor.get_tile_url_template.return_value = "http://localhost:8000/tiles/test1/{z}/{x}/{y}.png"
        
        # Upload an image
        client.post("/api/custom-images", json={
            "image_url": "https://example.com/img1.jpg",
            "name": "Image 1"
        })
        
        # List images
        response = client.get("/api/custom-images")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["count"] == 1
        assert len(data["datasets"]) == 1
        assert data["datasets"][0]["name"] == "Image 1"
    
    @patch('app.services.custom_image_service.tile_processor')
    def test_delete_custom_image_success(self, mock_processor, client: TestClient):
        """Test DELETE /api/custom-images/{dataset_id}"""
        # Mock tile processor
        mock_processor.is_tiled.return_value = True
        mock_processor.get_tile_info.return_value = {
            "tile_id": "test_delete",
            "max_zoom": 8,
            "status": "completed"
        }
        mock_processor.get_tile_url_template.return_value = "http://localhost:8000/tiles/test_delete/{z}/{x}/{y}.png"
        
        # Upload an image
        upload_response = client.post("/api/custom-images", json={
            "image_url": "https://example.com/delete-me.jpg",
            "name": "Delete Me"
        })
        dataset_id = upload_response.json()["dataset_id"]
        
        # Delete the image
        response = client.delete(f"/api/custom-images/{dataset_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "deleted" in data["message"].lower()
        
        # Verify it's gone
        list_response = client.get("/api/custom-images")
        assert list_response.json()["count"] == 0
    
    def test_delete_custom_image_not_found(self, client: TestClient):
        """Test deleting non-existent custom image"""
        response = client.delete("/api/custom-images/nonexistent_id")
        
        assert response.status_code == 404
    
    def test_delete_builtin_dataset_fails(self, client: TestClient):
        """Test that deleting built-in datasets is not allowed"""
        response = client.delete("/api/custom-images/viirs_snpp")
        
        assert response.status_code == 404
    
    @patch('app.services.custom_image_service.tile_processor')
    def test_get_tile_status_ready(self, mock_processor, client: TestClient):
        """Test GET /api/tile-status/{tile_id} when ready"""
        # Mock tile processor
        mock_processor.tile_index = {
            "test123": {
                "tile_id": "test123",
                "status": "completed",
                "max_zoom": 8
            }
        }
        mock_processor.processing_status = {}
        
        response = client.get("/api/tile-status/test123")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "ready"
        assert "tile_info" in data
    
    @patch('app.services.custom_image_service.tile_processor')
    def test_get_tile_status_processing(self, mock_processor, client: TestClient):
        """Test GET /api/tile-status/{tile_id} when processing"""
        # Mock tile processor
        mock_processor.tile_index = {}
        mock_processor.processing_status = {
            "test456": {
                "status": "processing",
                "progress": "generating_tiles",
                "started_at": "2025-10-05T12:00:00"
            }
        }
        
        response = client.get("/api/tile-status/test456")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "processing"
        assert data["progress"] == "generating_tiles"
    
    @patch('app.services.custom_image_service.tile_processor')
    def test_get_tile_status_not_found(self, mock_processor, client: TestClient):
        """Test GET /api/tile-status/{tile_id} for non-existent tile"""
        # Mock tile processor
        mock_processor.tile_index = {}
        mock_processor.processing_status = {}
        
        response = client.get("/api/tile-status/nonexistent")
        
        assert response.status_code == 404
    
    @patch('app.services.custom_image_service.tile_processor')
    def test_uploaded_image_accessible_via_catalog(self, mock_processor, client: TestClient):
        """Test that uploaded images are accessible via catalog endpoints"""
        # Mock tile processor
        mock_processor.is_tiled.return_value = True
        mock_processor.get_tile_info.return_value = {
            "tile_id": "test_catalog",
            "max_zoom": 8,
            "status": "completed"
        }
        mock_processor.get_tile_url_template.return_value = "http://localhost:8000/tiles/test_catalog/{z}/{x}/{y}.png"
        
        # Upload an image
        upload_response = client.post("/api/custom-images", json={
            "image_url": "https://example.com/catalog-test.jpg",
            "name": "Catalog Test"
        })
        dataset_id = upload_response.json()["dataset_id"]
        
        # Access via catalog endpoint
        catalog_response = client.get(f"/api/datasets/{dataset_id}")
        
        assert catalog_response.status_code == 200
        data = catalog_response.json()
        
        assert data["id"] == dataset_id
        assert data["name"] == "Catalog Test"
        assert data["source_id"] == "custom"
    
    @patch('app.services.custom_image_service.tile_processor')
    def test_uploaded_image_variants_accessible(self, mock_processor, client: TestClient):
        """Test that uploaded image variants are accessible"""
        # Mock tile processor
        mock_processor.is_tiled.return_value = True
        mock_processor.get_tile_info.return_value = {
            "tile_id": "test_variants",
            "max_zoom": 8,
            "status": "completed"
        }
        mock_processor.get_tile_url_template.return_value = "http://localhost:8000/tiles/test_variants/{z}/{x}/{y}.png"
        
        # Upload an image
        upload_response = client.post("/api/custom-images", json={
            "image_url": "https://example.com/variants-test.jpg",
            "name": "Variants Test"
        })
        dataset_id = upload_response.json()["dataset_id"]
        
        # Get variants
        variants_response = client.get(f"/api/datasets/{dataset_id}/variants")
        
        assert variants_response.status_code == 200
        data = variants_response.json()
        
        assert "variants" in data
        assert len(data["variants"]) == 1
        assert data["variants"][0]["id"] == "default"
        
        # Get specific variant
        variant_response = client.get(f"/api/datasets/{dataset_id}/variants/default")
        
        assert variant_response.status_code == 200
        variant_data = variant_response.json()
        
        assert "variant" in variant_data
        assert "{z}" in variant_data["variant"]["tile_url"]
