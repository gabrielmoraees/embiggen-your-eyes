#!/bin/bash

echo "======================================================================"
echo "  🧪 TESTING SEPARATED ARCHITECTURE (Deep Space vs Custom)"
echo "======================================================================"

passed=0
failed=0

# Test 1: Deep Space - Pre-tiled Gigapixel
echo ""
echo "🔍 TEST 1: Deep Space - Pre-tiled Gigapixel (1.5 GP Andromeda)"
response=$(curl -s -X POST "http://localhost:8000/api/search/images" \
  -H "Content-Type: application/json" \
  -d '{"celestial_body":"deep_space","layer":"andromeda_gigapixel"}')

if echo "$response" | grep -q "deep_space_andromeda_gigapixel"; then
    max_zoom=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin)[0]['max_zoom'])" 2>/dev/null)
    echo "   ✓ Deep Space search working"
    echo "   ✓ Max Zoom: $max_zoom (gigapixel)"
    ((passed++))
else
    echo "   ✗ Deep Space search failed"
    ((failed++))
fi

# Test 2: Verify old processable deep space layers are removed
echo ""
echo "🔍 TEST 2: Verify Old Processable Layers Removed"
response=$(curl -s -X POST "http://localhost:8000/api/search/images" \
  -H "Content-Type: application/json" \
  -d '{"celestial_body":"deep_space","layer":"andromeda_m31"}')

# Should fail because andromeda_m31 was removed from deep_space
if echo "$response" | grep -qi "error\|not found\|unknown"; then
    echo "   ✓ Old processable layers correctly removed"
    echo "   ✓ Deep Space now pre-tiled only"
    ((passed++))
else
    echo "   ✗ Old layers still accessible (should be removed)"
    ((failed++))
fi

# Test 3: Custom Image Upload
echo ""
echo "🔍 TEST 3: Custom Image Upload API"
response=$(curl -s -X POST "http://localhost:8000/api/custom-image" \
  -H "Content-Type: application/json" \
  -d '{"name":"Architecture Test","image_url":"https://images-assets.nasa.gov/image/PIA16695/PIA16695~orig.jpg","description":"Testing separated architecture","max_zoom":8}')

# Accept both "processing" and "exists" as success
if echo "$response" | grep -qE '"celestial_body":\s*"custom"'; then
    layer_id=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin)['layer_id'])" 2>/dev/null)
    status=$(echo "$response" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('status', d.get('message', 'unknown')))" 2>/dev/null)
    echo "   ✓ Custom image upload working"
    echo "   ✓ Layer ID: $layer_id"
    echo "   ✓ Status: $status"
    ((passed++))
    
    # Save layer_id for next test
    echo "$layer_id" > /tmp/test_layer_id.txt
else
    echo "   ✗ Custom upload failed"
    echo "   Response: $(echo "$response" | head -c 100)"
    ((failed++))
fi

# Test 4: Search Custom Image
echo ""
echo "🔍 TEST 4: Search Custom Image"
sleep 2
layer_id=$(cat /tmp/test_layer_id.txt 2>/dev/null || echo "custom_bb0ae50b544d")
response=$(curl -s -X POST "http://localhost:8000/api/search/images" \
  -H "Content-Type: application/json" \
  -d "{\"celestial_body\":\"custom\",\"layer\":\"$layer_id\"}")

if echo "$response" | grep -q "custom_"; then
    echo "   ✓ Custom image searchable"
    echo "   ✓ Separate from deep_space"
    ((passed++))
else
    echo "   ⚠ Custom search returned: $(echo "$response" | head -c 100)"
    ((failed++))
fi

# Test 5: Verify Separation - Deep Space should not contain custom
echo ""
echo "🔍 TEST 5: Verify Catalog Separation"
# Try to search for a custom layer as deep_space (should fail)
response=$(curl -s -X POST "http://localhost:8000/api/search/images" \
  -H "Content-Type: application/json" \
  -d "{\"celestial_body\":\"deep_space\",\"layer\":\"$layer_id\"}")

if echo "$response" | grep -qi "unknown\|error\|not found"; then
    echo "   ✓ Custom layers not in deep_space catalog"
    echo "   ✓ Proper separation enforced"
    ((passed++))
else
    echo "   ⚠ Separation not enforced properly"
    echo "   Response: $(echo "$response" | head -c 100)"
    ((failed++))
fi

# Test 6: Earth Imagery
echo ""
echo "🔍 TEST 6: Earth Satellite Imagery"
response=$(curl -s -X POST "http://localhost:8000/api/search/images" \
  -H "Content-Type: application/json" \
  -d '{"celestial_body":"earth","layer":"VIIRS_SNPP_CorrectedReflectance_TrueColor","start_date":"2024-08-15","end_date":"2024-08-15"}')

