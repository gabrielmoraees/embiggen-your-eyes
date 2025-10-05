"""
Unit tests for catalog service (discovery operations)
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.services.catalog_service import CatalogService
from app.models.enums import Category, Subject


class TestCatalogDiscovery:
    """Test catalog service discovery operations"""
    
    def test_get_categories(self):
        """Test getting all categories"""
        result = CatalogService.get_categories()
        
        assert "categories" in result
        categories = result["categories"]
        assert len(categories) > 0
        
        # Check structure
        for category in categories:
            assert "id" in category
            assert "name" in category
            assert "dataset_count" in category
            assert "subjects" in category
            assert "sources" in category
            assert category["dataset_count"] > 0
    
    def test_get_all_sources(self):
        """Test getting all sources"""
        result = CatalogService.get_sources()
        
        assert "sources" in result
        sources = result["sources"]
        assert len(sources) >= 5  # NASA GIBS, Trek, OPM, USGS, Custom
        
        # Check structure
        for source in sources:
            assert "id" in source
            assert "name" in source
            assert "description" in source
            assert "attribution" in source
            assert "dataset_count" in source
    
    def test_filter_sources_by_category(self):
        """Test filtering sources by category"""
        result = CatalogService.get_sources(category=Category.PLANETS)
        
        sources = result["sources"]
        assert len(sources) > 0
        
        # All sources should have at least one planet dataset
        for source in sources:
            assert source["dataset_count"] > 0
    
    def test_filter_sources_by_subject(self):
        """Test filtering sources by subject"""
        result = CatalogService.get_sources(subject=Subject.EARTH)
        
        sources = result["sources"]
        assert len(sources) > 0
        
        # Should include NASA GIBS (has Earth data)
        source_ids = [s["id"] for s in sources]
        assert "nasa_gibs" in source_ids