"""
Unit tests for enum types
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.models.enums import Category, Subject, SourceId, ProjectionType, AnnotationType


class TestEnums:
    """Test enum types"""
    
    def test_category_enum(self):
        """Test Category enum values"""
        assert Category.PLANETS.value == "planets"
        assert Category.MOONS.value == "moons"
        assert Category.GALAXIES.value == "galaxies"
        assert Category.CUSTOM.value == "custom"
    
    def test_subject_enum(self):
        """Test Subject enum values"""
        assert Subject.EARTH.value == "earth"
        assert Subject.MARS.value == "mars"
        assert Subject.MOON.value == "moon"
        assert Subject.CUSTOM.value == "custom"
    
    def test_source_id_enum(self):
        """Test SourceId enum values"""
        assert SourceId.NASA_GIBS.value == "nasa_gibs"
        assert SourceId.NASA_TREK.value == "nasa_trek"
        assert SourceId.OPENPLANETARYMAP.value == "openplanetarymap"
        assert SourceId.USGS.value == "usgs"
        assert SourceId.CUSTOM.value == "custom"
    
    def test_projection_type_enum(self):
        """Test ProjectionType enum values"""
        assert ProjectionType.WEB_MERCATOR.value == "epsg3857"
        assert ProjectionType.GEOGRAPHIC.value == "epsg4326"
    
    def test_annotation_type_enum(self):
        """Test AnnotationType enum values"""
        expected = ["point", "polygon", "rectangle", "circle", "text", "link"]
        actual = [ann_type.value for ann_type in AnnotationType]
        assert set(expected) == set(actual)
