"""
Annotation API routes
"""
from fastapi import APIRouter, HTTPException
from typing import Optional

from app.models.schemas import Annotation
from app.services.annotation_service import AnnotationService

router = APIRouter()


@router.post("/annotations", response_model=Annotation)
def create_annotation(annotation: Annotation):
    """Create a new annotation"""
    try:
        return AnnotationService.create_annotation(annotation)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/annotations")
def get_annotations(map_view_id: Optional[str] = None):
    """Get annotations, optionally filtered by map view"""
    return AnnotationService.get_annotations(map_view_id)


@router.get("/annotations/{annotation_id}", response_model=Annotation)
def get_annotation(annotation_id: str):
    """Get a specific annotation"""
    annotation = AnnotationService.get_annotation(annotation_id)
    if not annotation:
        raise HTTPException(status_code=404, detail="Annotation not found")
    return annotation


@router.put("/annotations/{annotation_id}", response_model=Annotation)
def update_annotation(annotation_id: str, annotation: Annotation):
    """Update an annotation"""
    try:
        updated_annotation = AnnotationService.update_annotation(annotation_id, annotation)
        if not updated_annotation:
            raise HTTPException(status_code=404, detail="Annotation not found")
        return updated_annotation
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/annotations/{annotation_id}")
def delete_annotation(annotation_id: str):
    """Delete an annotation"""
    if not AnnotationService.delete_annotation(annotation_id):
        raise HTTPException(status_code=404, detail="Annotation not found")
    return {"message": "Annotation deleted successfully"}
