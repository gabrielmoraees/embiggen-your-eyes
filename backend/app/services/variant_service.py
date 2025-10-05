"""
Variant service for handling dataset variants and URL resolution
"""
from typing import Optional, Dict, Any
from datetime import date
from app.models.schemas import Dataset, Variant
from app.data.storage import DATASETS


class VariantService:
    """Service for variant operations"""
    
    @staticmethod
    def get_variant_with_resolved_urls(
        dataset_id: str,
        variant_id: str,
        date_param: Optional[date] = None
    ) -> Optional[Dict[str, Any]]:
        """Get specific variant with resolved tile URLs"""
        dataset = DATASETS.get(dataset_id)
        if not dataset:
            return None
        
        variant = next((v for v in dataset.variants if v.id == variant_id), None)
        if not variant:
            return None
        
        # Resolve date for time-series maps
        selected_date = date_param or dataset.default_date or date.today()
        
        # Replace {date} placeholder in URLs if needed
        tile_url = variant.tile_url_template
        thumbnail_url = variant.thumbnail_url
        
        if dataset.supports_time_series:
            date_str = selected_date.strftime("%Y-%m-%d")
            tile_url = tile_url.replace("{date}", date_str)
            thumbnail_url = thumbnail_url.replace("{date}", date_str)
        
        return {
            "dataset_id": dataset_id,
            "variant": {
                **variant.model_dump(),
                "tile_url": tile_url,
                "thumbnail_url": thumbnail_url,
                "selected_date": selected_date if dataset.supports_time_series else None
            }
        }
