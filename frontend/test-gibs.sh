#!/bin/bash

# NASA GIBS Connection Test Script
# Tests if NASA GIBS tiles are accessible

echo "=================================="
echo "NASA GIBS Connection Test"
echo "=================================="
echo ""

# Get date from 3 days ago
DATE=$(date -v-3d +%Y-%m-%d 2>/dev/null || date -d '3 days ago' +%Y-%m-%d 2>/dev/null || echo "2024-10-01")
echo "Testing with date: $DATE"
echo ""

# Test 1: MODIS Terra True Color
echo "Test 1: MODIS Terra True Color"
URL1="https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/${DATE}/250m/2/1/1.jpg"
echo "URL: $URL1"
if curl -s -o /dev/null -w "%{http_code}" "$URL1" | grep -q "200"; then
    echo "✅ MODIS Terra - SUCCESS"
else
    echo "❌ MODIS Terra - FAILED"
fi
echo ""

# Test 2: Blue Marble (Static - always works)
echo "Test 2: Blue Marble (Static)"
URL2="https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/BlueMarble_NextGeneration/default/2004-08-01/500m/2/1/1.jpg"
echo "URL: $URL2"
if curl -s -o /dev/null -w "%{http_code}" "$URL2" | grep -q "200"; then
    echo "✅ Blue Marble - SUCCESS"
else
    echo "❌ Blue Marble - FAILED (check your internet)"
fi
echo ""

# Test 3: VIIRS SNPP
echo "Test 3: VIIRS SNPP True Color"
URL3="https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/VIIRS_SNPP_CorrectedReflectance_TrueColor/default/${DATE}/250m/2/1/1.jpg"
echo "URL: $URL3"
if curl -s -o /dev/null -w "%{http_code}" "$URL3" | grep -q "200"; then
    echo "✅ VIIRS SNPP - SUCCESS"
else
    echo "❌ VIIRS SNPP - FAILED"
fi
echo ""

echo "=================================="
echo "Recommendations:"
echo "=================================="
echo "1. If Blue Marble works: NASA GIBS is accessible"
echo "2. If other layers fail: Try a date 4-5 days ago"
echo "3. If nothing works: Check firewall/internet"
echo "4. In the app: Select 'Blue Marble' layer (always works)"
echo ""

