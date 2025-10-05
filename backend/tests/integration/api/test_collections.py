"""
Integration tests for collections API endpoints
"""
import pytest
from fastapi.testclient import TestClient


class TestCollectionsEndpoint:
    """Test collection management endpoints"""
    
    def test_create_collection(self, client: TestClient, sample_collection_data):
        """Test POST /api/collections"""
        response = client.post("/api/collections", json=sample_collection_data)
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert data["name"] == "Test Collection"
    
    def test_get_collections(self, client: TestClient, sample_collection_data):
        """Test GET /api/collections"""
        # Create a collection first
        client.post("/api/collections", json=sample_collection_data)
        
        response = client.get("/api/collections")
        assert response.status_code == 200
        data = response.json()
        
        assert "collections" in data
        assert len(data["collections"]) > 0
    
    def test_update_collection(self, client: TestClient, sample_collection_data):
        """Test PUT /api/collections/{collection_id}"""
        # Create collection
        create_response = client.post("/api/collections", json=sample_collection_data)
        collection_id = create_response.json()["id"]
        
        # Update collection
        updated_data = {**sample_collection_data, "name": "Updated Collection"}
        response = client.put(f"/api/collections/{collection_id}", json=updated_data)
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "Updated Collection"
    
    def test_delete_collection(self, client: TestClient, sample_collection_data):
        """Test DELETE /api/collections/{collection_id}"""
        # Create collection
        create_response = client.post("/api/collections", json=sample_collection_data)
        collection_id = create_response.json()["id"]
        
        # Delete collection
        response = client.delete(f"/api/collections/{collection_id}")
        assert response.status_code == 200
        
        # Verify it's deleted
        get_response = client.get(f"/api/collections/{collection_id}")
        assert get_response.status_code == 404
