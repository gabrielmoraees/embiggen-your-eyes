#!/usr/bin/env python3
"""
Complete System Test for Embiggen Your Eyes API
Tests all endpoints and functionality using urllib (no external dependencies)
"""
import urllib.request
import urllib.error
import json
import time

BASE_URL = "http://localhost:8000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def make_request(url, method="GET", data=None):
    """Make HTTP request using urllib"""
    try:
        if data:
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method=method
            )
        else:
            req = urllib.request.Request(url, method=method)
        
        with urllib.request.urlopen(req) as response:
            body = response.read().decode('utf-8')
            return response.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        try:
            return e.code, json.loads(body) if body else {}
        except:
            return e.code, {"error": body}
    except Exception as e:
        return None, {"error": str(e)}

def print_test(name):
    print(f"\n{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}TEST: {name}{Colors.END}")
    print(f"{Colors.BLUE}{'='*70}{Colors.END}")

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.YELLOW}ℹ {msg}{Colors.END}")

def test_health_check():
    """Test 1: Health check endpoint"""
    print_test("Health Check")
    
    try:
        status, data = make_request(f"{BASE_URL}/")
        assert status == 200, f"Expected 200, got {status}"
        assert data["status"] == "healthy", "Service not healthy"
        
        print_success("Health check passed")
        print_info(f"Service: {data['service']}")
        print_info(f"Version: {data['version']}")
        return True
    except Exception as e:
        print_error(f"Health check failed: {e}")
        return False

def test_list_all_layers():
    """Test 2: List all available layers"""
    print_test("List All Layers")
    
    try:
        status, data = make_request(f"{BASE_URL}/api/layers")
        assert status == 200, f"Expected 200, got {status}"
        assert "layers" in data, "No layers in response"
        assert data["total"] >= 10, f"Expected at least 10 layers, got {data['total']}"
        
        print_success(f"Found {data['total']} layers")
        
        # Count by celestial body
        by_body = {}
        for layer in data["layers"]:
            body = layer["celestial_body"]
            by_body[body] = by_body.get(body, 0) + 1
        
        for body, count in by_body.items():
            print_info(f"  {body}: {count} layers")
        
        return True
    except Exception as e:
        print_error(f"List layers failed: {e}")
        return False

def test_filter_layers_by_body():
    """Test 3: Filter layers by celestial body"""
    print_test("Filter Layers by Celestial Body")
    
    bodies = ["earth", "mars", "moon", "mercury", "deep_space"]
    all_passed = True
    
    for body in bodies:
        try:
            status, data = make_request(f"{BASE_URL}/api/layers?celestial_body={body}")
            assert status == 200, f"Expected 200, got {status}"
            
            count = data["total"]
            
            # Verify all returned layers match the filter
            for layer in data["layers"]:
                assert layer["celestial_body"] == body, f"Wrong body: {layer['celestial_body']}"
            
            print_success(f"{body}: {count} layers")
        except Exception as e:
            print_error(f"{body} filter failed: {e}")
            all_passed = False
    
    return all_passed

def test_search_earth_images():
    """Test 4: Search Earth imagery"""
    print_test("Search Earth Images")
    
    try:
        payload = {
            "celestial_body": "earth",
            "layer": "VIIRS_SNPP_CorrectedReflectance_TrueColor",
            "start_date": "2024-08-15",
            "end_date": "2024-08-15",
            "projection": "epsg3857",
            "limit": 1
        }
        
        status, data = make_request(f"{BASE_URL}/api/search/images", "POST", payload)
        assert status == 200, f"Expected 200, got {status}"
        assert len(data) > 0, "No results returned"
        
        result = data[0]
        assert "tile_url" in result, "No tile_url in result"
        assert "{z}" in result["tile_url"], "tile_url not a template"
        assert result["max_zoom"] == 9, f"Expected max_zoom 9, got {result['max_zoom']}"
        
        print_success("Earth search successful")
        print_info(f"Image ID: {result['id']}")
        print_info(f"Max Zoom: {result['max_zoom']}")
        
        return True
    except Exception as e:
        print_error(f"Earth search failed: {e}")
        return False

def test_search_mars_images():
    """Test 5: Search Mars imagery"""
    print_test("Search Mars Images")
    
    try:
        payload = {
            "celestial_body": "mars",
            "layer": "opm_mars_basemap"
        }
        
        status, data = make_request(f"{BASE_URL}/api/search/images", "POST", payload)
        assert status == 200, f"Expected 200, got {status}"
        assert len(data) > 0, "No results returned"
        
        result = data[0]
        assert "tile_url" in result, "No tile_url in result"
        assert "opm-mars" in result["tile_url"], "Not Mars OPM URL"
        
        print_success("Mars search successful")
        print_info(f"Image ID: {result['id']}")
        
        return True
    except Exception as e:
        print_error(f"Mars search failed: {e}")
        return False

def test_search_deep_space():
    """Test 6: Search Deep Space gigapixel"""
    print_test("Search Deep Space Gigapixel")
    
    try:
        payload = {
            "celestial_body": "deep_space",
            "layer": "andromeda_gigapixel"
        }
        
        status, data = make_request(f"{BASE_URL}/api/search/images", "POST", payload)
        assert status == 200, f"Expected 200, got {status}"
        assert len(data) > 0, "No results returned"
        
        result = data[0]
        assert "tile_url" in result, "No tile_url in result"
        assert "gigapan.com" in result["tile_url"], "Not Gigapan URL"
        assert result["max_zoom"] == 12, f"Expected max_zoom 12, got {result['max_zoom']}"
        
        print_success("Deep Space search successful")
        print_info(f"Image ID: {result['id']}")
        print_info(f"Max Zoom: {result['max_zoom']} (gigapixel!)")
        
        return True
    except Exception as e:
        print_error(f"Deep Space search failed: {e}")
        return False

