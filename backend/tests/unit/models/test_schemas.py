"""
Unit tests for Pydantic schemas
"""
import pytest
from datetime import date, datetime
from pydantic import ValidationError
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.models.enums import Category, Subject, SourceId, AnnotationType
from app.models.schemas import (
    Source,
    Variant,
    Dataset,
    View,
    Layer,
    BoundingBox,
    Annotation,
    ImageLink,
    Collection
)


class TestSource:
    """Test Source model"""
    
    def test_create_map_source(self):
        """Test creating a map source"""
        source = Source(
            id=SourceId.NASA_GIBS,
            name="NASA GIBS",
            description="NASA imagery service",
            attribution="NASA",
            url="https://nasa.gov"
        )
        assert source.id == SourceId.NASA_GIBS
        assert source.name == "NASA GIBS"


class TestVariant:
    """Test Variant model"""
    
    def test_create_variant(self):
        """Test creating a variant"""
        variant = Variant(
            id="true_color",
            name="True Color",
            description="Natural color",
            tile_url_template="https://example.com/{z}/{x}/{y}.jpg",
            thumbnail_url="https://example.com/thumb.jpg"
        )
        assert variant.id == "true_color"
        assert variant.is_default is False


class TestDataset:
    """Test Dataset model"""
    
    def test_create_static_map(self):
        """Test creating a static map"""
        variant = Variant(
            id="default",
            name="Default",
            description="Default view",
            tile_url_template="https://example.com/{z}/{x}/{y}.jpg",
            thumbnail_url="https://example.com/thumb.jpg"
        )
        
        dataset = Dataset(
            id="mars_map",
            name="Mars Dataset",
            description="Mars imagery",
            source_id=SourceId.NASA_TREK,
            category=Category.PLANETS,
            subject=Subject.MARS,
            supports_time_series=False,
            variants=[variant]
        )
        
        assert dataset.supports_time_series is False
        assert dataset.default_date is None
    
    def test_create_time_series_map(self):
        """Test creating a time-series map"""
        variant = Variant(
            id="true_color",
            name="True Color",
            description="Natural color",
            tile_url_template="https://example.com/{date}/{z}/{x}/{y}.jpg",
            thumbnail_url="https://example.com/{date}/thumb.jpg",
            is_default=True
        )
        
        dataset = Dataset(
            id="earth_map",
            name="Earth Dataset",
            description="Earth time-series",
            source_id=SourceId.NASA_GIBS,
            category=Category.PLANETS,
            subject=Subject.EARTH,
            supports_time_series=True,
            date_range_start=date(2020, 1, 1),
            date_range_end=date(2025, 12, 31),
            default_date=date(2025, 10, 4),
            variants=[variant]
        )
        
        assert dataset.supports_time_series is True
        assert dataset.default_date == date(2025, 10, 4)
        assert "{date}" in dataset.variants[0].tile_url_template


class TestView:
    """Test View model"""
    
    def test_create_map_view(self):
        """Test creating a map view"""
        view = View(
            name="My View",
            description="Test view",
            dataset_id="earth_map",
            variant_id="true_color",
            center_lat=40.7128,
            center_lng=-74.0060,
            zoom_level=10
        )
        
        assert view.name == "My View"
        assert view.dataset_id == "earth_map"
        assert view.zoom_level == 10


class TestLayer:
    """Test Layer model"""
    
    def test_create_layer(self):
        """Test creating a layer"""
        layer = Layer(
            id="borders",
            name="Country Borders",
            description="Political boundaries",
            tile_url_template="https://example.com/{z}/{x}/{y}.png",
            opacity=0.7
        )
        
        assert layer.id == "borders"
        assert layer.opacity == 0.7
        assert layer.enabled_by_default is False


class TestBoundingBox:
    """Test BoundingBox model"""
    
    def test_valid_bounding_box(self):
        """Test creating a valid bounding box"""
        bbox = BoundingBox(
            north=90.0,
            south=-90.0,
            east=180.0,
            west=-180.0
        )
        assert bbox.north == 90.0
        assert bbox.south == -90.0
    
    def test_bounding_box_validation(self):
        """Test bounding box with valid coordinates"""
        bbox = BoundingBox(
            north=40.0,
            south=30.0,
            east=-70.0,
            west=-80.0
        )
        assert bbox.north > bbox.south
        assert bbox.east > bbox.west


class TestAnnotation:
    """Test Annotation model"""
    
    def test_create_annotation(self):
        """Test creating an annotation"""
        annotation = Annotation(
            type=AnnotationType.POINT,
            coordinates=[{"lat": 40.7128, "lng": -74.0060}],
            text="New York City",
            color="#FF0000"
        )
        
        assert annotation.type == AnnotationType.POINT
        assert len(annotation.coordinates) == 1
        assert annotation.color == "#FF0000"


class TestImageLink:
    """Test ImageLink model"""
    
    def test_create_link(self):
        """Test creating an image link"""
        link = ImageLink(
            source_view_id="view1",
            target_view_id="view2",
            relationship_type="comparison",
            description="Compare two views"
        )
        
        assert link.source_view_id == "view1"
        assert link.target_view_id == "view2"
        assert link.relationship_type == "comparison"


class TestCollection:
    """Test Collection model"""
    
    def test_create_collection(self):
        """Test creating a collection"""
        collection = Collection(
            name="My Collection",
            description="Test collection",
            view_ids=["view1", "view2", "view3"]
        )
        
        assert collection.name == "My Collection"
        assert len(collection.view_ids) == 3
    
    def test_empty_collection(self):
        """Test creating an empty collection"""
        collection = Collection(
            name="Empty Collection"
        )
        
        assert len(collection.view_ids) == 0
