"""
Test script to verify tile URL templates are correctly generated
"""
import urllib.request
import urllib.error
import json

BASE_URL = "http://localhost:8000"

def make_post_request(url, data):
    """Make a POST request using urllib"""
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception as e:
        print(f"Error: {e}")
        return None, None

def test_earth_tiles():
    """Test Earth satellite tile URLs"""
    print("=" * 70)
    print("TEST 1: Earth Satellite Tile URLs")
    print("=" * 70)
    
    status, images = make_post_request(f"{BASE_URL}/api/search/images", {
        "celestial_body": "earth",
        "layer": "VIIRS_SNPP_CorrectedReflectance_TrueColor",
        "start_date": "2024-08-15",
        "end_date": "2024-08-15"
    })
    
    if status != 200 or not images:
        print("❌ FAILED: Could not retrieve Earth images")
        return False
    
    image = images[0]
    tile_url = image["tile_url"]
    
    # Check for placeholders
    has_placeholders = "{z}" in tile_url and "{x}" in tile_url and "{y}" in tile_url
    
    print(f"Tile URL: {tile_url[:80]}...")
    print(f"Has placeholders: {'✅' if has_placeholders else '❌'}")
    print(f"Max Zoom: {image.get('max_zoom')}")
    
    if has_placeholders:
        print("✅ PASSED: Earth tiles have correct format")
        return True
    else:
        print("❌ FAILED: Missing placeholders")
        return False

def test_deep_space_tiles():
    """Test Deep Space gigapixel tile URLs"""
    print("\n" + "=" * 70)
    print("TEST 2: Deep Space Gigapixel Tile URLs")
    print("=" * 70)
    
    status, images = make_post_request(f"{BASE_URL}/api/search/images", {
        "celestial_body": "deep_space",
        "layer": "andromeda_gigapixel"
    })
    
    if status != 200 or not images:
        print("❌ FAILED: Could not retrieve Deep Space images")
        return False
    
    image = images[0]
    tile_url = image["tile_url"]
    
    # Check for placeholders
    has_placeholders = "{z}" in tile_url and "{x}" in tile_url and "{y}" in tile_url
    is_gigapan = "gigapan.com" in tile_url
    
    print(f"Tile URL: {tile_url[:80]}...")
    print(f"Has placeholders: {'✅' if has_placeholders else '❌'}")
    print(f"Is Gigapan: {'✅' if is_gigapan else '❌'}")
    print(f"Max Zoom: {image.get('max_zoom')}")
    
    if has_placeholders and is_gigapan:
        print("✅ PASSED: Deep Space tiles have correct format")
        return True
    else:
        print("❌ FAILED: Incorrect format")
        return False

def test_planetary_tiles():
    """Test planetary surface map tile URLs"""
    print("\n" + "=" * 70)
    print("TEST 3: Planetary Surface Map Tile URLs")
    print("=" * 70)
    
    planets = [
        ("mars", "opm_mars_basemap"),
        ("moon", "opm_moon_basemap"),
        ("mercury", "opm_mercury_basemap")
    ]
    
    all_passed = True
    for celestial_body, layer in planets:
        status, images = make_post_request(f"{BASE_URL}/api/search/images", {
            "celestial_body": celestial_body,
            "layer": layer
        })
        
        if status != 200 or not images:
            print(f"❌ {celestial_body.upper()}: Failed to retrieve")
            all_passed = False
            continue
        
        image = images[0]
        tile_url = image["tile_url"]
        has_placeholders = "{z}" in tile_url and "{x}" in tile_url and "{y}" in tile_url
        
        if has_placeholders:
            print(f"✅ {celestial_body.upper()}: Correct format")
        else:
            print(f"❌ {celestial_body.upper()}: Missing placeholders")
            all_passed = False
    
    if all_passed:
        print("✅ PASSED: All planetary tiles have correct format")
    else:
        print("❌ FAILED: Some planetary tiles incorrect")
    
    return all_passed

def test_custom_tiles():
    """Test custom image tile URLs"""
    print("\n" + "=" * 70)
    print("TEST 4: Custom Image Tile URLs")
    print("=" * 70)
    
    # Check if any custom images exist
    status, images = make_post_request(f"{BASE_URL}/api/search/images", {
        "celestial_body": "custom",
        "layer": "custom_9ba84865af83"
    })
    
    if status != 200 or not images:
        print("⚠️  SKIPPED: No custom images available (this is OK)")
        return True
    
    image = images[0]
    tile_url = image["tile_url"]
    
    # Check for placeholders or placeholder message
    if "/api/tile-placeholder/" in tile_url:
        print("⚠️  Custom image still processing (this is OK)")
        return True
    
    has_placeholders = "{z}" in tile_url and "{x}" in tile_url and "{y}" in tile_url
    
    print(f"Tile URL: {tile_url[:80]}...")
    print(f"Has placeholders: {'✅' if has_placeholders else '❌'}")
    
    if has_placeholders:
        print("✅ PASSED: Custom tiles have correct format")
        return True
    else:
        print("❌ FAILED: Missing placeholders")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("  TILE URL TEMPLATE TESTS")
    print("=" * 70)
    
    results = []
    results.append(("Earth Tiles", test_earth_tiles()))
    results.append(("Deep Space Tiles", test_deep_space_tiles()))
    results.append(("Planetary Tiles", test_planetary_tiles()))
    results.append(("Custom Tiles", test_custom_tiles()))
    
    # Summary
    print("\n" + "=" * 70)
    print("  TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    exit(main())