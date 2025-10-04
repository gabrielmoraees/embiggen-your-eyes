# NASA GIBS API - Practical Examples

Complete guide to fetching images from NASA GIBS for tile web map applications.

## Table of Contents
- [WMTS Service](#wmts-service)
- [WMS Service](#wms-service)
- [Common Layers](#common-layers)
- [Date Formats](#date-formats)
- [Projections](#projections)
- [Practical Examples](#practical-examples)

## WMTS Service (Recommended for Tiled Maps)

### Base URL Format
```
https://gibs.earthdata.nasa.gov/wmts/{projection}/{quality}/{layer}/default/{date}/{resolution}/{z}/{y}/{x}.{format}
```

### Parameters

| Parameter | Description | Example Values |
|-----------|-------------|----------------|
| `projection` | Coordinate system | `epsg3857`, `epsg4326`, `epsg3413`, `epsg3031` |
| `quality` | Image quality tier | `best`, `std` |
| `layer` | Layer identifier | See [Common Layers](#common-layers) |
| `date` | Date of imagery | `2025-10-04`, `default` |
| `resolution` | Ground resolution | `250m`, `500m`, `1km`, `2km` |
| `z` | Zoom level | `0` to `9` (varies by layer) |
| `y` | Tile row | `0` to `2^z - 1` |
| `x` | Tile column | `0` to `2^z - 1` |
| `format` | Image format | `jpg`, `png` |

### Working WMTS Examples

#### Example 1: MODIS Terra True Color (Today)
```
https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/2025-10-04/250m/2/1/1.jpg
```
- **Layer**: MODIS Terra Corrected Reflectance True Color
- **Date**: October 4, 2025
- **Zoom**: 2, Tile: (1,1)
- **Resolution**: 250m
- **Format**: JPG

#### Example 2: VIIRS SNPP True Color
```
https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/VIIRS_SNPP_CorrectedReflectance_TrueColor/default/2025-10-04/250m/3/2/3.jpg
```
- **Layer**: VIIRS SNPP Corrected Reflectance True Color
- **Date**: October 4, 2025
- **Zoom**: 3, Tile: (2,3)
- **Resolution**: 250m
- **Format**: JPG

#### Example 3: MODIS Aqua True Color
```
https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Aqua_CorrectedReflectance_TrueColor/default/2025-10-03/250m/1/0/0.jpg
```
- **Layer**: MODIS Aqua Corrected Reflectance True Color
- **Date**: October 3, 2025
- **Zoom**: 1, Tile: (0,0)

#### Example 4: Blue Marble (Static)
```
https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/BlueMarble_NextGeneration/default/2004-08-01/500m/4/5/7.jpg
```
- **Layer**: Blue Marble Next Generation (static composite)
- **Fixed Date**: August 1, 2004 (doesn't change)
- **Resolution**: 500m

#### Example 5: Land Surface Temperature
```
https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_Land_Surface_Temp_Day/default/2025-10-04/1km/2/1/2.png
```
- **Layer**: MODIS Terra Land Surface Temperature (Day)
- **Date**: October 4, 2025
- **Resolution**: 1km
- **Format**: PNG (for transparency)

#### Example 6: Night Lights (Black Marble)
```
https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/VIIRS_Black_Marble/default/2016-01-01/500m/3/4/3.png
```
- **Layer**: VIIRS Black Marble (Earth at night)
- **Date**: 2016 composite
- **Resolution**: 500m

## WMS Service (Alternative)

### Base URL
```
https://gibs.earthdata.nasa.gov/wms/{projection}/{quality}/wms.cgi
```

### GetMap Request Format
```
https://gibs.earthdata.nasa.gov/wms/epsg3857/best/wms.cgi?SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0&LAYERS={layer}&CRS=EPSG:3857&BBOX={minx},{miny},{maxx},{maxy}&WIDTH={width}&HEIGHT={height}&FORMAT={format}&TIME={date}
```

### Working WMS Example
```
https://gibs.earthdata.nasa.gov/wms/epsg3857/best/wms.cgi?SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0&LAYERS=MODIS_Terra_CorrectedReflectance_TrueColor&CRS=EPSG:3857&BBOX=-20037508,-20037508,20037508,20037508&WIDTH=512&HEIGHT=512&FORMAT=image/jpeg&TIME=2025-10-04
```

## Common Layers

### Visible Imagery (True Color)

| Layer ID | Description | Resolution | Temporal | Format |
|----------|-------------|------------|----------|--------|
| `MODIS_Terra_CorrectedReflectance_TrueColor` | MODIS Terra True Color | 250m | Daily | jpg |
| `MODIS_Aqua_CorrectedReflectance_TrueColor` | MODIS Aqua True Color | 250m | Daily | jpg |
| `VIIRS_SNPP_CorrectedReflectance_TrueColor` | VIIRS SNPP True Color | 250m | Daily | jpg |
| `VIIRS_NOAA20_CorrectedReflectance_TrueColor` | VIIRS NOAA-20 True Color | 250m | Daily | jpg |
| `BlueMarble_NextGeneration` | Blue Marble Composite | 500m | Static | jpg |

### Temperature Layers

| Layer ID | Description | Resolution | Temporal | Format |
|----------|-------------|------------|----------|--------|
| `MODIS_Terra_Land_Surface_Temp_Day` | Land Surface Temp (Day) | 1km | Daily | png |
| `MODIS_Terra_Land_Surface_Temp_Night` | Land Surface Temp (Night) | 1km | Daily | png |
| `MODIS_Aqua_Land_Surface_Temp_Day` | Aqua Land Temp (Day) | 1km | Daily | png |

### Reference Layers

| Layer ID | Description | Resolution | Temporal | Format |
|----------|-------------|------------|----------|--------|
| `Reference_Features_15m` | Coastlines, borders | 15m | Static | png |
| `Reference_Labels_15m` | Place names | 15m | Static | png |
| `VIIRS_Black_Marble` | Earth at night | 500m | Static | png |

### Atmospheric & Environmental

| Layer ID | Description | Resolution | Temporal | Format |
|----------|-------------|------------|----------|--------|
| `MODIS_Terra_Aerosol` | Aerosol Optical Depth | 1km | Daily | png |
| `MODIS_Terra_Snow_Cover` | Snow Cover | 500m | Daily | png |
| `MODIS_Combined_MAIAC_L2G_AOT` | High-res Aerosol | 1km | Daily | png |

## Date Formats

### For Temporal Layers
- **Format**: `YYYY-MM-DD`
- **Example**: `2025-10-04`
- **Valid Range**: Usually from 2000-present (varies by layer)
- **Latency**: 3-4 hours for NRT (Near Real-Time), 1-2 days for standard

### For Static Layers
- **Blue Marble**: `2004-08-01` (always use this date)
- **Black Marble**: `2016-01-01` (always use this date)
- **Reference Layers**: Use `default` in URL

### Checking Latest Available Date
```bash
curl "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/wmts.cgi?SERVICE=WMTS&REQUEST=GetCapabilities" | grep -A 5 "MODIS_Terra_CorrectedReflectance_TrueColor"
```

## Projections

### EPSG:3857 (Web Mercator) - Recommended for Web Maps
```
https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/{layer}/default/{date}/{resolution}/{z}/{y}/{x}.{format}
```
- Used by Google Maps, Leaflet, OpenLayers
- Best for general web mapping
- Distorts near poles

### EPSG:4326 (Geographic/WGS84)
```
https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/{layer}/default/{date}/{resolution}/{z}/{y}/{x}.{format}
```
- Latitude/Longitude grid
- Better for scientific applications
- No distortion

### EPSG:3413 (Arctic Polar Stereographic)
```
https://gibs.earthdata.nasa.gov/wmts/epsg3413/best/{layer}/default/{date}/{resolution}/{z}/{y}/{x}.{format}
```
- Optimized for Arctic region
- Used for polar research

### EPSG:3031 (Antarctic Polar Stereographic)
```
https://gibs.earthdata.nasa.gov/wmts/epsg3031/best/{layer}/default/{date}/{resolution}/{z}/{y}/{x}.{format}
```
- Optimized for Antarctic region
- Used for polar research

## Practical Examples

### Example 1: Loading in Leaflet
```javascript
const gibsLayer = L.tileLayer(
    'https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/{date}/250m/{z}/{y}/{x}.jpg',
    {
        attribution: '© NASA GIBS',
        tileSize: 256,
        date: '2025-10-04',
        bounds: [[-85.0511, -180], [85.0511, 180]],
        minZoom: 1,
        maxZoom: 9
    }
);
```

### Example 2: Testing a Single Tile
```bash
# Download a specific tile
curl "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/2025-10-04/250m/2/1/1.jpg" -o test_tile.jpg
```

### Example 3: GetCapabilities Discovery
```bash
# Get full list of available layers
curl "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/wmts.cgi?SERVICE=WMTS&REQUEST=GetCapabilities" > gibs_capabilities.xml
```

### Example 4: Fetch Multiple Dates (Time Series)
```javascript
const dates = ['2025-10-01', '2025-10-02', '2025-10-03', '2025-10-04'];
dates.forEach(date => {
    const url = `https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/${date}/250m/3/2/3.jpg`;
    console.log(url);
});
```

### Example 5: Layer Comparison
```javascript
// Layer 1: True Color
const layer1 = 'https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/2025-10-04/250m/{z}/{y}/{x}.jpg';

// Layer 2: Land Surface Temperature
const layer2 = 'https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_Land_Surface_Temp_Day/default/2025-10-04/1km/{z}/{y}/{x}.png';

// Add both to map with different opacity
```

## Tile Coordinate System

### Understanding Z/Y/X Coordinates

For EPSG:3857 (Web Mercator):
- **Zoom Level 0**: 1 tile (entire world)
- **Zoom Level 1**: 4 tiles (2x2)
- **Zoom Level 2**: 16 tiles (4x4)
- **Zoom Level n**: 2^n × 2^n tiles

### Tile Coverage Examples

#### Zoom Level 2, Tile (1,1)
```
https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/2025-10-04/250m/2/1/1.jpg
```
Covers: Africa and parts of Europe/Middle East

#### Zoom Level 3, Tile (2,3)
```
https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/2025-10-04/250m/3/2/3.jpg
```
Covers: North America (central)

#### Zoom Level 5, Tile (10,12)
```
https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/2025-10-04/250m/5/10/12.jpg
```
Covers: California region

## Quality Tiers

### `best` (Recommended)
- Highest quality available
- Latest processing algorithms
- Use for production

### `std` (Standard)
- Standard quality
- May use older algorithms
- Faster processing

**Example URLs:**
```
# Best quality
https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/...

# Standard quality
https://gibs.earthdata.nasa.gov/wmts/epsg3857/std/...
```

## Image Formats

### JPG (`.jpg`)
- **Use for**: True color imagery, no transparency needed
- **Size**: Smaller files, faster loading
- **Quality**: Good for photographic imagery
- **Compression**: Lossy

### PNG (`.png`)
- **Use for**: Layers with transparency, scientific data
- **Size**: Larger files
- **Quality**: Lossless
- **Transparency**: Supports alpha channel

## Common Issues & Solutions

### Issue: Tiles Not Loading
**Solutions:**
1. Check date validity (may not have data for very recent dates)
2. Verify layer name spelling
3. Check zoom level is within range
4. Ensure date is in correct format (YYYY-MM-DD)

### Issue: Gray/Missing Tiles
**Solutions:**
1. Layer may not have coverage for that date
2. Try yesterday's date (24-48 hour latency)
3. Check GetCapabilities for valid date range

### Issue: CORS Errors
**Solutions:**
1. GIBS supports CORS by default
2. Ensure proper HTTPS usage
3. Check browser console for specific errors

## Performance Tips

1. **Use JPG for visible imagery** - Smaller files, faster loading
2. **Limit max zoom** - Higher zooms = more tiles = slower performance
3. **Cache tiles** - Browser caching is automatic
4. **Use Web Mercator (EPSG:3857)** - Most compatible with web libraries
5. **Preload nearby tiles** - Most libraries do this automatically

## Additional Resources

- **Full Layer List**: https://nasa-gibs.github.io/gibs-api-docs/available-visualizations/
- **API Documentation**: https://nasa-gibs.github.io/gibs-api-docs/
- **GetCapabilities URL**: https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/wmts.cgi?SERVICE=WMTS&REQUEST=GetCapabilities
- **Worldview (Test Interface)**: https://worldview.earthdata.nasa.gov/
- **GitHub Examples**: https://github.com/nasa-gibs/gibs-web-examples
- **GIBS Status**: https://status.earthdata.nasa.gov/

## Quick Reference Card

```
# Template URL
https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/{LAYER}/default/{DATE}/{RESOLUTION}/{Z}/{Y}/{X}.{FORMAT}

# Example: MODIS True Color, Today, Zoom 2
https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/2025-10-04/250m/2/1/1.jpg

# Popular Layers:
- MODIS_Terra_CorrectedReflectance_TrueColor
- VIIRS_SNPP_CorrectedReflectance_TrueColor
- BlueMarble_NextGeneration
- MODIS_Terra_Land_Surface_Temp_Day
- VIIRS_Black_Marble

# Projections:
- epsg3857 (Web Mercator) ← Use this for web maps
- epsg4326 (Geographic)
- epsg3413 (Arctic)
- epsg3031 (Antarctic)

# Date Format: YYYY-MM-DD
# Zoom Range: 0-9 (varies by layer)
# Formats: jpg (smaller) or png (transparency)
```

---

**Need help?** Check the [NASA GIBS documentation](https://nasa-gibs.github.io/gibs-api-docs/) or explore [NASA Worldview](https://worldview.earthdata.nasa.gov/) to discover more layers!

