"""
View service for managing user-saved map views
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
from app.models.schemas import View
from app.data.storage import views_db, DATASETS


class ViewService:
    """Service for view operations"""
    
    @staticmethod
    def create_view(view: View) -> View:
        """Create a new saved map view"""
        view.id = str(uuid.uuid4())
        view.created_at = datetime.now()
        view.updated_at = datetime.now()
        views_db[view.id] = view
        return view
    
    @staticmethod
    def get_all_views() -> Dict[str, Any]:
        """Get all saved map views"""
        return {"views": list(views_db.values()), "count": len(views_db)}
    
    @staticmethod
    def get_view(view_id: str) -> Optional[View]:
        """Get a specific map view"""
        return views_db.get(view_id)
    
    @staticmethod
    def update_view(view_id: str, view: View) -> Optional[View]:
        """Update a map view"""
        if view_id not in views_db:
            return None
        
        view.id = view_id
        view.updated_at = datetime.now()
        views_db[view_id] = view
        return view
    
    @staticmethod
    def delete_view(view_id: str) -> bool:
        """Delete a map view"""
        if view_id not in views_db:
            return False
        
        del views_db[view_id]
        return True
    
    @staticmethod
    def validate_view(view: View) -> tuple[bool, Optional[str]]:
        """Validate that a view references valid dataset and variant"""
        if view.dataset_id not in DATASETS:
            return False, f"Map not found: {view.dataset_id}"
        
        dataset = DATASETS[view.dataset_id]
        if not any(v.id == view.variant_id for v in dataset.variants):
            return False, f"Variant not found: {view.variant_id}"
        
        return True, None
