#!/usr/bin/env python3
"""
Comprehensive test suite for the gigapixel platform
Tests both pre-tiled and custom image processing using urllib (no external dependencies)
"""
import urllib.request
import urllib.error
import json
import time

BASE_URL = "http://localhost:8000"

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
        return e.code, None
    except Exception as e:
        return None, None

def test_health():
    """Test basic API health"""
    print("\n🔍 TEST 1: API Health Check")
    try:
        status, data = make_request(f"{BASE_URL}/")
        print(f"   Status: {status}")
        if status == 200:
            print("   ✓ API is running")
            return True
    except Exception as e:
        print(f"   ✗ API not accessible: {e}")
        return False

def test_layers_endpoint():
    """Test layers discovery endpoint"""
    print("\n🔍 TEST 2: Layer Discovery")
    status, data = make_request(f"{BASE_URL}/api/layers")
    print(f"   Status: {status}")
    
    if status == 200 and data:
        total = data.get("total", 0)
        print(f"   ✓ Found {total} layers")
        
        # Count by celestial body
        by_body = {}
        for layer in data.get("layers", []):
            body = layer["celestial_body"]
            by_body[body] = by_body.get(body, 0) + 1
        
        if "deep_space" in by_body:
            print(f"   ✓ Deep Space has {by_body['deep_space']} layer(s)")
        
        return True
    else:
        print(f"   ✗ Failed")
        return False

def test_pre_tiled_gigapixel():
    """Test pre-tiled gigapixel Andromeda"""
    print("\n🔍 TEST 3: Pre-tiled Gigapixel (1.5 GP Andromeda)")
    
    query = {
        "celestial_body": "deep_space",
        "layer": "andromeda_gigapixel"
    }
    
    status, data = make_request(f"{BASE_URL}/api/search/images", "POST", query)
    print(f"   Status: {status}")
    
    if status == 200 and data and len(data) > 0:
        image = data[0]
        print(f"   ✓ Image ID: {image['id']}")
        print(f"   ✓ Max Zoom: {image['max_zoom']}")
        print(f"   ✓ Tile URL: {image['tile_url'][:60]}...")
        
        # Check if it's a Gigapan URL
        if 'gigapan.com' in image['tile_url']:
            print("   ✓ Using Gigapan tile service (instant, no processing)")
        
        # Verify max_zoom is high (gigapixel)
        if image['max_zoom'] >= 10:
            print(f"   ✓ High zoom level confirmed ({image['max_zoom']} levels)")
        
        return True
    else:
        print(f"   ✗ Failed to get gigapixel image")
        return False

def test_custom_image_upload():
    """Test custom image upload"""
    print("\n🔍 TEST 4: Custom Image Upload")
    
    payload = {
        "name": "Test Gigapixel System",
        "image_url": "https://images-assets.nasa.gov/image/PIA16695/PIA16695~orig.jpg",
        "max_zoom": 8
    }
    
    status, data = make_request(f"{BASE_URL}/api/custom-image", "POST", payload)
    print(f"   Status: {status}")
    
    if status == 200 and data:
        print(f"   ✓ Layer ID: {data['layer_id']}")
        print(f"   ✓ Status: {data.get('status', data.get('message', 'unknown'))}")
        print(f"   ✓ Celestial Body: {data['celestial_body']}")
        return True
    else:
        print(f"   ✗ Upload failed")
        return False

def test_earth_imagery():
    """Test Earth satellite imagery"""
    print("\n🔍 TEST 5: Earth Satellite Imagery")
    
    query = {
        "celestial_body": "earth",
        "layer": "VIIRS_SNPP_CorrectedReflectance_TrueColor",
        "start_date": "2024-08-15",
        "end_date": "2024-08-15"
    }
    
    status, data = make_request(f"{BASE_URL}/api/search/images", "POST", query)
    print(f"   Status: {status}")
    
    if status == 200 and data and len(data) > 0:
        image = data[0]
        print(f"   ✓ Image ID: {image['id']}")
        print(f"   ✓ Using NASA GIBS")
        return True
    else:
        print(f"   ✗ Failed")
        return False

def test_planetary_maps():
    """Test planetary surface maps"""
    print("\n🔍 TEST 6: Planetary Surface Maps")
    
    planets = [
        ("mars", "opm_mars_basemap"),
        ("moon", "opm_moon_basemap"),
        ("mercury", "opm_mercury_basemap")
    ]
    
    all_passed = True
    for body, layer in planets:
        query = {
            "celestial_body": body,
            "layer": layer
        }
        
        status, data = make_request(f"{BASE_URL}/api/search/images", "POST", query)
        
        if status == 200 and data and len(data) > 0:
            print(f"   ✓ {body.capitalize()} accessible")
        else:
            print(f"   ✗ {body.capitalize()} failed")
            all_passed = False
    
    return all_passed

def test_architecture_separation():
    """Test that Deep Space and Custom are properly separated"""
    print("\n🔍 TEST 7: Architecture Separation")
    
    # Try to access a custom layer as deep_space (should fail)
    query = {
        "celestial_body": "deep_space",
        "layer": "custom_test"
    }
    
    status, data = make_request(f"{BASE_URL}/api/search/images", "POST", query)
    
    # Should get an error (not 200)
    if status != 200:
        print("   ✓ Deep Space properly rejects custom layers")
        return True
    else:
        print("   ✗ Separation not enforced")
        return False

def test_tile_url_format():
    """Test that tile URLs have proper placeholders"""
    print("\n🔍 TEST 8: Tile URL Format Validation")
    
    query = {
        "celestial_body": "deep_space",
        "layer": "andromeda_gigapixel"
    }
    
    status, data = make_request(f"{BASE_URL}/api/search/images", "POST", query)
    
    if status == 200 and data and len(data) > 0:
        tile_url = data[0]['tile_url']
        
        # Check for placeholders
        has_z = "{z}" in tile_url or "{z}_" in tile_url
        has_x = "{x}" in tile_url or "_{x}" in tile_url
        has_y = "{y}" in tile_url or "_{y}" in tile_url
        
        if has_z and has_x and has_y:
            print("   ✓ Tile URL has proper placeholders")
            return True
        else:
            print("   ✗ Tile URL missing placeholders")
            return False
    else:
        print("   ✗ Failed to get tile URL")
        return False

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("  GIGAPIXEL SYSTEM - COMPREHENSIVE TEST SUITE")
    print("="*70)
    
    tests = [
        test_health,
        test_layers_endpoint,
        test_pre_tiled_gigapixel,
        test_custom_image_upload,
        test_earth_imagery,
        test_planetary_maps,
        test_architecture_separation,
        test_tile_url_format,
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
        time.sleep(0.5)
    
    # Summary
    print("\n" + "="*70)
    print("  TEST SUMMARY")
    print("="*70)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n   Passed: {passed}/{total}")
    print(f"   Success Rate: {passed * 100 // total}%")
    
    if passed == total:
        print("\n   🎉 ALL TESTS PASSED!")
        return True
    else:
        print(f"\n   ⚠ {total - passed} test(s) failed")
        return False

if __name__ == "__main__":
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\nTest suite failed: {e}")
        exit(1)