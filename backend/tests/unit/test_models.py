"""
Unit tests for data models and validation
"""
import pytest
from datetime import date
from pydantic import ValidationError
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from main import (
    CelestialBody,
    ImageLayer,
    BoundingBox,
    ImageSearchQuery,
    ImageMetadata,
    AnnotationType,
    Annotation,
    ImageLink,
    Collection
)


class TestCelestialBodyEnum:
    """Test CelestialBody enum"""
    
    def test_all_celestial_bodies_exist(self):
        """Test that all expected celestial bodies are defined"""
        expected = ["earth", "mars", "moon", "mercury", "custom"]
        actual = [body.value for body in CelestialBody]
        assert set(expected) == set(actual)
    
    def test_celestial_body_values(self):
        """Test celestial body enum values"""
        assert CelestialBody.EARTH.value == "earth"
        assert CelestialBody.MARS.value == "mars"
        assert CelestialBody.MERCURY.value == "mercury"
        assert CelestialBody.CUSTOM.value == "custom"


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


class TestImageSearchQuery:
    """Test ImageSearchQuery model"""
    
    def test_default_values(self):
        """Test default values for search query"""
        query = ImageSearchQuery()
        assert query.celestial_body == CelestialBody.EARTH
        assert query.projection == "epsg3857"
        assert query.limit == 50
    
    def test_custom_query(self):
        """Test creating a custom search query"""
        bbox = BoundingBox(north=45, south=40, east=-70, west=-75)
        query = ImageSearchQuery(
            celestial_body=CelestialBody.MARS,
            layer="opm_mars_basemap",
            bbox=bbox,
            limit=10
        )
        assert query.celestial_body == CelestialBody.MARS
        assert query.layer == "opm_mars_basemap"
        assert query.limit == 10


class TestImageMetadata:
    """Test ImageMetadata model"""
    
    def test_valid_metadata(self):
        """Test creating valid image metadata"""
        bbox = BoundingBox(north=90, south=-90, east=180, west=-180)
        metadata = ImageMetadata(
            id="test_123",
            layer="test_layer",
            date=date(2024, 1, 1),
            bbox=bbox,
            tile_url="https://example.com/{z}/{x}/{y}.jpg",
            thumbnail_url="https://example.com/thumb.jpg",
            max_zoom=9
        )
        assert metadata.id == "test_123"
        assert metadata.max_zoom == 9
        assert "{z}" in metadata.tile_url


class TestAnnotation:
    """Test Annotation model"""
    
    def test_annotation_types(self):
        """Test all annotation types are valid"""
        types = [AnnotationType.POINT, AnnotationType.POLYGON, 
                AnnotationType.RECTANGLE, AnnotationType.CIRCLE, AnnotationType.TEXT]
        assert len(types) == 5
    
    def test_create_annotation(self):
        """Test creating an annotation"""
        annotation = Annotation(
            image_id="test_image",
            type=AnnotationType.POINT,
            coordinates=[{"lat": 40.7, "lng": -74.0}],
            text="Test point",
            color="#FF0000"
        )
        assert annotation.image_id == "test_image"
        assert annotation.type == AnnotationType.POINT
        assert annotation.color == "#FF0000"


class TestImageLink:
    """Test ImageLink model"""
    
    def test_create_link(self):
        """Test creating an image link"""
        link = ImageLink(
            source_image_id="img1",
            target_image_id="img2",
            relationship_type="before_after",
            description="Comparison"
        )
        assert link.source_image_id == "img1"
        assert link.target_image_id == "img2"
        assert link.relationship_type == "before_after"


class TestCollection:
    """Test Collection model"""
    
    def test_create_collection(self):
        """Test creating a collection"""
        collection = Collection(
            name="Test Collection",
            description="Test description",
            image_ids=["img1", "img2", "img3"]
        )
        assert collection.name == "Test Collection"
        assert len(collection.image_ids) == 3
    
    def test_empty_collection(self):
        """Test creating an empty collection"""
        collection = Collection(name="Empty Collection")
        assert collection.image_ids == []
