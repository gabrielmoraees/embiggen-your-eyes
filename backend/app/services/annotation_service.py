"""
Annotation service for managing map annotations
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
from app.models.schemas import Annotation
from app.models.enums import AnnotationType
from app.data.storage import annotations_db, DATASETS


class AnnotationService:
    """Service for annotation operations"""
    
    @staticmethod
    def _validate_link_target(annotation: Annotation) -> Optional[str]:
        """
        Validate link target for LINK type annotations
        Returns error message if invalid, None if valid
        """
        if annotation.type != AnnotationType.LINK:
            return None
        
        if not annotation.link_target:
            return "link_target is required for LINK type annotations"
        
        # Validate dataset exists
        if annotation.link_target.dataset_id not in DATASETS:
            return f"Target dataset not found: {annotation.link_target.dataset_id}"
        
        # Validate variant exists in dataset
        dataset = DATASETS[annotation.link_target.dataset_id]
        variant_ids = [v.id for v in dataset.variants]
        if annotation.link_target.variant_id not in variant_ids:
            return f"Target variant not found: {annotation.link_target.variant_id}"
        
        return None
    
    @staticmethod
    def create_annotation(annotation: Annotation) -> Annotation:
        """Create a new annotation"""
        # Validate link target if it's a LINK type
        error = AnnotationService._validate_link_target(annotation)
        if error:
            raise ValueError(error)
        
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
        
        # Validate link target if it's a LINK type
        error = AnnotationService._validate_link_target(annotation)
        if error:
            raise ValueError(error)
        
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
