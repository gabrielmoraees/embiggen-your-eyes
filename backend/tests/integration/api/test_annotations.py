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


class TestLinkAnnotationsEndpoint:
    """Test link annotation specific endpoints"""
    
    def test_create_link_annotation(self, client: TestClient):
        """Test creating a link annotation"""
        link_data = {
            "type": "link",
            "coordinates": [{"lat": 25.0, "lng": -80.0}],
            "text": "See Mars dust storm",
            "color": "#0066CC",
            "link_target": {
                "dataset_id": "mars_viking",
                "variant_id": "colorized",
                "center_lat": -14.5,
                "center_lng": 175.4,
                "zoom_level": 6,
                "preserve_zoom": True,
                "preserve_layers": False
            }
        }
        
        response = client.post("/api/annotations", json=link_data)
        assert response.status_code == 200
        data = response.json()
        
        assert data["type"] == "link"
        assert data["link_target"] is not None
        assert data["link_target"]["dataset_id"] == "mars_viking"
        assert data["link_target"]["variant_id"] == "colorized"
    
    def test_create_link_without_target_fails(self, client: TestClient):
        """Test that creating a LINK without link_target fails"""
        link_data = {
            "type": "link",
            "coordinates": [{"lat": 25.0, "lng": -80.0}],
            "text": "Invalid link"
        }
        
        response = client.post("/api/annotations", json=link_data)
        assert response.status_code == 422  # Pydantic validation error
    
    def test_create_link_with_invalid_dataset(self, client: TestClient):
        """Test that creating a LINK with invalid dataset fails"""
        link_data = {
            "type": "link",
            "coordinates": [{"lat": 25.0, "lng": -80.0}],
            "text": "Invalid dataset link",
            "link_target": {
                "dataset_id": "nonexistent_dataset",
                "variant_id": "some_variant"
            }
        }
        
        response = client.post("/api/annotations", json=link_data)
        assert response.status_code == 400  # Service validation error
        assert "Target dataset not found" in response.json()["detail"]
    
    def test_create_link_with_invalid_variant(self, client: TestClient):
        """Test that creating a LINK with invalid variant fails"""
        link_data = {
            "type": "link",
            "coordinates": [{"lat": 25.0, "lng": -80.0}],
            "text": "Invalid variant link",
            "link_target": {
                "dataset_id": "viirs_snpp",
                "variant_id": "nonexistent_variant"
            }
        }
        
        response = client.post("/api/annotations", json=link_data)
        assert response.status_code == 400
        assert "Target variant not found" in response.json()["detail"]
    
    def test_create_point_with_link_target_fails(self, client: TestClient):
        """Test that non-LINK annotations cannot have link_target"""
        point_data = {
            "type": "point",
            "coordinates": [{"lat": 25.0, "lng": -80.0}],
            "text": "Point with link target",
            "link_target": {
                "dataset_id": "mars_viking",
                "variant_id": "colorized"
            }
        }
        
        response = client.post("/api/annotations", json=point_data)
        assert response.status_code == 422  # Pydantic validation error
    
    def test_update_link_annotation(self, client: TestClient):
        """Test updating a link annotation"""
        # Create link annotation
        link_data = {
            "type": "link",
            "coordinates": [{"lat": 25.0, "lng": -80.0}],
            "text": "Original link",
            "link_target": {
                "dataset_id": "mars_viking",
                "variant_id": "colorized"
            }
        }
        
        create_response = client.post("/api/annotations", json=link_data)
        annotation_id = create_response.json()["id"]
        
        # Update link
        updated_data = {
            "type": "link",
            "coordinates": [{"lat": 26.0, "lng": -81.0}],
            "text": "Updated link",
            "link_target": {
                "dataset_id": "viirs_snpp",
                "variant_id": "true_color",
                "zoom_level": 8
            }
        }
        
        response = client.put(f"/api/annotations/{annotation_id}", json=updated_data)
        assert response.status_code == 200
        data = response.json()
        
        assert data["text"] == "Updated link"
        assert data["link_target"]["dataset_id"] == "viirs_snpp"
        assert data["link_target"]["variant_id"] == "true_color"
    
    def test_get_link_annotation(self, client: TestClient):
        """Test retrieving a link annotation"""
        link_data = {
            "type": "link",
            "coordinates": [{"lat": 25.0, "lng": -80.0}],
            "text": "Test link",
            "link_target": {
                "dataset_id": "mars_viking",
                "variant_id": "colorized"
            }
        }
        
        create_response = client.post("/api/annotations", json=link_data)
        annotation_id = create_response.json()["id"]
        
        # Get the annotation
        response = client.get(f"/api/annotations/{annotation_id}")
        assert response.status_code == 200
        data = response.json()
        
        assert data["type"] == "link"
        assert data["link_target"] is not None
        assert data["link_target"]["dataset_id"] == "mars_viking"
    
    def test_delete_link_annotation(self, client: TestClient):
        """Test deleting a link annotation"""
        link_data = {
            "type": "link",
            "coordinates": [{"lat": 25.0, "lng": -80.0}],
            "text": "Link to delete",
            "link_target": {
                "dataset_id": "mars_viking",
                "variant_id": "colorized"
            }
        }
        
        create_response = client.post("/api/annotations", json=link_data)
        annotation_id = create_response.json()["id"]
        
        # Delete the annotation
        response = client.delete(f"/api/annotations/{annotation_id}")
        assert response.status_code == 200
        
        # Verify it's deleted
        get_response = client.get(f"/api/annotations/{annotation_id}")
        assert get_response.status_code == 404
    
    def test_link_with_minimal_target(self, client: TestClient):
        """Test link with minimal target (only dataset and variant)"""
        link_data = {
            "type": "link",
            "coordinates": [{"lat": 25.0, "lng": -80.0}],
            "text": "Minimal link",
            "link_target": {
                "dataset_id": "mars_viking",
                "variant_id": "colorized"
            }
        }
        
        response = client.post("/api/annotations", json=link_data)
        assert response.status_code == 200
        data = response.json()
        
        assert data["link_target"]["dataset_id"] == "mars_viking"
        assert data["link_target"]["center_lat"] is None
        assert data["link_target"]["zoom_level"] is None
    
    def test_filter_link_annotations_by_view(self, client: TestClient, sample_map_view_data):
        """Test filtering link annotations by view"""
        # Create a view
        view_response = client.post("/api/views", json=sample_map_view_data)
        view_id = view_response.json()["id"]
        
        # Create link annotation for this view
        link_data = {
            "map_view_id": view_id,
            "type": "link",
            "coordinates": [{"lat": 25.0, "lng": -80.0}],
            "text": "View link",
            "link_target": {
                "dataset_id": "mars_viking",
                "variant_id": "colorized"
            }
        }
        
        client.post("/api/annotations", json=link_data)
        
        # Get annotations for this view
        response = client.get(f"/api/annotations?map_view_id={view_id}")
        assert response.status_code == 200
        data = response.json()
        
        annotations = data["annotations"]
        assert len(annotations) > 0
        assert annotations[0]["type"] == "link"
        assert annotations[0]["map_view_id"] == view_id
