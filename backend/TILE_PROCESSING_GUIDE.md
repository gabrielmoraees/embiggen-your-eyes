# On-Demand Tile Processing System

## Overview

The Embiggen Your Eyes API now includes an **on-demand tile processing system** that automatically converts NASA gigapixel images into tile pyramids when they're first requested. This allows all celestial bodies (Earth, Mars, Moon, Mercury, and Deep Space) to use the same tile-based rendering approach.

## How It Works

### 1. **Automatic Processing**
When a user searches for a deep space object:
- The API checks if tiles already exist
- If not, it triggers background processing automatically
- The image is downloaded from NASA
- GDAL converts it to a tile pyramid
- Tiles are cached for future requests

### 2. **Tile Processing Flow**

```
User Request → Check Cache → Tiles Exist? 
                              ├─ YES: Return tile URL
                              └─ NO:  Trigger Processing → Return Placeholder
                                      ↓
                                  Background Processing:
                                  1. Download NASA image
                                  2. Generate tiles (GDAL)
                                  3. Update cache index
                                  4. Tiles ready for next request
```

### 3. **File Structure**

```
backend/
├── main.py                    # Main API with tile endpoints
├── tile_processor.py          # Tile processing logic
├── tiles_cache/               # Generated tiles (served statically)
│   ├── {tile_id}/            # One directory per image
│   │   ├── 0/                # Zoom level 0
│   │   ├── 1/                # Zoom level 1
│   │   └── ...               # Up to max zoom
│   └── tile_index.json       # Index of processed tiles
└── downloads/                 # Downloaded source images
    └── {tile_id}.jpg         # Original NASA images
```

## API Endpoints

### 1. **Search Images** (Enhanced)
```http
POST /api/search/images
Content-Type: application/json

{
  "celestial_body": "deep_space",
  "layer": "andromeda_m31",
  "start_date": "2024-01-01",
  "end_date": "2024-01-01"
}
```

**Response:**
- If tiles exist: Returns tile URL template like `/tiles/{tile_id}/{z}/{x}/{y}.png`
- If processing: Returns placeholder URL `/api/tile-placeholder/{layer}`
- Processing starts automatically in background

### 2. **Check Tile Status**
```http
GET /api/tile-status/{layer}
```

**Response:**
```json
{
  "layer": "andromeda_m31",
  "status": "completed",  // or "processing", "failed", "not_started"
  "tile_info": {
    "tile_id": "abc123...",
    "max_zoom": 8,
    "created_at": "2024-01-01T12:00:00"
  }
}
```

### 3. **Manually Trigger Processing**
```http
POST /api/process-tiles/{layer}
```

**Response:**
```json
{
  "message": "Tile processing started",
  "status": "processing",
  "layer": "andromeda_m31",
  "check_status_url": "/api/tile-status/andromeda_m31"
}
```

## Configuration

### Deep Space Catalog
In `main.py`, each deep space object has a `uses_tiling` flag:

```python
DEEP_SPACE_CATALOG = {
    "andromeda_m31": {
        "name": "Andromeda Galaxy (M31)",
        "image_url": "https://images-assets.nasa.gov/...",
        "uses_tiling": True,  # Enable on-demand tiling
        ...
    }
}
```

### Tile Processor Settings
In `tile_processor.py`:

```python
# Tile generation settings
--zoom=0-8           # Zoom levels (0-8 = 9 levels)
--profile=mercator   # Web Mercator (EPSG:3857)
--processes=4        # Use 4 CPU cores
```

## Installation

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Install GDAL

**macOS (Homebrew):**
```bash
brew install gdal
```

**Ubuntu/Debian:**
```bash
sudo apt-get install gdal-bin python3-gdal
```

**Verify Installation:**
```bash
gdal2tiles.py --help
```

### 3. Start Server
```bash
uvicorn main:app --reload --port 8000
```

## Frontend Integration

### Polling Pattern (Recommended)
```javascript
async function loadDeepSpaceImage(layer) {
  // 1. Request the image
  const response = await fetch('/api/search/images', {
    method: 'POST',
    body: JSON.stringify({
      celestial_body: 'deep_space',
      layer: layer,
      start_date: '2024-01-01',
      end_date: '2024-01-01'
    })
  });
  
  const data = await response.json();
  const tileUrl = data[0].tile_url;
  
  // 2. Check if tiles are ready
  if (tileUrl.includes('/api/tile-placeholder/')) {
    // Tiles not ready - poll for status
    await pollTileStatus(layer);
    // Retry after processing completes
    return loadDeepSpaceImage(layer);
  }
  
  // 3. Tiles ready - use with Leaflet
  L.tileLayer(tileUrl, {
    maxZoom: data[0].max_zoom,
    attribution: data[0].description
  }).addTo(map);
}

async function pollTileStatus(layer) {
  while (true) {
    const status = await fetch(`/api/tile-status/${layer}`).then(r => r.json());
    
    if (status.status === 'completed') {
      console.log('Tiles ready!');
      break;
    } else if (status.status === 'failed') {
      throw new Error('Tile processing failed');
    }
    
    // Wait 5 seconds before checking again
    await new Promise(resolve => setTimeout(resolve, 5000));
  }
}
```

