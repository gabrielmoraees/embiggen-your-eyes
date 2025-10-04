"""
Integration tests for API endpoints
Tests the API endpoints with the test client
"""
import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self, client: TestClient):
        """Test GET / returns healthy status"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data


class TestLayersEndpoint:
    """Test layers discovery endpoints"""
    
    def test_list_all_layers(self, client: TestClient):
        """Test GET /api/layers returns all layers"""
        response = client.get("/api/layers")
        assert response.status_code == 200
        data = response.json()
        assert "layers" in data
        assert "total" in data
        assert data["total"] > 0
        assert len(data["layers"]) == data["total"]
    
    def test_filter_layers_by_earth(self, client: TestClient):
        """Test filtering layers by Earth"""
        response = client.get("/api/layers?celestial_body=earth")
        assert response.status_code == 200
        data = response.json()
        assert data["celestial_body"] == "earth"
        # All returned layers should be Earth
        for layer in data["layers"]:
            assert layer["celestial_body"] == "earth"
    
    def test_filter_layers_by_mars(self, client: TestClient):
        """Test filtering layers by Mars"""
        response = client.get("/api/layers?celestial_body=mars")
        assert response.status_code == 200
        data = response.json()
        for layer in data["layers"]:
            assert layer["celestial_body"] == "mars"
    


class TestImageSearchEndpoint:
    """Test image search endpoint"""
    
    def test_search_earth_images(self, client: TestClient, sample_earth_search_query):
        """Test searching for Earth images"""
        response = client.post("/api/search/images", json=sample_earth_search_query)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Verify first result has required fields
        image = data[0]
        assert "id" in image
        assert "tile_url" in image
        assert "thumbnail_url" in image
        assert "max_zoom" in image
        assert "{z}" in image["tile_url"]
        assert "{x}" in image["tile_url"]
        assert "{y}" in image["tile_url"]
    
    def test_search_mars_images(self, client: TestClient, sample_mars_search_query):
        """Test searching for Mars images"""
        response = client.post("/api/search/images", json=sample_mars_search_query)
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        
        image = data[0]
        assert "mars" in image["id"]
        assert "tile_url" in image
    
    
    def test_search_with_limit(self, client: TestClient):
        """Test search respects limit parameter"""
        query = {
            "celestial_body": "earth",
            "layer": "VIIRS_SNPP_CorrectedReflectance_TrueColor",
            "limit": 3
        }
        response = client.post("/api/search/images", json=query)
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 3


class TestAnnotationsEndpoint:
    """Test annotations CRUD endpoints"""
    
    def test_create_annotation(self, client: TestClient, sample_annotation_data):
        """Test POST /api/annotations creates annotation"""
        response = client.post("/api/annotations", json=sample_annotation_data)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["image_id"] == sample_annotation_data["image_id"]
        assert data["type"] == sample_annotation_data["type"]
        assert "created_at" in data
    
    def test_get_annotations_for_image(self, client: TestClient, sample_annotation_data):
        """Test GET /api/annotations/image/{image_id}"""
        # Create annotation first
        create_response = client.post("/api/annotations", json=sample_annotation_data)
        assert create_response.status_code == 200
        
        # Get annotations for the image
        image_id = sample_annotation_data["image_id"]
        response = client.get(f"/api/annotations/image/{image_id}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert data[0]["image_id"] == image_id
    
    def test_update_annotation(self, client: TestClient, sample_annotation_data):
        """Test PUT /api/annotations/{annotation_id}"""
        # Create annotation
        create_response = client.post("/api/annotations", json=sample_annotation_data)
        annotation_id = create_response.json()["id"]
        
        # Update annotation
        updated_data = sample_annotation_data.copy()
        updated_data["text"] = "Updated text"
        response = client.put(f"/api/annotations/{annotation_id}", json=updated_data)
        assert response.status_code == 200
        data = response.json()
        assert data["text"] == "Updated text"
        assert "updated_at" in data
    
    def test_delete_annotation(self, client: TestClient, sample_annotation_data):
        """Test DELETE /api/annotations/{annotation_id}"""
        # Create annotation
        create_response = client.post("/api/annotations", json=sample_annotation_data)
        annotation_id = create_response.json()["id"]
        
        # Delete annotation
        response = client.delete(f"/api/annotations/{annotation_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "deleted"
        
        # Verify it's deleted
        get_response = client.get(f"/api/annotations/image/{sample_annotation_data['image_id']}")
        annotations = get_response.json()
        assert not any(ann["id"] == annotation_id for ann in annotations)


class TestLinksEndpoint:
    """Test image links endpoints"""
    
    def test_create_link(self, client: TestClient, sample_link_data):
        """Test POST /api/links creates link"""
        response = client.post("/api/links", json=sample_link_data)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["source_image_id"] == sample_link_data["source_image_id"]
        assert data["target_image_id"] == sample_link_data["target_image_id"]
    
    def test_get_links_for_image(self, client: TestClient, sample_link_data):
        """Test GET /api/links/image/{image_id}"""
        # Create link
        client.post("/api/links", json=sample_link_data)
        
        # Get links for source image
        response = client.get(f"/api/links/image/{sample_link_data['source_image_id']}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_delete_link(self, client: TestClient, sample_link_data):
        """Test DELETE /api/links/{link_id}"""
        # Create link
        create_response = client.post("/api/links", json=sample_link_data)
        link_id = create_response.json()["id"]
        
        # Delete link
        response = client.delete(f"/api/links/{link_id}")
        assert response.status_code == 200
        assert response.json()["status"] == "deleted"


class TestCollectionsEndpoint:
    """Test collections endpoints"""
    
    def test_create_collection(self, client: TestClient, sample_collection_data):
        """Test POST /api/collections creates collection"""
        response = client.post("/api/collections", json=sample_collection_data)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["name"] == sample_collection_data["name"]
        assert len(data["image_ids"]) == len(sample_collection_data["image_ids"])
    
    def test_get_all_collections(self, client: TestClient, sample_collection_data):
        """Test GET /api/collections returns all collections"""
        # Create a collection
        client.post("/api/collections", json=sample_collection_data)
        
        # Get all collections
        response = client.get("/api/collections")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_get_collection_by_id(self, client: TestClient, sample_collection_data):
        """Test GET /api/collections/{collection_id}"""
        # Create collection
        create_response = client.post("/api/collections", json=sample_collection_data)
        collection_id = create_response.json()["id"]
        
        # Get collection by ID
        response = client.get(f"/api/collections/{collection_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == collection_id
        assert data["name"] == sample_collection_data["name"]
    
    def test_add_images_to_collection(self, client: TestClient, sample_collection_data):
        """Test PUT /api/collections/{collection_id}/images"""
        # Create collection
        create_response = client.post("/api/collections", json=sample_collection_data)
        collection_id = create_response.json()["id"]
        
        # Add more images
        new_images = ["image_004", "image_005"]
        response = client.put(
            f"/api/collections/{collection_id}/images",
            json=new_images
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["image_ids"]) > len(sample_collection_data["image_ids"])
    
    def test_delete_collection(self, client: TestClient, sample_collection_data):
        """Test DELETE /api/collections/{collection_id}"""
        # Create collection
        create_response = client.post("/api/collections", json=sample_collection_data)
        collection_id = create_response.json()["id"]
        
        # Delete collection
        response = client.delete(f"/api/collections/{collection_id}")
        assert response.status_code == 200
        assert response.json()["status"] == "deleted"


class TestCustomImageEndpoint:
    """Test custom image upload endpoint"""
    
    def test_upload_custom_image(self, client: TestClient, sample_custom_image_data):
        """Test POST /api/custom-image"""
        response = client.post("/api/custom-image", json=sample_custom_image_data)
        assert response.status_code == 200
        data = response.json()
        assert "layer_id" in data
        assert data["celestial_body"] == "custom"
        assert "status" in data or "message" in data
    
    def test_duplicate_custom_image(self, client: TestClient, sample_custom_image_data):
        """Test uploading the same image twice returns existing"""
        # Upload first time
        response1 = client.post("/api/custom-image", json=sample_custom_image_data)
        layer_id_1 = response1.json()["layer_id"]
        
        # Upload second time (same URL)
        response2 = client.post("/api/custom-image", json=sample_custom_image_data)
        layer_id_2 = response2.json()["layer_id"]
        
        # Should return same layer ID
        assert layer_id_1 == layer_id_2
