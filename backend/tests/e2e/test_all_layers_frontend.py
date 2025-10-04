"""
E2E Tests: Verify all map layers work from frontend perspective

This test suite simulates a frontend user workflow:
1. Fetching available layers
2. Searching for images with each layer
3. Verifying tile URLs are accessible
4. Verifying thumbnail URLs are accessible

Tests all celestial bodies: Earth, Mars, Moon, Mercury
"""
import pytest
from fastapi.testclient import TestClient
import requests
from datetime import date


@pytest.mark.e2e
class TestAllLayersFrontendAccessibility:
    """Test that all layers are accessible and working from frontend perspective"""
    
    def test_get_all_available_layers(self, client: TestClient):
        """E2E: Frontend fetches all available layers"""
        response = client.get("/api/layers")
        assert response.status_code == 200
        
        data = response.json()
        assert "layers" in data
        assert len(data["layers"]) > 0
        
        # Verify each layer has required fields
        for layer in data["layers"]:
            assert "id" in layer
            assert "value" in layer
            assert "display_name" in layer
            assert "celestial_body" in layer
            assert "satellite" in layer
            assert "type" in layer
            assert "description" in layer
        
        print(f"\n✓ Found {len(data['layers'])} available layers")
    
    def test_earth_layers_complete_workflow(self, client: TestClient):
        """E2E: Test complete workflow for all Earth layers"""
        # Get Earth layers
        response = client.get("/api/layers?celestial_body=earth")
        assert response.status_code == 200
        
        earth_layers = response.json()["layers"]
        assert len(earth_layers) == 4, "Expected 4 Earth layers"
        
        today = date.today().isoformat()
        
        for layer in earth_layers:
            layer_value = layer["value"]
            print(f"\n  Testing Earth layer: {layer['display_name']}")
            
            # 1. Search for images with this layer
            search_response = client.post("/api/search/images", json={
                "celestial_body": "earth",
                "layer": layer_value,
                "date_start": today,
                "date_end": today,
                "limit": 1
            })
            assert search_response.status_code == 200
            
            images = search_response.json()
            assert len(images) > 0, f"No images found for {layer_value}"
            
            image = images[0]
            
            # 2. Verify tile URL is accessible
            tile_url = image["tile_url"].replace("{z}", "0").replace("{y}", "0").replace("{x}", "0")
            tile_response = requests.head(tile_url, timeout=10)
            assert tile_response.status_code == 200, f"Tile URL failed for {layer_value}"
            assert "image" in tile_response.headers.get("content-type", "").lower()
            
            # 3. Verify thumbnail URL is accessible
            thumb_response = requests.head(image["thumbnail_url"], timeout=10)
            assert thumb_response.status_code == 200, f"Thumbnail failed for {layer_value}"
            assert "image" in thumb_response.headers.get("content-type", "").lower()
            
            print(f"    ✓ {layer['display_name']} - All checks passed")
    
    def test_mars_layers_complete_workflow(self, client: TestClient):
        """E2E: Test complete workflow for all Mars layers"""
        # Get Mars layers
        response = client.get("/api/layers?celestial_body=mars")
        assert response.status_code == 200
        
        mars_layers = response.json()["layers"]
        assert len(mars_layers) == 2, "Expected 2 Mars layers"
        
        for layer in mars_layers:
            layer_value = layer["value"]
            print(f"\n  Testing Mars layer: {layer['display_name']}")
            
            # 1. Search for images with this layer
            search_response = client.post("/api/search/images", json={
                "celestial_body": "mars",
                "layer": layer_value,
                "limit": 1
            })
            assert search_response.status_code == 200
            
            images = search_response.json()
            assert len(images) > 0, f"No images found for {layer_value}"
            
            image = images[0]
            
            # 2. Verify tile URL is accessible
            tile_url = image["tile_url"].replace("{z}", "0").replace("{y}", "0").replace("{x}", "0")
            tile_response = requests.head(tile_url, timeout=10)
            assert tile_response.status_code == 200, f"Tile URL failed for {layer_value}"
            assert "image" in tile_response.headers.get("content-type", "").lower()
            
            # 3. Verify thumbnail URL is accessible
            thumb_response = requests.head(image["thumbnail_url"], timeout=10)
            assert thumb_response.status_code == 200, f"Thumbnail failed for {layer_value}"
            assert "image" in thumb_response.headers.get("content-type", "").lower()
            
            print(f"    ✓ {layer['display_name']} - All checks passed")
    
    def test_moon_layers_complete_workflow(self, client: TestClient):
        """E2E: Test complete workflow for all Moon layers"""
        # Get Moon layers
        response = client.get("/api/layers?celestial_body=moon")
        assert response.status_code == 200
        
        moon_layers = response.json()["layers"]
        assert len(moon_layers) == 2, "Expected 2 Moon layers"
        
        for layer in moon_layers:
            layer_value = layer["value"]
            print(f"\n  Testing Moon layer: {layer['display_name']}")
            
            # 1. Search for images with this layer
            search_response = client.post("/api/search/images", json={
                "celestial_body": "moon",
                "layer": layer_value,
                "limit": 1
            })
            assert search_response.status_code == 200
            
            images = search_response.json()
            assert len(images) > 0, f"No images found for {layer_value}"
            
            image = images[0]
            
            # 2. Verify tile URL is accessible
            tile_url = image["tile_url"].replace("{z}", "0").replace("{y}", "0").replace("{x}", "0")
            tile_response = requests.head(tile_url, timeout=10)
            assert tile_response.status_code == 200, f"Tile URL failed for {layer_value}"
            assert "image" in tile_response.headers.get("content-type", "").lower()
            
            # 3. Verify thumbnail URL is accessible
            thumb_response = requests.head(image["thumbnail_url"], timeout=10)
            assert thumb_response.status_code == 200, f"Thumbnail failed for {layer_value}"
            assert "image" in thumb_response.headers.get("content-type", "").lower()
            
            print(f"    ✓ {layer['display_name']} - All checks passed")
    
    def test_mercury_layers_complete_workflow(self, client: TestClient):
        """E2E: Test complete workflow for all Mercury layers"""
        # Get Mercury layers
        response = client.get("/api/layers?celestial_body=mercury")
        assert response.status_code == 200
        
        mercury_layers = response.json()["layers"]
        assert len(mercury_layers) == 1, "Expected 1 Mercury layer"
        
        for layer in mercury_layers:
            layer_value = layer["value"]
            print(f"\n  Testing Mercury layer: {layer['display_name']}")
            
            # 1. Search for images with this layer
            search_response = client.post("/api/search/images", json={
                "celestial_body": "mercury",
                "layer": layer_value,
                "limit": 1
            })
            assert search_response.status_code == 200
            
            images = search_response.json()
            assert len(images) > 0, f"No images found for {layer_value}"
            
            image = images[0]
            
            # 2. Verify tile URL is accessible
            tile_url = image["tile_url"].replace("{z}", "0").replace("{y}", "0").replace("{x}", "0")
            tile_response = requests.head(tile_url, timeout=10)
            assert tile_response.status_code == 200, f"Tile URL failed for {layer_value}"
            assert "image" in tile_response.headers.get("content-type", "").lower()
            
            # 3. Verify thumbnail URL is accessible
            thumb_response = requests.head(image["thumbnail_url"], timeout=10)
            assert thumb_response.status_code == 200, f"Thumbnail failed for {layer_value}"
            assert "image" in thumb_response.headers.get("content-type", "").lower()
            
            print(f"    ✓ {layer['display_name']} - All checks passed")
    
    def test_all_layers_summary(self, client: TestClient):
        """E2E: Generate summary of all working layers"""
        response = client.get("/api/layers")
        assert response.status_code == 200
        
        layers = response.json()["layers"]
        
        # Group by celestial body
        by_body = {}
        for layer in layers:
            body = layer["celestial_body"]
            if body not in by_body:
                by_body[body] = []
            by_body[body].append(layer)
        
        print("\n" + "=" * 60)
        print("FRONTEND-ACCESSIBLE LAYERS SUMMARY")
        print("=" * 60)
        
        total = 0
        for body, body_layers in sorted(by_body.items()):
            print(f"\n{body.upper()} ({len(body_layers)} layers):")
            for layer in body_layers:
                print(f"  ✓ {layer['display_name']}")
                print(f"    Source: {layer['satellite']}")
                print(f"    Type: {layer['type']}")
            total += len(body_layers)
        
        print(f"\n🎉 TOTAL: {total} working layers accessible from frontend")
        print("=" * 60)
        
        # Verify expected counts
        assert by_body.get("earth", []) and len(by_body["earth"]) == 4
        assert by_body.get("mars", []) and len(by_body["mars"]) == 2
        assert by_body.get("moon", []) and len(by_body["moon"]) == 2
        assert by_body.get("mercury", []) and len(by_body["mercury"]) == 1
        assert total == 9


