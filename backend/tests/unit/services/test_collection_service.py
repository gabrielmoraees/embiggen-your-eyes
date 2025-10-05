"""
Unit tests for collection service
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.services.collection_service import CollectionService
from app.models.schemas import Collection
from app.data.storage import collections_db


class TestCollectionService:
    """Test collection service business logic"""
    
    def setup_method(self):
        """Clear collections before each test"""
        collections_db.clear()
    
    def test_create_collection(self):
        """Test creating a new collection"""
        collection = Collection(
            name="My Collection",
            description="Test collection",
            view_ids=["view1", "view2"]
        )
        
        created = CollectionService.create_collection(collection)
        
        assert created.id is not None
        assert created.name == "My Collection"
        assert len(created.view_ids) == 2
        assert created.created_at is not None
        assert created.updated_at is not None
        assert created.id in collections_db
    
    def test_create_empty_collection(self):
        """Test creating an empty collection"""
        collection = Collection(name="Empty Collection")
        
        created = CollectionService.create_collection(collection)
        
        assert created.id is not None
        assert len(created.view_ids) == 0
    
    def test_get_all_collections_empty(self):
        """Test getting all collections when none exist"""
        result = CollectionService.get_all_collections()
        
        assert "collections" in result
        assert len(result["collections"]) == 0
    
    def test_get_all_collections_with_data(self):
        """Test getting all collections when some exist"""
        coll1 = Collection(name="Collection 1")
        coll2 = Collection(name="Collection 2")
        
        CollectionService.create_collection(coll1)
        CollectionService.create_collection(coll2)
        
        result = CollectionService.get_all_collections()
        
        assert len(result["collections"]) == 2
    
    def test_get_existing_collection(self):
        """Test getting a specific collection"""
        collection = Collection(
            name="Test Collection",
            view_ids=["view1"]
        )
        created = CollectionService.create_collection(collection)
        
        retrieved = CollectionService.get_collection(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == "Test Collection"
    
    def test_get_nonexistent_collection(self):
        """Test getting a collection that doesn't exist"""
        collection = CollectionService.get_collection("nonexistent_id")
        
        assert collection is None
    
    def test_update_collection(self):
        """Test updating a collection"""
        collection = Collection(
            name="Original Name",
            view_ids=["view1"]
        )
        created = CollectionService.create_collection(collection)
        
        # Update the collection
        updated = Collection(
            name="Updated Name",
            view_ids=["view1", "view2", "view3"]
        )
        
        result = CollectionService.update_collection(created.id, updated)
        
        assert result is not None
        assert result.id == created.id
        assert result.name == "Updated Name"
        assert len(result.view_ids) == 3
        assert result.updated_at > created.updated_at
    
    def test_update_nonexistent_collection(self):
        """Test updating a collection that doesn't exist"""
        collection = Collection(name="Test")
        result = CollectionService.update_collection("nonexistent_id", collection)
        
        assert result is None
    
    def test_delete_collection(self):
        """Test deleting a collection"""
        collection = Collection(name="Test Collection")
        created = CollectionService.create_collection(collection)
        
        success = CollectionService.delete_collection(created.id)
        
        assert success is True
        assert created.id not in collections_db
        assert CollectionService.get_collection(created.id) is None
    
    def test_delete_nonexistent_collection(self):
        """Test deleting a collection that doesn't exist"""
        success = CollectionService.delete_collection("nonexistent_id")
        
        assert success is False
