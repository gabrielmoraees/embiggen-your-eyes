"""
Unit tests for custom image service
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.services.custom_image_service import CustomImageService
from app.models.enums import Category, Subject, SourceId
from app.data.storage import DATASETS


class TestCustomImageService:
    """Test custom image service business logic"""
    
    def setup_method(self):
        """Clear custom datasets before each test"""
        # Remove any custom datasets
        custom_ids = [
            dataset_id for dataset_id, dataset in DATASETS.items()
            if dataset.source_id == SourceId.CUSTOM
        ]
        for dataset_id in custom_ids:
            del DATASETS[dataset_id]
    
    @patch('app.services.custom_image_service.tile_processor')
    def test_create_custom_dataset_from_url_already_tiled(self, mock_processor):
        """Test creating dataset when image is already tiled"""
        # Mock tile processor
        mock_processor.is_tiled.return_value = True
        mock_processor.get_tile_info.return_value = {
            "tile_id": "test123",
            "source_url": "https://example.com/image.jpg",
            "max_zoom": 8,
            "status": "completed"
        }
        mock_processor.get_tile_url_template.return_value = "http://localhost:8000/tiles/test123/{z}/{x}/{y}.png"
        
        # Create dataset
        result = CustomImageService.create_custom_dataset_from_url(
            image_url="https://example.com/image.jpg",
            name="Test Image",
            description="Test description"
        )
        
        # Verify result
        assert result["status"] == "ready"
        assert "dataset" in result
        assert result["dataset"].name == "Test Image"
        assert result["dataset"].source_id == SourceId.CUSTOM
        assert result["dataset"].category == Category.CUSTOM
        assert result["dataset"].subject == Subject.CUSTOM
        assert len(result["dataset"].variants) == 1
        assert result["dataset"].variants[0].id == "default"
        
        # Verify dataset was added to catalog
        assert result["dataset"].id in DATASETS
    
    @patch('app.services.custom_image_service.tile_processor')
    def test_create_custom_dataset_from_url_needs_processing(self, mock_processor):
        """Test creating dataset when image needs tile processing"""
        # Mock tile processor
        mock_processor.is_tiled.return_value = False
        mock_processor._generate_tile_id.return_value = "test456"
        mock_processor.process_image.return_value = {
            "tile_id": "test456",
            "source_url": "https://example.com/new-image.jpg",
            "max_zoom": 8,
            "status": "completed"
        }
        mock_processor.get_tile_url_template.return_value = "http://localhost:8000/tiles/test456/{z}/{x}/{y}.png"
        
        # Create dataset
        result = CustomImageService.create_custom_dataset_from_url(
            image_url="https://example.com/new-image.jpg",
            name="New Image"
        )
        
        # Verify processing was called
        mock_processor.process_image.assert_called_once()
        
        # Verify result
        assert result["status"] == "ready"
        assert result["dataset"].name == "New Image"
        assert "message" in result
    
    @patch('app.services.custom_image_service.tile_processor')
    def test_create_custom_dataset_with_custom_category(self, mock_processor):
        """Test creating dataset with custom category and subject"""
        # Mock tile processor
        mock_processor.is_tiled.return_value = True
        mock_processor.get_tile_info.return_value = {
            "tile_id": "test789",
            "max_zoom": 8,
            "status": "completed"
        }
        mock_processor.get_tile_url_template.return_value = "http://localhost:8000/tiles/test789/{z}/{x}/{y}.png"
        
        # Create dataset with custom category
        result = CustomImageService.create_custom_dataset_from_url(
            image_url="https://example.com/galaxy.jpg",
            name="My Galaxy",
            category=Category.GALAXIES,
            subject=Subject.ANDROMEDA
        )
        
        # Verify custom category and subject
        assert result["dataset"].category == Category.GALAXIES
        assert result["dataset"].subject == Subject.ANDROMEDA
    
    @patch('app.services.custom_image_service.tile_processor')
    def test_create_custom_dataset_processing_in_progress(self, mock_processor):
        """Test creating dataset when processing fails/is in progress"""
        # Mock tile processor
        mock_processor.is_tiled.return_value = False
        mock_processor._generate_tile_id.return_value = "test_processing"
        mock_processor.process_image.side_effect = Exception("Processing in progress")
        mock_processor.get_tile_url_template.side_effect = ValueError("Tiles not ready")
        
        # Create dataset
        result = CustomImageService.create_custom_dataset_from_url(
            image_url="https://example.com/processing.jpg",
            name="Processing Image"
        )
        
        # Verify status is processing
        assert result["status"] == "processing"
        assert "tile_info" in result
        assert result["tile_info"]["status"] == "processing"
    
    @patch('app.services.custom_image_service.tile_processor')
    def test_get_tile_status_ready(self, mock_processor):
        """Test getting tile status when tiles are ready"""
        # Mock tile processor
        mock_processor.tile_index = {
            "test123": {
                "tile_id": "test123",
                "status": "completed",
                "max_zoom": 8
            }
        }
        
        # Get status
        result = CustomImageService.get_tile_status("test123")
        
        # Verify result
        assert result["status"] == "ready"
        assert "tile_info" in result
        assert result["tile_info"]["tile_id"] == "test123"
    
    @patch('app.services.custom_image_service.tile_processor')
    def test_get_tile_status_processing(self, mock_processor):
        """Test getting tile status when processing"""
        # Mock tile processor
        mock_processor.tile_index = {}
        mock_processor.processing_status = {
            "test456": {
                "status": "processing",
                "progress": "generating_tiles",
                "started_at": "2025-10-05T12:00:00"
            }
        }
        
        # Get status
        result = CustomImageService.get_tile_status("test456")
        
        # Verify result
        assert result["status"] == "processing"
        assert result["progress"] == "generating_tiles"
        assert "started_at" in result
    
    @patch('app.services.custom_image_service.tile_processor')
    def test_get_tile_status_not_found(self, mock_processor):
        """Test getting tile status for non-existent tile"""
        # Mock tile processor
        mock_processor.tile_index = {}
        mock_processor.processing_status = {}
        
        # Get status
        result = CustomImageService.get_tile_status("nonexistent")
        
        # Verify result
        assert result["status"] == "not_found"
        assert "message" in result
    
    @patch('app.services.custom_image_service.tile_processor')
    def test_list_custom_datasets_empty(self, mock_processor):
        """Test listing custom datasets when none exist"""
        # List datasets
        result = CustomImageService.list_custom_datasets()
        
        # Verify result
        assert "datasets" in result
        assert "count" in result
        assert result["count"] == 0
        assert len(result["datasets"]) == 0
    
    @patch('app.services.custom_image_service.tile_processor')
    def test_list_custom_datasets_with_data(self, mock_processor):
        """Test listing custom datasets when some exist"""
        # Mock tile processor
        mock_processor.is_tiled.return_value = True
        mock_processor.get_tile_info.return_value = {
            "tile_id": "test1",
            "max_zoom": 8,
            "status": "completed"
        }
        mock_processor.get_tile_url_template.return_value = "http://localhost:8000/tiles/test1/{z}/{x}/{y}.png"
        
        # Create two custom datasets
        CustomImageService.create_custom_dataset_from_url(
            image_url="https://example.com/img1.jpg",
            name="Image 1"
        )
        
        mock_processor.get_tile_info.return_value = {
            "tile_id": "test2",
            "max_zoom": 8,
            "status": "completed"
        }
        mock_processor.get_tile_url_template.return_value = "http://localhost:8000/tiles/test2/{z}/{x}/{y}.png"
        
        CustomImageService.create_custom_dataset_from_url(
            image_url="https://example.com/img2.jpg",
            name="Image 2"
        )
        
        # List datasets
        result = CustomImageService.list_custom_datasets()
        
        # Verify result
        assert result["count"] == 2
        assert len(result["datasets"]) == 2
        
        # All should be custom source
        for dataset in result["datasets"]:
            assert dataset.source_id == SourceId.CUSTOM
    
    @patch('app.services.custom_image_service.tile_processor')
    def test_delete_custom_dataset_success(self, mock_processor):
        """Test deleting a custom dataset"""
        # Mock tile processor
        mock_processor.is_tiled.return_value = True
        mock_processor.get_tile_info.return_value = {
            "tile_id": "test_delete",
            "max_zoom": 8,
            "status": "completed"
        }
        mock_processor.get_tile_url_template.return_value = "http://localhost:8000/tiles/test_delete/{z}/{x}/{y}.png"
        
        # Create dataset
        result = CustomImageService.create_custom_dataset_from_url(
            image_url="https://example.com/delete-me.jpg",
            name="Delete Me"
        )
        dataset_id = result["dataset"].id
        
        # Verify it exists
        assert dataset_id in DATASETS
        
        # Delete dataset
        success = CustomImageService.delete_custom_dataset(dataset_id)
        
        # Verify deletion
        assert success is True
        assert dataset_id not in DATASETS
    
    def test_delete_custom_dataset_not_found(self):
        """Test deleting a dataset that doesn't exist"""
        success = CustomImageService.delete_custom_dataset("nonexistent")
        
        assert success is False
    
    @patch('app.services.custom_image_service.tile_processor')
    def test_delete_non_custom_dataset_fails(self, mock_processor):
        """Test that deleting non-custom datasets is not allowed"""
        # Try to delete a built-in dataset (should fail)
        success = CustomImageService.delete_custom_dataset("viirs_snpp")
        
        assert success is False
    
    @patch('app.services.custom_image_service.tile_processor')
    def test_dataset_has_correct_structure(self, mock_processor):
        """Test that created dataset has correct structure"""
        # Mock tile processor
        mock_processor.is_tiled.return_value = True
        mock_processor.get_tile_info.return_value = {
            "tile_id": "test_structure",
            "max_zoom": 8,
            "status": "completed"
        }
        mock_processor.get_tile_url_template.return_value = "http://localhost:8000/tiles/test_structure/{z}/{x}/{y}.png"
        
        # Create dataset
        result = CustomImageService.create_custom_dataset_from_url(
            image_url="https://example.com/test.jpg",
            name="Test Structure",
            description="Test description"
        )
        
        dataset = result["dataset"]
        
        # Verify structure
        assert dataset.id.startswith("custom_")
        assert dataset.name == "Test Structure"
        assert dataset.description == "Test description"
        assert dataset.source_id == SourceId.CUSTOM
        assert dataset.supports_time_series is False
        assert dataset.projection.value == "epsg3857"
        
        # Verify variant
        assert len(dataset.variants) == 1
        variant = dataset.variants[0]
        assert variant.id == "default"
        assert variant.name == "Original"
        assert variant.is_default is True
        assert "{z}" in variant.tile_url_template
        assert "{x}" in variant.tile_url_template
        assert "{y}" in variant.tile_url_template
