"""
Annotation service for managing map annotations
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
from app.models.schemas import Annotation
from app.data.storage import annotations_db


class AnnotationService:
    """Service for annotation operations"""
    
    @staticmethod
    def create_annotation(annotation: Annotation) -> Annotation:
        """Create a new annotation"""
        annotation.id = str(uuid.uuid4())
        annotation.created_at = datetime.now()
        annotation.updated_at = datetime.now()
        annotations_db[annotation.id] = annotation
        return annotation
    
    @staticmethod
    def get_annotations(map_view_id: Optional[str] = None) -> Dict[str, Any]:
        """Get annotations, optionally filtered by map view"""
        if map_view_id:
            filtered = [a for a in annotations_db.values() if a.map_view_id == map_view_id]
            return {"annotations": filtered}
        return {"annotations": list(annotations_db.values())}
    
    @staticmethod
    def get_annotation(annotation_id: str) -> Optional[Annotation]:
        """Get a specific annotation"""
        return annotations_db.get(annotation_id)
    
    @staticmethod
    def update_annotation(annotation_id: str, annotation: Annotation) -> Optional[Annotation]:
        """Update an annotation"""
        if annotation_id not in annotations_db:
            return None
        
        annotation.id = annotation_id
        annotation.updated_at = datetime.now()
        annotations_db[annotation_id] = annotation
        return annotation
    
    @staticmethod
    def delete_annotation(annotation_id: str) -> bool:
        """Delete an annotation"""
        if annotation_id not in annotations_db:
            return False
        
        del annotations_db[annotation_id]
        return True
