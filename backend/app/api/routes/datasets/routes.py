"""
Dataset API routes - CRUD operations and dataset management
"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from datetime import date, datetime

from app.models.enums import Category, Subject, SourceId
from app.models.schemas import DatasetCreateRequest, DatasetUpdateRequest
from app.services.catalog_service import CatalogService
from app.services.variant_service import VariantService
from app.services.dataset_service import DatasetService
from app.data.storage import DATASETS

router = APIRouter()


@router.post("")
def create_dataset(request: DatasetCreateRequest):
    """
    Create a new dataset from URL
    
    The URL can be either:
    - A tile service URL (with {z}/{x}/{y} or {bbox} placeholders)
    - An image file URL (.jpg, .png, .tif, etc.)
    
    The endpoint automatically detects the type and processes accordingly.
    """
    result = DatasetService.create_dataset(request)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to create dataset"))
    
    return result


@router.get("")
def get_datasets(
    category: Optional[Category] = None,
    subject: Optional[Subject] = None,
    source_id: Optional[SourceId] = None,
    supports_time_series: Optional[bool] = None
):
    """Get list of datasets with optional filters"""
    return CatalogService.get_datasets(category, subject, source_id, supports_time_series)


@router.get("/{dataset_id}")
def get_dataset(dataset_id: str):
    """Get details for a specific dataset"""
    dataset = CatalogService.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail=f"Dataset not found: {dataset_id}")
    return dataset


@router.get("/{dataset_id}/status")
def get_dataset_status(dataset_id: str):
    """Get processing status for a dataset"""
    from app.services import tile_processor as tile_processor_module
    
    tile_processor = tile_processor_module.tile_processor
    
    # Check if dataset exists
    if dataset_id not in DATASETS:
        raise HTTPException(status_code=404, detail=f"Dataset not found: {dataset_id}")
    
    dataset = DATASETS[dataset_id]
    
    # If dataset doesn't have tile processing, just return current status
    if not hasattr(dataset, 'tile_id') or not dataset.tile_id:
        return {
            "dataset_id": dataset_id,
            "status": getattr(dataset, 'processing_status', 'ready') or "ready"
        }
    
    tile_id = dataset.tile_id
    
    # Check if tiles are ready
    tile_index = getattr(tile_processor, 'tile_index', {})
    tile_info = tile_index.get(tile_id)
    
    if tile_info and tile_info.get('status') == 'completed':
        # Auto-update dataset status
        if dataset.processing_status == "processing":
            dataset.processing_status = "ready"
            dataset.updated_at = datetime.now()
        
        return {
            "dataset_id": dataset_id,
            "status": "ready",
            "tile_info": tile_info
        }
    
    # Check if currently processing
    processing_status_dict = getattr(tile_processor, 'processing_status', {})
    processing_status = processing_status_dict.get(tile_id)
    if processing_status:
        return {
            "dataset_id": dataset_id,
            "status": "processing",
            "progress": processing_status.get('progress'),
            "started_at": processing_status.get('started_at')
        }
    
    # Return current dataset status
    return {
        "dataset_id": dataset_id,
        "status": getattr(dataset, 'processing_status', 'ready') or "ready"
    }


@router.put("/{dataset_id}")
@router.patch("/{dataset_id}")
def update_dataset(dataset_id: str, request: DatasetUpdateRequest):
    """
    Update a dataset's metadata (only custom datasets can be updated)
    
    Supports both PUT and PATCH methods.
    Only name, description, category, and subject can be updated.
    """
    result = DatasetService.update_dataset(dataset_id, request)
    
    if not result.get("success"):
        if "not found" in result.get("error", "").lower():
            raise HTTPException(status_code=404, detail=result.get("error"))
        else:
            raise HTTPException(status_code=403, detail=result.get("error"))
    
    return result


@router.delete("/{dataset_id}")
def delete_dataset(dataset_id: str):
    """Delete a dataset (only custom datasets can be deleted)"""
    # Check if dataset exists
    if dataset_id not in DATASETS:
        raise HTTPException(status_code=404, detail=f"Dataset not found: {dataset_id}")
    
    dataset = DATASETS[dataset_id]
    
    # Only allow deleting custom datasets
    if dataset.source_id != SourceId.CUSTOM:
        raise HTTPException(status_code=403, detail="Can only delete custom datasets")
    
    # Delete the dataset
    del DATASETS[dataset_id]
    
    return {"success": True, "message": f"Dataset {dataset_id} deleted successfully"}


@router.get("/{dataset_id}/variants")
def get_dataset_variants(dataset_id: str):
    """Get variants for a specific dataset"""
    result = CatalogService.get_dataset_variants(dataset_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Dataset not found: {dataset_id}")
    return result


@router.get("/{dataset_id}/variants/{variant_id}")
def get_dataset_variant(dataset_id: str, variant_id: str, date_param: Optional[date] = None):
    """Get specific variant with resolved tile URLs"""
    result = VariantService.get_variant_with_resolved_urls(dataset_id, variant_id, date_param)
    if not result:
        raise HTTPException(status_code=404, detail=f"Dataset or variant not found")
    return result
