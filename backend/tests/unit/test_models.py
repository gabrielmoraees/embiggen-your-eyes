"""
Unit tests for data models and validation
"""
import pytest
from datetime import date, datetime
from pydantic import ValidationError
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.models.enums import (
    Category,
    Subject,
    SourceId,
    ProjectionType,
    AnnotationType
)
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


class TestEnums:
    """Test enum definitions"""
    
    def test_category_enum(self):
        """Test Category enum values"""
        expected = ["planets", "moons", "dwarf_planets", "galaxies", "nebulae", "star_clusters", "phenomena", "regions", "custom"]
        actual = [cat.value for cat in Category]
        assert set(expected) == set(actual)
    
    def test_subject_enum(self):
        """Test Subject enum values"""
        # Just test that key subjects exist
        assert Subject.EARTH.value == "earth"
        assert Subject.MARS.value == "mars"
        assert Subject.MOON.value == "moon"
        assert Subject.MERCURY.value == "mercury"
    
    def test_source_enum(self):
        """Test SourceId enum values"""
        expected = ["nasa_gibs", "nasa_trek", "openplanetarymap", "usgs", "custom"]
        actual = [source.value for source in SourceId]
        assert set(expected) == set(actual)
    
    def test_projection_enum(self):
        """Test ProjectionType enum values"""
        assert ProjectionType.WEB_MERCATOR.value == "epsg3857"
        assert ProjectionType.GEOGRAPHIC.value == "epsg4326"
    
    def test_annotation_type_enum(self):
        """Test AnnotationType enum values"""
        types = [AnnotationType.POINT, AnnotationType.POLYGON, 
                AnnotationType.RECTANGLE, AnnotationType.CIRCLE, AnnotationType.TEXT]
        assert len(types) == 5


class TestSource:
    """Test Source model"""
    
    def test_create_map_source(self):
        """Test creating a map source"""
        source = Source(
            id=SourceId.NASA_GIBS,
            name="NASA GIBS",
            description="Global Imagery Browse Services",
            attribution="NASA EOSDIS",
            url="https://earthdata.nasa.gov/gibs",
            terms_of_use="Public domain"
        )
        assert source.id == SourceId.NASA_GIBS
        assert source.name == "NASA GIBS"
        assert source.url == "https://earthdata.nasa.gov/gibs"


class TestVariant:
    """Test Variant model"""
    
    def test_create_variant(self):
        """Test creating a map variant"""
        variant = Variant(
            id="true_color",
            name="True Color",
            description="Natural color composite",
            tile_url_template="https://example.com/{z}/{x}/{y}.jpg",
            thumbnail_url="https://example.com/thumb.jpg",
            max_zoom=9,
            is_default=True
        )
        assert variant.id == "true_color"
        assert variant.is_default is True
        assert "{z}" in variant.tile_url_template


class TestMap:
    """Test Dataset model"""
    
    def test_create_static_map(self):
        """Test creating a static (non-time-series) map"""
        variant = Variant(
            id="default",
            name="Default",
            description="Default view",
            tile_url_template="https://example.com/{z}/{x}/{y}.png",
            thumbnail_url="https://example.com/thumb.png",
            is_default=True
        )
        
        dataset = Dataset(
            id="test_map",
            name="Test Dataset",
            description="A test map",
            source_id=SourceId.OPENPLANETARYMAP,
            category=Category.PLANETS,
            subject=Subject.MARS,
            supports_time_series=False,
            variants=[variant]
        )
        
        assert dataset.id == "test_map"
        assert dataset.supports_time_series is False
        assert len(dataset.variants) == 1
        assert dataset.category == Category.PLANETS
        assert dataset.subject == Subject.MARS
    
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
        """Test creating a user-saved map view"""
        view = View(
            name="My Favorite View",
            description="A beautiful view of Earth",
            dataset_id="viirs_snpp",
            variant_id="true_color",
            selected_date=date(2025, 10, 4),
            center_lat=40.7128,
            center_lng=-74.0060,
            zoom_level=8,
            active_layers=["labels", "borders"],
            annotation_ids=["ann1", "ann2"]
        )
        
        assert view.name == "My Favorite View"
        assert view.dataset_id == "viirs_snpp"
        assert view.variant_id == "true_color"
        assert view.zoom_level == 8
        assert len(view.active_layers) == 2
        assert len(view.annotation_ids) == 2


class TestLayer:
    """Test Layer model"""
    
    def test_create_layer(self):
        """Test creating an overlayable layer"""
        layer = Layer(
            id="labels",
            name="Labels",
            description="Place name labels",
            tile_url_template="https://example.com/labels/{z}/{x}/{y}.png",
            opacity=0.8,
            blend_mode="normal",
            enabled_by_default=False
        )
        
        assert layer.id == "labels"
        assert layer.opacity == 0.8
        assert layer.enabled_by_default is False


class TestBoundingBox:
    """Test BoundingBox model"""
    
    def test_valid_bounding_box(self):
        """Test creating a valid bounding box"""
        bbox = BoundingBox(north=90, south=-90, east=180, west=-180)
        assert bbox.north == 90
        assert bbox.south == -90
        assert bbox.east == 180
        assert bbox.west == -180
    
    def test_bounding_box_validation(self):
        """Test bounding box requires all fields"""
        with pytest.raises(ValidationError):
            BoundingBox(north=90, south=-90)  # Missing east and west


class TestAnnotation:
    """Test Annotation model"""
    
    def test_create_annotation(self):
        """Test creating an annotation"""
        annotation = Annotation(
            map_view_id="view_123",
            type=AnnotationType.POINT,
            coordinates=[{"lat": 40.7, "lng": -74.0}],
            text="Test point",
            color="#FF0000"
        )
        assert annotation.map_view_id == "view_123"
        assert annotation.type == AnnotationType.POINT
        assert annotation.color == "#FF0000"


class TestImageLink:
    """Test ImageLink model (now for Views)"""
    
    def test_create_link(self):
        """Test creating a link between map views"""
        link = ImageLink(
            source_view_id="view1",
            target_view_id="view2",
            relationship_type="before_after",
            description="Comparison"
        )
        assert link.source_view_id == "view1"
        assert link.target_view_id == "view2"
        assert link.relationship_type == "before_after"


class TestCollection:
    """Test Collection model (now for Views)"""
    
    def test_create_collection(self):
        """Test creating a collection of map views"""
        collection = Collection(
            name="Test Collection",
            description="Test description",
            view_ids=["view1", "view2", "view3"]
        )
        assert collection.name == "Test Collection"
        assert len(collection.view_ids) == 3
    
    def test_empty_collection(self):
        """Test creating an empty collection"""
        collection = Collection(name="Empty Collection")
        assert collection.view_ids == []