"""
Unit tests for catalog service
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.services.catalog_service import CatalogService
from app.models.enums import Category, Subject, SourceId


class TestCatalogService:
    """Test catalog service business logic"""
    
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
    
    def test_get_all_datasets(self):
        """Test getting all datasets"""
        result = CatalogService.get_datasets()
        
        assert "datasets" in result
        assert "count" in result
        datasets = result["datasets"]
        assert len(datasets) == result["count"]
        assert len(datasets) >= 7  # Current catalog size
    
    def test_filter_datasets_by_category(self):
        """Test filtering datasets by category"""
        result = CatalogService.get_datasets(category=Category.PLANETS)
        
        datasets = result["datasets"]
        assert len(datasets) > 0
        
        # All datasets should be planets
        for dataset in datasets:
            assert dataset.category == Category.PLANETS
    
    def test_filter_datasets_by_subject(self):
        """Test filtering datasets by subject"""
        result = CatalogService.get_datasets(subject=Subject.MARS)
        
        datasets = result["datasets"]
        assert len(datasets) >= 2  # Mars Viking and Mars OPM
        
        # All datasets should be Mars
        for dataset in datasets:
            assert dataset.subject == Subject.MARS
    
    def test_filter_datasets_by_source(self):
        """Test filtering datasets by source"""
        result = CatalogService.get_datasets(source_id=SourceId.NASA_GIBS)
        
        datasets = result["datasets"]
        assert len(datasets) >= 2  # VIIRS and MODIS
        
        # All datasets should be from NASA GIBS
        for dataset in datasets:
            assert dataset.source_id == SourceId.NASA_GIBS
    
    def test_filter_datasets_by_time_series(self):
        """Test filtering datasets by time series support"""
        result = CatalogService.get_datasets(supports_time_series=True)
        
        datasets = result["datasets"]
        assert len(datasets) > 0
        
        # All datasets should support time series
        for dataset in datasets:
            assert dataset.supports_time_series is True
    
    def test_filter_datasets_multiple_criteria(self):
        """Test filtering datasets with multiple criteria"""
        result = CatalogService.get_datasets(
            category=Category.PLANETS,
            subject=Subject.EARTH,
            supports_time_series=True
        )
        
        datasets = result["datasets"]
        assert len(datasets) >= 2  # VIIRS and MODIS
        
        # All datasets should match all criteria
        for dataset in datasets:
            assert dataset.category == Category.PLANETS
            assert dataset.subject == Subject.EARTH
            assert dataset.supports_time_series is True
    
    def test_get_existing_dataset(self):
        """Test getting a specific dataset"""
        dataset = CatalogService.get_dataset("viirs_snpp")
        
        assert dataset is not None
        assert dataset.id == "viirs_snpp"
        assert dataset.name == "VIIRS SNPP"
    
    def test_get_nonexistent_dataset(self):
        """Test getting a dataset that doesn't exist"""
        dataset = CatalogService.get_dataset("nonexistent")
        
        assert dataset is None
    
    def test_get_dataset_variants(self):
        """Test getting variants for a dataset"""
        result = CatalogService.get_dataset_variants("viirs_snpp")
        
        assert result is not None
        assert "dataset_id" in result
        assert "dataset_name" in result
        assert "variants" in result
        assert result["dataset_id"] == "viirs_snpp"
        assert len(result["variants"]) == 2  # True color and false color
    
    def test_get_variants_for_nonexistent_dataset(self):
        """Test getting variants for dataset that doesn't exist"""
        result = CatalogService.get_dataset_variants("nonexistent")
        
        assert result is None
