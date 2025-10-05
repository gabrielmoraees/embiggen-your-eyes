"""
Unit tests for dataset service operations
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.services.catalog_service import CatalogService
from app.models.enums import Category, Subject, SourceId


class TestDatasetOperations:
    """Test dataset listing and retrieval operations"""
    
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
