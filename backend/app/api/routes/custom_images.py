"""
Custom image API routes for user uploads
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Optional

from app.models.enums import Category, Subject
from app.services.custom_image_service import CustomImageService

router = APIRouter()


class CustomImageUpload(BaseModel):
    """Request model for custom image upload"""
    image_url: HttpUrl
    name: str
    description: Optional[str] = None
    category: Optional[Category] = Category.CUSTOM
    subject: Optional[Subject] = Subject.CUSTOM


@router.post("/custom-images")
def upload_custom_image(upload: CustomImageUpload):
    """
    Upload a custom image from URL
    
    The image will be:
    1. Downloaded and processed into tiles
    2. Added as a new dataset
    3. Available for use like any other dataset
    
    Returns the created dataset and processing status
    """
    try:
        result = CustomImageService.create_custom_dataset_from_url(
            image_url=str(upload.image_url),
            name=upload.name,
            description=upload.description,
            category=upload.category,
            subject=upload.subject
        )
        
        return {
            "success": True,
            "dataset_id": result["dataset"].id,
            "dataset": result["dataset"],
            "status": result["status"],
            "message": result["message"]
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process custom image: {str(e)}"
        )


@router.get("/custom-images")
def list_custom_images():
    """List all custom user-uploaded datasets"""
    return CustomImageService.list_custom_datasets()


@router.delete("/custom-images/{dataset_id}")
def delete_custom_image(dataset_id: str):
    """Delete a custom dataset"""
    success = CustomImageService.delete_custom_dataset(dataset_id)
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Custom dataset not found"
        )
    
    return {"message": "Custom dataset deleted successfully"}


@router.get("/tile-status/{tile_id}")
def get_tile_status(tile_id: str):
    """
    Get the processing status of tiles
    
    Use this to poll for tile processing completion
    """
    result = CustomImageService.get_tile_status(tile_id)
    
    if result["status"] == "not_found":
        raise HTTPException(status_code=404, detail="Tile ID not found")
    
    return result