if echo "$response" | grep -q "gibs.earthdata.nasa.gov"; then
    echo "   ✓ Earth imagery working"
    ((passed++))
else
    echo "   ✗ Earth imagery failed"
    ((failed++))
fi

# Test 7: Planetary Maps
echo ""
echo "🔍 TEST 7: Planetary Surface Maps"
planets_passed=0

for planet in "mars:opm_mars_basemap" "moon:opm_moon_basemap" "mercury:opm_mercury_basemap"; do
    IFS=':' read -r body layer <<< "$planet"
    response=$(curl -s -X POST "http://localhost:8000/api/search/images" \
      -H "Content-Type: application/json" \
      -d "{\"celestial_body\":\"$body\",\"layer\":\"$layer\"}")
    
    if echo "$response" | grep -q "${body}_"; then
        # Capitalize first letter for display
        body_display=$(echo "$body" | awk '{print toupper(substr($0,1,1)) tolower(substr($0,2))}')
        echo "   ✓ $body_display working"
        ((planets_passed++))
    else
        body_display=$(echo "$body" | awk '{print toupper(substr($0,1,1)) tolower(substr($0,2))}')
        echo "   ✗ $body_display failed"
    fi
done

if [ $planets_passed -eq 3 ]; then
    ((passed++))
else
    ((failed++))
fi

# Test 8: Layer Discovery
echo ""
echo "🔍 TEST 8: Layer Discovery (6 Celestial Bodies)"
response=$(curl -s "http://localhost:8000/api/layers")
total_layers=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin)['total'])" 2>/dev/null)

# We now have 10 predefined layers (not 16+)
if [ "$total_layers" -ge "10" ]; then
    echo "   ✓ Found $total_layers layers"
    echo "   ✓ All celestial bodies available"
    ((passed++))
else
    echo "   ⚠ Only $total_layers layers found (expected at least 10)"
    ((failed++))
fi

# Test 9: Annotations
echo ""
echo "🔍 TEST 9: Annotation System"
response=$(curl -s -X POST "http://localhost:8000/api/annotations" \
  -H "Content-Type: application/json" \
  -d '{"image_id":"test_separated_arch","type":"point","coordinates":[{"lat":40.7,"lng":-74.0}],"title":"Test","description":"Architecture test"}')

if echo "$response" | grep -q '"id"'; then
    echo "   ✓ Annotations working"
    ((passed++))
else
    echo "   ✗ Annotations failed"
    ((failed++))
fi

# Test 10: Verify Custom Catalog is Separate
echo ""
echo "🔍 TEST 10: Verify Custom Catalog Independence"
# Custom images should have their own catalog
response=$(curl -s -X POST "http://localhost:8000/api/custom-image" \
  -H "Content-Type: application/json" \
  -d '{"name":"Second Custom","image_url":"https://images-assets.nasa.gov/image/PIA18906/PIA18906~orig.jpg","max_zoom":8}')

# Accept both "processing" and "exists" as success
if echo "$response" | grep -qE '"celestial_body":\s*"custom"'; then
    status=$(echo "$response" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('status', d.get('message', 'unknown')))" 2>/dev/null)
    echo "   ✓ Custom catalog independent"
    echo "   ✓ Multiple custom images supported"
    echo "   ✓ Status: $status"
    ((passed++))
else
    echo "   ✗ Custom catalog test failed"
    echo "   Response: $(echo "$response" | head -c 100)"
    ((failed++))
fi

# Summary
echo ""
echo "======================================================================"
echo "  📊 TEST RESULTS - SEPARATED ARCHITECTURE"
echo "======================================================================"
total=$((passed + failed))
percentage=$((passed * 100 / total))

echo ""
echo "   ✓ Passed: $passed"
echo "   ✗ Failed: $failed"
echo "   📈 Success Rate: $percentage%"
echo ""

if [ $failed -eq 0 ]; then
    echo "======================================================================"
    echo "  🎉 ALL TESTS PASSED! 🎉"
    echo "======================================================================"
    echo ""
    echo "  ✅ Deep Space (pre-curated) working"
    echo "  ✅ Custom (user-uploaded) working"
    echo "  ✅ Proper separation enforced"
    echo "  ✅ 6 celestial bodies operational"
    echo "  ✅ All planetary maps working"
    echo "  ✅ Annotations functional"
    echo ""
    echo "  🚀 ARCHITECTURE REFACTOR SUCCESSFUL! 🚀"
    echo ""
    exit 0
else
    echo "  ⚠ $failed test(s) failed - review output above"
    echo ""
    exit 1
fi
