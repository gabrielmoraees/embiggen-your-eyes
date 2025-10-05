"""
View API routes for user-saved map configurations
"""
from fastapi import APIRouter, HTTPException

from app.models.schemas import View
from app.services.view_service import ViewService

router = APIRouter()


@router.post("/views", response_model=View)
def create_map_view(view: View):
    """Create a new saved map view"""
    # Validate map and variant exist
    is_valid, error_msg = ViewService.validate_view(view)
    if not is_valid:
        raise HTTPException(status_code=404, detail=error_msg)
    
    return ViewService.create_view(view)


@router.get("/views")
def get_map_views():
    """Get all saved map views"""
    return ViewService.get_all_views()


@router.get("/views/{view_id}", response_model=View)
def get_map_view(view_id: str):
    """Get a specific map view"""
    view = ViewService.get_view(view_id)
    if not view:
        raise HTTPException(status_code=404, detail="View not found")
    return view


@router.put("/views/{view_id}", response_model=View)
def update_map_view(view_id: str, view: View):
    """Update a map view"""
    updated_view = ViewService.update_view(view_id, view)
    if not updated_view:
        raise HTTPException(status_code=404, detail="View not found")
    return updated_view


@router.delete("/views/{view_id}")
def delete_map_view(view_id: str):
    """Delete a map view"""
    if not ViewService.delete_view(view_id):
        raise HTTPException(status_code=404, detail="View not found")
    return {"message": "View deleted successfully"}
