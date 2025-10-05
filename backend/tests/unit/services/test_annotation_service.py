"""
Unit tests for annotation service
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.services.annotation_service import AnnotationService
from app.models.schemas import Annotation
from app.models.enums import AnnotationType
from app.data.storage import annotations_db


class TestAnnotationService:
    """Test annotation service business logic"""
    
    def setup_method(self):
        """Clear annotations before each test"""
        annotations_db.clear()
    
    def test_create_annotation(self):
        """Test creating a new annotation"""
        annotation = Annotation(
            type=AnnotationType.POINT,
            coordinates=[{"lat": 40.7128, "lng": -74.0060}],
            text="New York City",
            color="#FF0000"
        )
        
        created = AnnotationService.create_annotation(annotation)
        
        assert created.id is not None
        assert created.text == "New York City"
        assert created.created_at is not None
        assert created.updated_at is not None
        assert created.id in annotations_db
    
    def test_get_all_annotations_empty(self):
        """Test getting all annotations when none exist"""
        result = AnnotationService.get_annotations()
        
        assert "annotations" in result
        assert len(result["annotations"]) == 0
    
    def test_get_all_annotations_with_data(self):
        """Test getting all annotations when some exist"""
        ann1 = Annotation(type=AnnotationType.POINT, coordinates=[{"lat": 0, "lng": 0}])
        ann2 = Annotation(type=AnnotationType.POLYGON, coordinates=[{"lat": 1, "lng": 1}])
        
        AnnotationService.create_annotation(ann1)
        AnnotationService.create_annotation(ann2)
        
        result = AnnotationService.get_annotations()
        
        assert len(result["annotations"]) == 2
    
    def test_filter_annotations_by_view(self):
        """Test filtering annotations by map view"""
        ann1 = Annotation(
            type=AnnotationType.POINT,
            coordinates=[{"lat": 0, "lng": 0}],
            map_view_id="view1"
        )
        ann2 = Annotation(
            type=AnnotationType.POINT,
            coordinates=[{"lat": 1, "lng": 1}],
            map_view_id="view2"
        )
        ann3 = Annotation(
            type=AnnotationType.POINT,
            coordinates=[{"lat": 2, "lng": 2}],
            map_view_id="view1"
        )
        
        AnnotationService.create_annotation(ann1)
        AnnotationService.create_annotation(ann2)
        AnnotationService.create_annotation(ann3)
        
        result = AnnotationService.get_annotations(map_view_id="view1")
        
        assert len(result["annotations"]) == 2
        for ann in result["annotations"]:
            assert ann.map_view_id == "view1"
    
    def test_get_existing_annotation(self):
        """Test getting a specific annotation"""
        annotation = Annotation(
            type=AnnotationType.POINT,
            coordinates=[{"lat": 0, "lng": 0}],
            text="Test"
        )
        created = AnnotationService.create_annotation(annotation)
        
        retrieved = AnnotationService.get_annotation(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.text == "Test"
    
    def test_get_nonexistent_annotation(self):
        """Test getting an annotation that doesn't exist"""
        annotation = AnnotationService.get_annotation("nonexistent_id")
        
        assert annotation is None
    
    def test_update_annotation(self):
        """Test updating an annotation"""
        annotation = Annotation(
            type=AnnotationType.POINT,
            coordinates=[{"lat": 0, "lng": 0}],
            text="Original"
        )
        created = AnnotationService.create_annotation(annotation)
        
        # Update the annotation
        updated = Annotation(
            type=AnnotationType.POINT,
            coordinates=[{"lat": 1, "lng": 1}],
            text="Updated"
        )
        
        result = AnnotationService.update_annotation(created.id, updated)
        
        assert result is not None
        assert result.id == created.id
        assert result.text == "Updated"
        assert result.coordinates == [{"lat": 1, "lng": 1}]
        assert result.updated_at > created.updated_at
    
    def test_update_nonexistent_annotation(self):
        """Test updating an annotation that doesn't exist"""
        annotation = Annotation(
            type=AnnotationType.POINT,
            coordinates=[{"lat": 0, "lng": 0}]
        )
        result = AnnotationService.update_annotation("nonexistent_id", annotation)
        
        assert result is None
    
    def test_delete_annotation(self):
        """Test deleting an annotation"""
        annotation = Annotation(
            type=AnnotationType.POINT,
            coordinates=[{"lat": 0, "lng": 0}]
        )
        created = AnnotationService.create_annotation(annotation)
        
        success = AnnotationService.delete_annotation(created.id)
        
        assert success is True
        assert created.id not in annotations_db
        assert AnnotationService.get_annotation(created.id) is None
    
    def test_delete_nonexistent_annotation(self):
        """Test deleting an annotation that doesn't exist"""
        success = AnnotationService.delete_annotation("nonexistent_id")
        
        assert success is False
