"""
Unit tests for annotation service
"""
import pytest
import sys
from pathlib import Path
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.services.annotation_service import AnnotationService
from app.models.schemas import Annotation, LinkTarget
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


class TestLinkAnnotations:
    """Test link annotation specific functionality"""
    
    def setup_method(self):
        """Clear annotations before each test"""
        annotations_db.clear()
    
    def test_create_link_annotation(self):
        """Test creating a link annotation"""
        link_annotation = Annotation(
            type=AnnotationType.LINK,
            coordinates=[{"lat": 25.0, "lng": -80.0}],
            text="See Mars dust storm",
            color="#0066CC",
            link_target=LinkTarget(
                dataset_id="mars_viking",
                variant_id="colorized",
                center_lat=-14.5,
                center_lng=175.4,
                zoom_level=6
            )
        )
        
        created = AnnotationService.create_annotation(link_annotation)
        
        assert created.id is not None
        assert created.type == AnnotationType.LINK
        assert created.link_target is not None
        assert created.link_target.dataset_id == "mars_viking"
        assert created.link_target.variant_id == "colorized"
    
    def test_create_link_without_target_fails(self):
        """Test that creating a LINK without link_target fails at Pydantic validation"""
        with pytest.raises(ValidationError):
            Annotation(
                type=AnnotationType.LINK,
                coordinates=[{"lat": 25.0, "lng": -80.0}],
                text="Invalid link"
            )
    
    def test_create_link_with_invalid_dataset(self):
        """Test that creating a LINK with invalid dataset fails"""
        link_annotation = Annotation(
            type=AnnotationType.LINK,
            coordinates=[{"lat": 25.0, "lng": -80.0}],
            text="Invalid dataset link",
            link_target=LinkTarget(
                dataset_id="nonexistent_dataset",
                variant_id="some_variant"
            )
        )
        
        with pytest.raises(ValueError, match="Target dataset not found"):
            AnnotationService.create_annotation(link_annotation)
    
    def test_create_link_with_invalid_variant(self):
        """Test that creating a LINK with invalid variant fails"""
        link_annotation = Annotation(
            type=AnnotationType.LINK,
            coordinates=[{"lat": 25.0, "lng": -80.0}],
            text="Invalid variant link",
            link_target=LinkTarget(
                dataset_id="viirs_snpp",
                variant_id="nonexistent_variant"
            )
        )
        
        with pytest.raises(ValueError, match="Target variant not found"):
            AnnotationService.create_annotation(link_annotation)
    
    def test_create_non_link_with_target_fails(self):
        """Test that non-LINK annotations cannot have link_target"""
        with pytest.raises(ValidationError):
            Annotation(
                type=AnnotationType.POINT,
                coordinates=[{"lat": 25.0, "lng": -80.0}],
                text="Point with link target",
                link_target=LinkTarget(
                    dataset_id="mars_viking",
                    variant_id="colorized"
                )
            )
    
    def test_update_link_annotation(self):
        """Test updating a link annotation"""
        link_annotation = Annotation(
            type=AnnotationType.LINK,
            coordinates=[{"lat": 25.0, "lng": -80.0}],
            text="Original link",
            link_target=LinkTarget(
                dataset_id="mars_viking",
                variant_id="colorized"
            )
        )
        
        created = AnnotationService.create_annotation(link_annotation)
        
        # Update the link
        updated_link = Annotation(
            type=AnnotationType.LINK,
            coordinates=[{"lat": 26.0, "lng": -81.0}],
            text="Updated link",
            link_target=LinkTarget(
                dataset_id="viirs_snpp",
                variant_id="true_color",
                zoom_level=8
            )
        )
        
        result = AnnotationService.update_annotation(created.id, updated_link)
        
        assert result is not None
        assert result.text == "Updated link"
        assert result.link_target.dataset_id == "viirs_snpp"
        assert result.link_target.variant_id == "true_color"
    
    def test_link_target_preserve_options(self):
        """Test link target preserve options"""
        link_annotation = Annotation(
            type=AnnotationType.LINK,
            coordinates=[{"lat": 25.0, "lng": -80.0}],
            text="Link with preserve options",
            link_target=LinkTarget(
                dataset_id="mars_viking",
                variant_id="colorized",
                preserve_zoom=False,
                preserve_layers=True
            )
        )
        
        created = AnnotationService.create_annotation(link_annotation)
        
        assert created.link_target.preserve_zoom is False
        assert created.link_target.preserve_layers is True
    
    def test_link_with_optional_position(self):
        """Test link with optional center position"""
        link_annotation = Annotation(
            type=AnnotationType.LINK,
            coordinates=[{"lat": 25.0, "lng": -80.0}],
            text="Link without target position",
            link_target=LinkTarget(
                dataset_id="mars_viking",
                variant_id="colorized"
            )
        )
        
        created = AnnotationService.create_annotation(link_annotation)
        
        assert created.link_target.center_lat is None
        assert created.link_target.center_lng is None
    
    def test_delete_link_annotation(self):
        """Test deleting a link annotation"""
        link_annotation = Annotation(
            type=AnnotationType.LINK,
            coordinates=[{"lat": 25.0, "lng": -80.0}],
            text="Link to delete",
            link_target=LinkTarget(
                dataset_id="mars_viking",
                variant_id="colorized"
            )
        )
        
        created = AnnotationService.create_annotation(link_annotation)
        success = AnnotationService.delete_annotation(created.id)
        
        assert success is True
        assert created.id not in annotations_db
