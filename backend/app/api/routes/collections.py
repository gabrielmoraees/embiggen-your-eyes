"""
Collection API routes
"""
from fastapi import APIRouter, HTTPException

from app.models.schemas import Collection
from app.services.collection_service import CollectionService

router = APIRouter()


@router.post("/collections", response_model=Collection)
def create_collection(collection: Collection):
    """Create a new collection"""
    return CollectionService.create_collection(collection)


@router.get("/collections")
def get_collections():
    """Get all collections"""
    return CollectionService.get_all_collections()


@router.get("/collections/{collection_id}", response_model=Collection)
def get_collection(collection_id: str):
    """Get a specific collection"""
    collection = CollectionService.get_collection(collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    return collection


@router.put("/collections/{collection_id}", response_model=Collection)
def update_collection(collection_id: str, collection: Collection):
    """Update a collection"""
    updated_collection = CollectionService.update_collection(collection_id, collection)
    if not updated_collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    return updated_collection


@router.delete("/collections/{collection_id}")
def delete_collection(collection_id: str):
    """Delete a collection"""
    if not CollectionService.delete_collection(collection_id):
        raise HTTPException(status_code=404, detail="Collection not found")
    return {"message": "Collection deleted successfully"}