@pytest.mark.e2e
class TestLayerTileAccessibility:
    """Test that tile URLs for all layers return valid images"""
    
    def test_all_layer_tiles_return_images(self, client: TestClient):
        """E2E: Verify all layer tiles return valid image content"""
        response = client.get("/api/layers")
        layers = response.json()["layers"]
        
        print("\n" + "=" * 60)
        print("TESTING TILE ACCESSIBILITY FOR ALL LAYERS")
        print("=" * 60)
        
        failed_layers = []
        
        for layer in layers:
            layer_value = layer["value"]
            celestial_body = layer["celestial_body"]
            
            # Search for an image with this layer
            search_data = {
                "celestial_body": celestial_body,
                "layer": layer_value,
                "limit": 1
            }
            
            # Add date for Earth layers
            if celestial_body == "earth":
                today = date.today().isoformat()
                search_data["date_start"] = today
                search_data["date_end"] = today
            
            search_response = client.post("/api/search/images", json=search_data)
            assert search_response.status_code == 200
            
            images = search_response.json()
            if len(images) == 0:
                failed_layers.append(f"{layer['display_name']} - No images found")
                continue
            
            image = images[0]
            
            # Test tile URL at zoom 0
            tile_url = image["tile_url"].replace("{z}", "0").replace("{y}", "0").replace("{x}", "0")
            
            try:
                tile_response = requests.head(tile_url, timeout=10)
                content_type = tile_response.headers.get("content-type", "")
                
                if tile_response.status_code != 200:
                    failed_layers.append(f"{layer['display_name']} - HTTP {tile_response.status_code}")
                elif "image" not in content_type.lower():
                    failed_layers.append(f"{layer['display_name']} - Invalid content-type: {content_type}")
                else:
                    print(f"  ✓ {layer['display_name']} - {content_type}")
            except Exception as e:
                failed_layers.append(f"{layer['display_name']} - {str(e)}")
        
        print("=" * 60)
        
        if failed_layers:
            print("\n❌ FAILED LAYERS:")
            for failure in failed_layers:
                print(f"  - {failure}")
            pytest.fail(f"{len(failed_layers)} layers failed accessibility test")
        else:
            print(f"\n✅ All {len(layers)} layers passed tile accessibility test")
