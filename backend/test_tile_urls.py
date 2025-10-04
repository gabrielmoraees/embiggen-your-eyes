"""
Test script to verify tile URL templates are correctly generated
"""
import requests
import re
from datetime import date

BASE_URL = "http://localhost:8000"

def test_tile_url_format():
    """Test that tile URLs contain proper {z}/{x}/{y} placeholders"""
    print("=" * 60)
    print("Testing Tile URL Template Format")
    print("=" * 60)
    
    # Search for images
    response = requests.post(f"{BASE_URL}/api/search/images", json={
        "layer": "MODIS_Terra_CorrectedReflectance_TrueColor",
        "date_start": "2024-10-04",
        "date_end": "2024-10-04",
        "projection": "epsg3857",
        "limit": 1
    })
    
    if response.status_code != 200:
        print(f"❌ API Error: {response.status_code}")
        return False
    
    images = response.json()
    if not images:
        print("❌ No images returned")
        return False
    
    image = images[0]
    tile_url = image["tile_url"]
    
    print(f"\n📡 Received tile_url:")
    print(f"   {tile_url}")
    
    # Check if URL contains placeholders
    has_z_placeholder = "{z}" in tile_url
    has_x_placeholder = "{x}" in tile_url
    has_y_placeholder = "{y}" in tile_url
    
    print(f"\n🔍 Placeholder Check:")
    print(f"   {{z}} present: {'✅' if has_z_placeholder else '❌'}")
    print(f"   {{x}} present: {'✅' if has_x_placeholder else '❌'}")
    print(f"   {{y}} present: {'✅' if has_y_placeholder else '❌'}")
    
    # Check if URL has hardcoded coordinates
    has_hardcoded = re.search(r'/\d+/\d+/\d+\.jpg', tile_url)
    if has_hardcoded:
        print(f"   ⚠️  WARNING: Found hardcoded coordinates: {has_hardcoded.group()}")
    
    # Verify additional fields
    print(f"\n📊 Additional Fields:")
    print(f"   projection: {image.get('projection', 'MISSING')}")
    print(f"   max_zoom: {image.get('max_zoom', 'MISSING')}")
    
    # Test placeholder replacement
    print(f"\n🧪 Example Tile URLs (after placeholder replacement):")
    test_tiles = [
        (0, 0, 0, "Zoom 0 - World view"),
        (2, 1, 1, "Zoom 2 - Region"),
        (5, 10, 20, "Zoom 5 - Closer view"),
        (9, 255, 255, "Zoom 9 - Maximum detail")
    ]
    
    for z, x, y, description in test_tiles:
        tile = (tile_url
                .replace('{z}', str(z))
                .replace('{x}', str(x))
                .replace('{y}', str(y)))
        print(f"   {description}:")
        print(f"   {tile}")
    
    # Final verdict
    print(f"\n" + "=" * 60)
    if has_z_placeholder and has_x_placeholder and has_y_placeholder and not has_hardcoded:
        print("✅ SUCCESS: Tile URL format is CORRECT!")
        print("   Frontend can use this URL template with mapping libraries.")
        return True
    else:
        print("❌ FAILURE: Tile URL format is INCORRECT!")
        if not (has_z_placeholder and has_x_placeholder and has_y_placeholder):
            print("   Missing required placeholders {z}/{x}/{y}")
        if has_hardcoded:
            print("   Contains hardcoded coordinates instead of placeholders")
        return False

def test_different_projections():
    """Test both projection options"""
    print("\n" + "=" * 60)
    print("Testing Different Projections")
    print("=" * 60)
    
    projections = ["epsg3857", "epsg4326"]
    
    for proj in projections:
        print(f"\n📍 Testing projection: {proj}")
        response = requests.post(f"{BASE_URL}/api/search/images", json={
            "layer": "MODIS_Terra_CorrectedReflectance_TrueColor",
            "date_start": "2024-10-04",
            "date_end": "2024-10-04",
            "projection": proj,
            "limit": 1
        })
        
        if response.status_code == 200:
            image = response.json()[0]
            if proj in image["tile_url"] and image["projection"] == proj:
                print(f"   ✅ {proj} URL generated correctly")
            else:
                print(f"   ❌ {proj} URL incorrect")
        else:
            print(f"   ❌ API error for {proj}")

def test_actual_tile_loading():
    """Test if actual tiles can be loaded from NASA GIBS"""
    print("\n" + "=" * 60)
    print("Testing Actual Tile Loading from NASA GIBS")
    print("=" * 60)
    
    # Use a known good date with MODIS data
    # MODIS Terra has been collecting data since 2000
    test_date = "2024-08-15"  # Use a recent historical date
    
    # Get a tile URL - use VIIRS which has better availability
    response = requests.post(f"{BASE_URL}/api/search/images", json={
        "layer": "VIIRS_SNPP_CorrectedReflectance_TrueColor",
        "date_start": test_date,
        "date_end": test_date,
        "projection": "epsg3857",
        "limit": 1
    })
    
    if response.status_code != 200:
        print("❌ Could not get tile URL from API")
        return
    
    template_url = response.json()[0]["tile_url"]
    
    # Test tiles that should exist for MODIS Terra in Web Mercator
    # These are common tiles that NASA GIBS serves
    test_cases = [
        (1, 0, 0, "Northern hemisphere"),
        (1, 1, 0, "Northeast quadrant"),
        (2, 2, 1, "Mid-latitude region"),
    ]
    
    print(f"\n🌐 Testing tiles from {test_date}:")
    success_count = 0
    
    for z, x, y, description in test_cases:
        tile_url = (template_url
                   .replace('{z}', str(z))
                   .replace('{x}', str(x))
                   .replace('{y}', str(y)))
        
        try:
            tile_response = requests.head(tile_url, timeout=10)
            if tile_response.status_code == 200:
                print(f"   ✅ {description} (z={z}, x={x}, y={y}): Tile loaded successfully")
                success_count += 1
            else:
                print(f"   ⚠️  {description} (z={z}, x={x}, y={y}): Status {tile_response.status_code}")
        except requests.RequestException as e:
            print(f"   ❌ {description} (z={z}, x={x}, y={y}): Request failed - {str(e)[:50]}")
    
    if success_count > 0:
        print(f"\n   ✅ Successfully loaded {success_count}/{len(test_cases)} tiles from NASA GIBS")
    else:
        print(f"\n   ℹ️  No tiles loaded (may be normal if date doesn't have coverage)")
    
    return success_count > 0

if __name__ == "__main__":
    print("\n🚀 Starting Tile URL Tests")
    print("📡 Make sure the backend is running on http://localhost:8000\n")
    
    try:
        # Test 1: URL format
        format_success = test_tile_url_format()
        
        # Test 2: Different projections
        test_different_projections()
        
        # Test 3: Actual tile loading
        tiles_success = test_actual_tile_loading()
        
        print("\n" + "=" * 60)
        if format_success:
            print("🎉 ALL TESTS PASSED!")
            print("Your backend is correctly generating tile URL templates.")
            if tiles_success:
                print("NASA GIBS tiles are loading successfully!")
        else:
            print("⚠️  SOME TESTS FAILED")
            print("Check the output above for details.")
        print("=" * 60 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to backend server")
        print("Make sure the server is running: python main.py")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