def test_custom_image_upload():
    """Test 7: Custom image upload"""
    print_test("Custom Image Upload")
    
    try:
        payload = {
            "name": "Test Complete System",
            "image_url": "https://images-assets.nasa.gov/image/PIA16695/PIA16695~orig.jpg",
            "max_zoom": 8
        }
        
        status, data = make_request(f"{BASE_URL}/api/custom-image", "POST", payload)
        assert status == 200, f"Expected 200, got {status}"
        assert "layer_id" in data, "No layer_id in response"
        assert data["celestial_body"] == "custom", "Wrong celestial body"
        
        print_success("Custom upload successful")
        print_info(f"Layer ID: {data['layer_id']}")
        print_info(f"Status: {data.get('status', data.get('message', 'unknown'))}")
        
        return True
    except Exception as e:
        print_error(f"Custom upload failed: {e}")
        return False

def test_annotations():
    """Test 8: Annotation system"""
    print_test("Annotations")
    
    try:
        # Create annotation
        payload = {
            "image_id": "test_complete_system",
            "type": "point",
            "coordinates": [{"lat": 40.7, "lng": -74.0}],
            "title": "Test Annotation",
            "description": "Complete system test"
        }
        
        status, data = make_request(f"{BASE_URL}/api/annotations", "POST", payload)
        assert status == 200, f"Expected 200, got {status}"
        assert "id" in data, "No annotation ID returned"
        
        annotation_id = data["id"]
        print_success(f"Annotation created: {annotation_id}")
        
        # Retrieve annotations
        status, data = make_request(f"{BASE_URL}/api/annotations/image/test_complete_system")
        assert status == 200, f"Expected 200, got {status}"
        assert len(data) > 0, "No annotations retrieved"
        
        print_success(f"Retrieved {len(data)} annotation(s)")
        
        return True
    except Exception as e:
        print_error(f"Annotations failed: {e}")
        return False

def test_image_links():
    """Test 9: Image linking system"""
    print_test("Image Links")
    
    try:
        # Create link
        payload = {
            "source_image_id": "test_img_1",
            "target_image_id": "test_img_2",
            "relationship_type": "comparison",
            "description": "Test link"
        }
        
        status, data = make_request(f"{BASE_URL}/api/links", "POST", payload)
        assert status == 200, f"Expected 200, got {status}"
        assert "id" in data, "No link ID returned"
        
        link_id = data["id"]
        print_success(f"Link created: {link_id}")
        
        # Retrieve links
        status, data = make_request(f"{BASE_URL}/api/links/image/test_img_1")
        assert status == 200, f"Expected 200, got {status}"
        assert len(data) > 0, "No links retrieved"
        
        print_success(f"Retrieved {len(data)} link(s)")
        
        return True
    except Exception as e:
        print_error(f"Image links failed: {e}")
        return False

def test_collections():
    """Test 10: Collections system"""
    print_test("Collections")
    
    try:
        # Create collection
        payload = {
            "name": "Test Collection",
            "description": "Complete system test collection",
            "image_ids": ["test_img_1", "test_img_2"]
        }
        
        status, data = make_request(f"{BASE_URL}/api/collections", "POST", payload)
        assert status == 200, f"Expected 200, got {status}"
        assert "id" in data, "No collection ID returned"
        
        collection_id = data["id"]
        print_success(f"Collection created: {collection_id}")
        
        # List collections
        status, data = make_request(f"{BASE_URL}/api/collections")
        assert status == 200, f"Expected 200, got {status}"
        assert len(data) > 0, "No collections retrieved"
        
        print_success(f"Retrieved {len(data)} collection(s)")
        
        return True
    except Exception as e:
        print_error(f"Collections failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print(f"\n{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}COMPLETE SYSTEM TEST SUITE{Colors.END}")
    print(f"{Colors.BLUE}{'='*70}{Colors.END}")
    
    tests = [
        ("Health Check", test_health_check),
        ("List All Layers", test_list_all_layers),
        ("Filter Layers by Body", test_filter_layers_by_body),
        ("Search Earth Images", test_search_earth_images),
        ("Search Mars Images", test_search_mars_images),
        ("Search Deep Space", test_search_deep_space),
        ("Custom Image Upload", test_custom_image_upload),
        ("Annotations", test_annotations),
        ("Image Links", test_image_links),
        ("Collections", test_collections),
    ]
    
    results = []
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))
        time.sleep(0.5)  # Brief pause between tests
    
    # Summary
    print(f"\n{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}TEST SUMMARY{Colors.END}")
    print(f"{Colors.BLUE}{'='*70}{Colors.END}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{Colors.GREEN}✓ PASS{Colors.END}" if result else f"{Colors.RED}✗ FAIL{Colors.END}"
        print(f"{status} - {name}")
    
    print(f"\n{Colors.BLUE}{'='*70}{Colors.END}")
    if passed == total:
        print(f"{Colors.GREEN}ALL TESTS PASSED! ({passed}/{total}){Colors.END}")
    else:
        print(f"{Colors.YELLOW}TESTS PASSED: {passed}/{total}{Colors.END}")
    print(f"{Colors.BLUE}{'='*70}{Colors.END}\n")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrupted by user{Colors.END}")
        exit(1)
    except Exception as e:
        print_error(f"Test suite failed: {e}")
        exit(1)