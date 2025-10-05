"""
Catalog API routes for datasets, sources, and categories
"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from datetime import date

from app.models.enums import Category, Subject, SourceId
from app.services.catalog_service import CatalogService
from app.services.variant_service import VariantService

router = APIRouter()


@router.get("/categories")
def get_categories():
    """Get list of available categories"""
    return CatalogService.get_categories()


@router.get("/sources")
def get_sources(category: Optional[Category] = None, subject: Optional[Subject] = None):
    """Get list of sources, optionally filtered by category or subject"""
    return CatalogService.get_sources(category, subject)


@router.get("/datasets")
def get_datasets(
    category: Optional[Category] = None,
    subject: Optional[Subject] = None,
    source_id: Optional[SourceId] = None,
    supports_time_series: Optional[bool] = None
):
    """Get list of datasets with optional filters"""
    return CatalogService.get_datasets(category, subject, source_id, supports_time_series)


@router.get("/datasets/{dataset_id}")
def get_dataset(dataset_id: str):
    """Get details for a specific dataset"""
    dataset = CatalogService.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail=f"Dataset not found: {dataset_id}")
    return dataset


@router.get("/datasets/{dataset_id}/variants")
def get_dataset_variants(dataset_id: str):
    """Get variants for a specific dataset"""
    result = CatalogService.get_dataset_variants(dataset_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Dataset not found: {dataset_id}")
    return result


@router.get("/datasets/{dataset_id}/variants/{variant_id}")
def get_dataset_variant(dataset_id: str, variant_id: str, date_param: Optional[date] = None):
    """Get specific variant with resolved tile URLs"""
    result = VariantService.get_variant_with_resolved_urls(dataset_id, variant_id, date_param)
    if not result:
        raise HTTPException(status_code=404, detail=f"Dataset or variant not found")
    return result
