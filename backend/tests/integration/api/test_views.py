"""
Integration tests for views API endpoints
"""
import pytest
from fastapi.testclient import TestClient


class TestViewsEndpoint:
    """Test view management endpoints"""
    
    def test_create_map_view(self, client: TestClient):
        """Test POST /api/views"""
        view_data = {
            "name": "Test View",
            "description": "A test view",
            "dataset_id": "viirs_snpp",
            "variant_id": "true_color",
            "center_lat": 40.7128,
            "center_lng": -74.0060,
            "zoom_level": 10
        }
        
        response = client.post("/api/views", json=view_data)
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert data["name"] == "Test View"
        assert data["dataset_id"] == "viirs_snpp"
    
    def test_list_map_views(self, client: TestClient):
        """Test GET /api/views"""
        # Create a view first
        view_data = {
            "name": "Test View",
            "dataset_id": "viirs_snpp",
            "variant_id": "true_color"
        }
        client.post("/api/views", json=view_data)
        
        # List views
        response = client.get("/api/views")
        assert response.status_code == 200
        data = response.json()
        
        assert "views" in data
        assert "count" in data
        assert len(data["views"]) > 0
    
    def test_get_specific_view(self, client: TestClient):
        """Test GET /api/views/{view_id}"""
        # Create a view first
        view_data = {
            "name": "Test View",
            "dataset_id": "viirs_snpp",
            "variant_id": "true_color"
        }
        create_response = client.post("/api/views", json=view_data)
        view_id = create_response.json()["id"]
        
        # Get the view
        response = client.get(f"/api/views/{view_id}")
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == view_id
        assert data["name"] == "Test View"
    
    def test_update_map_view(self, client: TestClient):
        """Test PUT /api/views/{view_id}"""
        # Create a view first
        view_data = {
            "name": "Original Name",
            "dataset_id": "viirs_snpp",
            "variant_id": "true_color"
        }
        create_response = client.post("/api/views", json=view_data)
        view_id = create_response.json()["id"]
        
        # Update the view
        updated_data = {
            "name": "Updated Name",
            "dataset_id": "viirs_snpp",
            "variant_id": "false_color"
        }
        response = client.put(f"/api/views/{view_id}", json=updated_data)
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "Updated Name"
        assert data["variant_id"] == "false_color"
    
    def test_delete_map_view(self, client: TestClient):
        """Test DELETE /api/views/{view_id}"""
        # Create a view first
        view_data = {
            "name": "Test View",
            "dataset_id": "viirs_snpp",
            "variant_id": "true_color"
        }
        create_response = client.post("/api/views", json=view_data)
        view_id = create_response.json()["id"]
        
        # Delete the view
        response = client.delete(f"/api/views/{view_id}")
        assert response.status_code == 200
        
        # Verify it's deleted
        get_response = client.get(f"/api/views/{view_id}")
        assert get_response.status_code == 404
