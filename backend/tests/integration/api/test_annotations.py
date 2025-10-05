"""
Integration tests for annotations API endpoints
"""
import pytest
from fastapi.testclient import TestClient


class TestAnnotationsEndpoint:
    """Test annotation management endpoints"""
    
    def test_create_annotation(self, client: TestClient, sample_annotation_data):
        """Test POST /api/annotations"""
        response = client.post("/api/annotations", json=sample_annotation_data)
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert data["type"] == "point"
    
    def test_get_annotations(self, client: TestClient, sample_annotation_data):
        """Test GET /api/annotations"""
        # Create an annotation first
        client.post("/api/annotations", json=sample_annotation_data)
        
        response = client.get("/api/annotations")
        assert response.status_code == 200
        data = response.json()
        
        assert "annotations" in data
        assert len(data["annotations"]) > 0
    
    def test_filter_annotations_by_view(self, client: TestClient, sample_map_view_data, sample_annotation_data):
        """Test filtering annotations by map view"""
        # Create a view
        view_response = client.post("/api/views", json=sample_map_view_data)
        view_id = view_response.json()["id"]
        
        # Create annotation linked to view
        annotation_data = {**sample_annotation_data, "map_view_id": view_id}
        client.post("/api/annotations", json=annotation_data)
        
        # Get annotations for this view
        response = client.get(f"/api/annotations?map_view_id={view_id}")
        assert response.status_code == 200
        data = response.json()
        
        annotations = data["annotations"]
        assert len(annotations) > 0
        assert all(a["map_view_id"] == view_id for a in annotations)
    
    def test_update_annotation(self, client: TestClient, sample_annotation_data):
        """Test PUT /api/annotations/{annotation_id}"""
        # Create annotation
        create_response = client.post("/api/annotations", json=sample_annotation_data)
        annotation_id = create_response.json()["id"]
        
        # Update annotation
        updated_data = {**sample_annotation_data, "text": "Updated text"}
        response = client.put(f"/api/annotations/{annotation_id}", json=updated_data)
        assert response.status_code == 200
        data = response.json()
        
        assert data["text"] == "Updated text"
    
    def test_delete_annotation(self, client: TestClient, sample_annotation_data):
        """Test DELETE /api/annotations/{annotation_id}"""
        # Create annotation
        create_response = client.post("/api/annotations", json=sample_annotation_data)
        annotation_id = create_response.json()["id"]
        
        # Delete annotation
        response = client.delete(f"/api/annotations/{annotation_id}")
        assert response.status_code == 200
        
        # Verify it's deleted
        get_response = client.get(f"/api/annotations/{annotation_id}")
        assert get_response.status_code == 404