### Direct Usage (If Tiles Pre-processed)
```javascript
// Standard tile layer usage (same as planets)
const tileUrl = data[0].tile_url;  // e.g., /tiles/abc123/{z}/{x}/{y}.png

L.tileLayer(tileUrl, {
  maxZoom: data[0].max_zoom,
  attribution: data[0].description
}).addTo(map);
```

## Performance Considerations

### Processing Time
- **Small images (<10 MB):** 10-30 seconds
- **Medium images (10-100 MB):** 1-3 minutes
- **Large images (100 MB - 1 GB):** 5-15 minutes
- **Gigapixel images (1+ GB):** 15-60+ minutes

### Disk Space
- **Source images:** 10 MB - 2 GB each
- **Tile pyramids:** 2-5x source image size
- **Total per image:** Up to 10 GB for gigapixel images

### Recommendations
1. **Pre-process popular images** during setup
2. **Set up monitoring** for disk space
3. **Implement cleanup** for old/unused tiles
4. **Use CDN** for production tile serving

## Pre-processing Script

To pre-process tiles before deployment:

```bash
# Create preprocessing script
cat > preprocess_tiles.py << 'EOF'
import requests
import time

layers = [
    "andromeda_m31",
    "whirlpool_m51",
    "sombrero_m104",
    "carina_nebula",
    "orion_nebula",
    "pillars_creation"
]

for layer in layers:
    print(f"Processing {layer}...")
    
    # Trigger processing
    response = requests.post(f"http://localhost:8000/api/process-tiles/{layer}")
    print(response.json())
    
    # Poll status
    while True:
        status = requests.get(f"http://localhost:8000/api/tile-status/{layer}").json()
        print(f"  Status: {status['status']}")
        
        if status['status'] == 'completed':
            break
        elif status['status'] == 'failed':
            print(f"  ERROR: {status}")
            break
        
        time.sleep(10)
    
    print(f"✓ {layer} complete\n")

print("All tiles processed!")
EOF

python3 preprocess_tiles.py
```

## Troubleshooting

### GDAL Not Found
```bash
# Check if GDAL is installed
which gdal2tiles.py

# If not found, install:
brew install gdal  # macOS
# or
sudo apt-get install gdal-bin  # Linux
```

### Processing Hangs
- Check logs for errors
- Verify source image URL is accessible
- Check disk space available
- Increase timeout in `tile_processor.py`

### Tiles Not Loading
- Verify tiles directory is mounted correctly
- Check file permissions
- Confirm tile_index.json is valid JSON
- Check browser network tab for 404 errors

### Out of Disk Space
```bash
# Check disk usage
du -sh tiles_cache/
du -sh downloads/

# Clean up old downloads
rm -rf downloads/*

# Remove specific tiles
rm -rf tiles_cache/{tile_id}/
# Update tile_index.json to remove entry
```

## Production Recommendations

### 1. **Use Object Storage**
```python
# Instead of local filesystem
# Use S3, Google Cloud Storage, or Azure Blob
TILES_BASE_DIR = "s3://your-bucket/tiles/"
```

### 2. **Add Caching Layer**
- CloudFront, Cloudflare, or Fastly CDN
- Cache tiles at edge locations
- Reduce origin server load

### 3. **Process Asynchronously**
- Use Celery or RQ for background jobs
- Separate worker processes
- Better error handling and retries

### 4. **Add Monitoring**
```python
# Track processing metrics
- Processing success/failure rate
- Average processing time
- Disk space usage
- Cache hit/miss ratio
```

### 5. **Implement Cleanup**
```python
# Automated maintenance
- Remove tiles older than X days
- Implement LRU eviction
- Compress old tiles
```

## Benefits

✅ **Consistent UX:** All celestial bodies use same tile-based interface  
✅ **On-Demand Processing:** Only process images that users actually request  
✅ **Automatic Caching:** Once processed, tiles are served instantly  
✅ **Scalable:** Add new images without manual pre-processing  
✅ **Flexible:** Easy to add new NASA image sources  
✅ **Progressive:** Works with existing static image fallback  

## Limitations

⚠️ **First Request Slow:** Initial tile generation takes time  
⚠️ **Disk Space:** Gigapixel images require significant storage  
⚠️ **GDAL Dependency:** Requires system-level installation  
⚠️ **CPU Intensive:** Tile generation uses significant CPU  
⚠️ **No Streaming:** Users must wait for complete processing  

## Future Enhancements

- **Streaming tile generation:** Return lower zoom levels first
- **Progressive loading:** Show preview while processing
- **Distributed processing:** Use multiple workers
- **Smart caching:** Predict popular images
- **Compression:** Use WebP or AVIF for smaller tiles
- **Cloud integration:** Direct NASA API → Cloud Storage → CDN

