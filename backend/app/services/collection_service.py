"""
Collection service for managing collections of map views
"""
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
from app.models.schemas import Collection
from app.data.storage import collections_db


class CollectionService:
    """Service for collection operations"""
    
    @staticmethod
    def create_collection(collection: Collection) -> Collection:
        """Create a new collection"""
        collection.id = str(uuid.uuid4())
        collection.created_at = datetime.now()
        collection.updated_at = datetime.now()
        collections_db[collection.id] = collection
        return collection
    
    @staticmethod
    def get_all_collections() -> Dict[str, Any]:
        """Get all collections"""
        return {"collections": list(collections_db.values())}
    
    @staticmethod
    def get_collection(collection_id: str) -> Optional[Collection]:
        """Get a specific collection"""
        return collections_db.get(collection_id)
    
    @staticmethod
    def update_collection(collection_id: str, collection: Collection) -> Optional[Collection]:
        """Update a collection"""
        if collection_id not in collections_db:
            return None
        
        collection.id = collection_id
        collection.updated_at = datetime.now()
        collections_db[collection_id] = collection
        return collection
    
    @staticmethod
    def delete_collection(collection_id: str) -> bool:
        """Delete a collection"""
        if collection_id not in collections_db:
            return False
        
        del collections_db[collection_id]
        return True
