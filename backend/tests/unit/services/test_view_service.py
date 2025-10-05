"""
Unit tests for view service
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.services.view_service import ViewService
from app.models.schemas import View
from app.data.storage import views_db


class TestViewService:
    """Test view service business logic"""
    
    def setup_method(self):
        """Clear views before each test"""
        views_db.clear()
    
    def test_create_view(self):
        """Test creating a new view"""
        view = View(
            name="Test View",
            description="A test view",
            dataset_id="viirs_snpp",
            variant_id="true_color",
            center_lat=40.7128,
            center_lng=-74.0060,
            zoom_level=10
        )
        
        created_view = ViewService.create_view(view)
        
        assert created_view.id is not None
        assert created_view.name == "Test View"
        assert created_view.created_at is not None
        assert created_view.updated_at is not None
        assert created_view.id in views_db
    
    def test_get_all_views_empty(self):
        """Test getting all views when none exist"""
        result = ViewService.get_all_views()
        
        assert "views" in result
        assert "count" in result
        assert result["count"] == 0
        assert len(result["views"]) == 0
    
    def test_get_all_views_with_data(self):
        """Test getting all views when some exist"""
        # Create two views
        view1 = View(name="View 1", dataset_id="viirs_snpp", variant_id="true_color")
        view2 = View(name="View 2", dataset_id="mars_viking", variant_id="colorized")
        
        ViewService.create_view(view1)
        ViewService.create_view(view2)
        
        result = ViewService.get_all_views()
        
        assert result["count"] == 2
        assert len(result["views"]) == 2
    
    def test_get_existing_view(self):
        """Test getting a specific view"""
        view = View(name="Test View", dataset_id="viirs_snpp", variant_id="true_color")
        created_view = ViewService.create_view(view)
        
        retrieved_view = ViewService.get_view(created_view.id)
        
        assert retrieved_view is not None
        assert retrieved_view.id == created_view.id
        assert retrieved_view.name == "Test View"
    
    def test_get_nonexistent_view(self):
        """Test getting a view that doesn't exist"""
        view = ViewService.get_view("nonexistent_id")
        
        assert view is None
    
    def test_update_view(self):
        """Test updating a view"""
        view = View(name="Original Name", dataset_id="viirs_snpp", variant_id="true_color")
        created_view = ViewService.create_view(view)
        
        # Update the view
        updated_view = View(
            name="Updated Name",
            dataset_id="viirs_snpp",
            variant_id="false_color",
            zoom_level=15
        )
        
        result = ViewService.update_view(created_view.id, updated_view)
        
        assert result is not None
        assert result.id == created_view.id
        assert result.name == "Updated Name"
        assert result.variant_id == "false_color"
        assert result.zoom_level == 15
        assert result.updated_at > created_view.updated_at
    
    def test_update_nonexistent_view(self):
        """Test updating a view that doesn't exist"""
        view = View(name="Test", dataset_id="viirs_snpp", variant_id="true_color")
        result = ViewService.update_view("nonexistent_id", view)
        
        assert result is None
    
    def test_delete_view(self):
        """Test deleting a view"""
        view = View(name="Test View", dataset_id="viirs_snpp", variant_id="true_color")
        created_view = ViewService.create_view(view)
        
        # Delete the view
        success = ViewService.delete_view(created_view.id)
        
        assert success is True
        assert created_view.id not in views_db
        assert ViewService.get_view(created_view.id) is None
    
    def test_delete_nonexistent_view(self):
        """Test deleting a view that doesn't exist"""
        success = ViewService.delete_view("nonexistent_id")
        
        assert success is False
    
    def test_validate_view_with_valid_dataset(self):
        """Test validating a view with valid dataset"""
        view = View(
            name="Test View",
            dataset_id="viirs_snpp",
            variant_id="true_color"
        )
        
        is_valid, error_msg = ViewService.validate_view(view)
        
        assert is_valid is True
        assert error_msg is None
    
    def test_validate_view_with_invalid_dataset(self):
        """Test validating a view with invalid dataset"""
        view = View(
            name="Test View",
            dataset_id="nonexistent_dataset",
            variant_id="true_color"
        )
        
        is_valid, error_msg = ViewService.validate_view(view)
        
        assert is_valid is False
        assert error_msg is not None
        assert "not found" in error_msg.lower()
    
    def test_validate_view_with_invalid_variant(self):
        """Test validating a view with invalid variant"""
        view = View(
            name="Test View",
            dataset_id="viirs_snpp",
            variant_id="nonexistent_variant"
        )
        
        is_valid, error_msg = ViewService.validate_view(view)
        
        assert is_valid is False
        assert error_msg is not None
        assert "variant" in error_msg.lower()
