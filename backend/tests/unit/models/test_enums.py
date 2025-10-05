"""
Unit tests for enumeration types
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.models.enums import (
    Category,
    Subject,
    SourceId,
    ProjectionType,
    AnnotationType
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
        expected = ["point", "polygon", "rectangle", "circle", "text"]
        actual = [ann_type.value for ann_type in AnnotationType]
        assert set(expected) == set(actual)
