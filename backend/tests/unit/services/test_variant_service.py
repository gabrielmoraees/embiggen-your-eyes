"""
Unit tests for variant service
"""
import pytest
from datetime import date
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.services.variant_service import VariantService


class TestVariantService:
    """Test variant service business logic"""
    
    def test_get_variant_for_static_map(self):
        """Test getting variant for static (non-time-series) map"""
        result = VariantService.get_variant_with_resolved_urls(
            "mars_viking",
            "colorized"
        )
        
        assert result is not None
        assert "dataset_id" in result
        assert "variant" in result
        
        variant = result["variant"]
        assert variant["id"] == "colorized"
        assert "tile_url" in variant
        assert "thumbnail_url" in variant
        assert variant["selected_date"] is None  # No date for static maps
        assert "{date}" not in variant["tile_url"]
    
    def test_get_variant_for_time_series_map_with_date(self):
        """Test getting variant for time-series map with specific date"""
        test_date = date(2025, 10, 4)
        result = VariantService.get_variant_with_resolved_urls(
            "viirs_snpp",
            "true_color",
            date_param=test_date
        )
        
        assert result is not None
        variant = result["variant"]
        
        # Date should be resolved in URLs
        assert "2025-10-04" in variant["tile_url"]
        assert "2025-10-04" in variant["thumbnail_url"]
        assert variant["selected_date"] == test_date
        assert "{date}" not in variant["tile_url"]
    
    def test_get_variant_for_time_series_map_without_date(self):
        """Test getting variant for time-series map without date (uses default)"""
        result = VariantService.get_variant_with_resolved_urls(
            "viirs_snpp",
            "true_color"
        )
        
        assert result is not None
        variant = result["variant"]
        
        # Should use default date or today
        assert variant["selected_date"] is not None
        assert "{date}" not in variant["tile_url"]
        # Date should be in YYYY-MM-DD format in URL
        import re
        assert re.search(r'\d{4}-\d{2}-\d{2}', variant["tile_url"])
    
    def test_get_variant_for_nonexistent_dataset(self):
        """Test getting variant for dataset that doesn't exist"""
        result = VariantService.get_variant_with_resolved_urls(
            "nonexistent",
            "variant"
        )
        
        assert result is None
    
    def test_get_nonexistent_variant(self):
        """Test getting variant that doesn't exist for a dataset"""
        result = VariantService.get_variant_with_resolved_urls(
            "viirs_snpp",
            "nonexistent_variant"
        )
        
        assert result is None
    
    def test_variant_url_resolution_preserves_template_placeholders(self):
        """Test that z/x/y placeholders are preserved in resolved URLs"""
        result = VariantService.get_variant_with_resolved_urls(
            "mars_viking",
            "colorized"
        )
        
        variant = result["variant"]
        
        # Tile placeholders should be preserved
        assert "{z}" in variant["tile_url"]
        assert "{x}" in variant["tile_url"]
        assert "{y}" in variant["tile_url"]
    
    def test_multiple_variants_for_same_dataset(self):
        """Test getting different variants for the same dataset"""
        result1 = VariantService.get_variant_with_resolved_urls(
            "viirs_snpp",
            "true_color"
        )
        result2 = VariantService.get_variant_with_resolved_urls(
            "viirs_snpp",
            "false_color"
        )
        
        assert result1 is not None
        assert result2 is not None
        assert result1["variant"]["id"] == "true_color"
        assert result2["variant"]["id"] == "false_color"
        assert result1["variant"]["tile_url"] != result2["variant"]["tile_url"]
