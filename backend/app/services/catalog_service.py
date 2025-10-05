"""
Catalog service for managing datasets, sources, and categories
"""
from typing import Optional, List, Dict, Any
from app.models.enums import Category, Subject, SourceId, get_enum_order
from app.models.schemas import Source, Dataset
from app.data.storage import SOURCES, DATASETS


class CatalogService:
    """Service for catalog operations"""
    
    @staticmethod
    def get_categories() -> Dict[str, Any]:
        """Get list of available categories with metadata"""
        categories = {}
        for dataset in DATASETS.values():
            cat = dataset.category.value
            if cat not in categories:
                categories[cat] = {
                    "id": cat,
                    "name": cat.replace('_', ' ').title(),
                    "dataset_count": 0,
                    "subjects": set(),
                    "sources": set()
                }
            categories[cat]["dataset_count"] += 1
            categories[cat]["subjects"].add(dataset.subject.value)
            categories[cat]["sources"].add(dataset.source_id.value)
        
        # Convert sets to sorted lists for JSON serialization
        for cat in categories.values():
            # Sort subjects by enum order, then alphabetically for unordered ones
            subjects = list(cat["subjects"])
            cat["subjects"] = sorted(
                subjects,
                key=lambda s: (get_enum_order(Subject, s), s)
            )
            cat["sources"] = sorted(list(cat["sources"]))
        
        # Sort categories by enum order, then alphabetically for unordered ones
        sorted_categories = sorted(
            categories.values(),
            key=lambda c: (get_enum_order(Category, c["id"]), c["id"])
        )
        
        return {"categories": sorted_categories}
    
    @staticmethod
    def get_sources(
        category: Optional[Category] = None,
        subject: Optional[Subject] = None
    ) -> Dict[str, Any]:
        """Get list of sources with optional filtering"""
        sources = []
        for source in SOURCES.values():
            # Count datasets for this source
            dataset_count = sum(
                1 for d in DATASETS.values()
                if d.source_id == source.id and (
                    category is None or d.category == category
                ) and (
                    subject is None or d.subject == subject
                )
            )
            
            if dataset_count > 0 or (category is None and subject is None):
                sources.append({
                    **source.model_dump(),
                    "dataset_count": dataset_count
                })
        
        return {"sources": sources}
    
    @staticmethod
    def get_datasets(
        category: Optional[Category] = None,
        subject: Optional[Subject] = None,
        source_id: Optional[SourceId] = None,
        supports_time_series: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Get filtered list of datasets"""
        filtered_datasets = []
        
        for dataset in DATASETS.values():
            # Apply filters
            if category and dataset.category != category:
                continue
            if subject and dataset.subject != subject:
                continue
            if source_id and dataset.source_id != source_id:
                continue
            if supports_time_series is not None and dataset.supports_time_series != supports_time_series:
                continue
            
            filtered_datasets.append(dataset)
        
        return {"datasets": filtered_datasets, "count": len(filtered_datasets)}
    
    @staticmethod
    def get_dataset(dataset_id: str) -> Optional[Dataset]:
        """Get a specific dataset by ID"""
        return DATASETS.get(dataset_id)
    
    @staticmethod
    def get_dataset_variants(dataset_id: str) -> Optional[Dict[str, Any]]:
        """Get variants for a specific dataset"""
        dataset = DATASETS.get(dataset_id)
        if not dataset:
            return None
        
        return {
            "dataset_id": dataset_id,
            "dataset_name": dataset.name,
            "variants": dataset.variants
        }
