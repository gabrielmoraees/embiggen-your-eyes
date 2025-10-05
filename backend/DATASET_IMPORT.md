# Dataset Import Guide

This guide explains how to import custom images from URLs and convert them into tile-based datasets for the application.

## Overview

The dataset import system allows users to:
1. **Import images from URLs** - Provide a URL to any publicly accessible image
2. **Automatic tile processing** - The system converts the image into a tile pyramid
3. **Use as a dataset** - The image becomes available like any other dataset in the catalog
4. **Track progress** - Real-time feedback during download, georeferencing, and tile generation

## How It Works

### Asynchronous Processing

The system uses **asynchronous processing** to provide instant feedback while handling large images:

**Problem**: Downloading and processing gigapixel images can take minutes, blocking HTTP requests.

**Solution**: 
1. **POST /api/datasets** returns immediately with `status: "processing"`
2. Background thread handles download, georeferencing, and tile generation
3. **GET /api/datasets/{dataset_id}/status** allows real-time progress tracking
4. Dataset updates to `status: "ready"` when complete

### Architecture Flow

```
User provides image URL
         ↓
POST /api/datasets (returns immediately with dataset_id)
         ↓
Background Processing Thread (non-daemon)
         ├─→ Download image (0-20%)
         ├─→ Georeference to world bounds (20-40%)
         ├─→ Generate tiles with GDAL (40-95%)
         │   └─→ Real-time tile counting every 2 seconds
         ├─→ Save tile index (95-100%)
         └─→ Update dataset status to "ready"
         ↓
Dataset available in catalog with tile URLs
```

### Tile Processing

The system uses **GDAL** to convert large images into a tile pyramid:
- **Zoom levels**: Dynamically calculated based on image dimensions (typically 0-8)
- **Format**: PNG tiles in XYZ/Slippy Map format (Leaflet-compatible)
- **Projection**: Web Mercator (EPSG:3857)
- **Georeferencing**: Automatic georeferencing to world bounds (EPSG:4326)
- **Storage**: `tiles_cache/{tile_id}/{z}/{x}/{y}.png`
- **Processing**: Asynchronous with real-time progress tracking

## API Endpoints

### 1. Create Dataset from Image

**Endpoint**: `POST /api/datasets`

**Request Body**:
```json
{
  "name": "Andromeda Galaxy",
  "description": "High-resolution image of the Andromeda Galaxy",
  "category": "galaxies",
  "subject": "andromeda",
  "url": "https://esahubble.org/media/archives/images/original/heic2501a.tif"
}
```

**Response** (Immediate):
```json
{
  "success": true,
  "dataset_id": "custom_abc123",
  "dataset": {
    "id": "custom_abc123",
    "name": "Andromeda Galaxy",
    "source_id": "custom",
    "category": "galaxies",
    "subject": "andromeda",
    "processing_status": "processing",
    "variants": [{
      "id": "default",
      "name": "Original",
      "tile_url_template": "",
      "thumbnail_url": "",
      "min_zoom": 0,
      "max_zoom": 8
    }]
  },
  "status": "processing",
  "message": "Dataset created, processing tiles",
  "is_duplicate": false
}
```

**Notes**:
- The endpoint returns **immediately** with `status: "processing"`
- Tile URLs are empty initially and populated when processing completes
- Use the status endpoint to track progress

### 2. Check Processing Status

**Endpoint**: `GET /api/datasets/{dataset_id}/status`

**Response** (Processing):
```json
{
  "dataset_id": "custom_abc123",
  "status": "processing",
  "progress": "generating_tiles",
  "percentage": 65,
  "message": "Generating tiles... 45,234 tiles created",
  "error": null,
  "started_at": "2025-10-05T14:30:00"
}
```

**Response** (Ready):
```json
{
  "dataset_id": "custom_abc123",
  "status": "ready",
  "percentage": 100,
  "message": "Dataset ready!",
  "tile_info": {
    "tile_id": "96b343634272c2059960557f41bdd041",
    "min_zoom": 0,
    "max_zoom": 8,
    "status": "completed",
    "created_at": "2025-10-05T14:35:00"
  }
}
```

**Progress Stages**:
- `"queued"` (0%) - Waiting to start
- `"downloading"` (0-20%) - Downloading image from URL
- `"georeferencing"` (20-40%) - Georeferencing image to world bounds
- `"generating_tiles"` (40-95%) - Creating tile pyramid with real-time count
- `"finalizing"` (95%) - Saving metadata
- `"ready"` (100%) - Complete and ready to use

### 3. List All Datasets

**Endpoint**: `GET /api/datasets`

Returns all datasets including custom ones. Filter by category/subject:
```bash
GET /api/datasets?category=galaxies&subject=andromeda
```

### 4. Delete Dataset

**Endpoint**: `DELETE /api/datasets/{dataset_id}`

**Response**:
```json
{
  "message": "Dataset deleted successfully"
}
```

**Note**: This is a future feature. Currently, datasets are stored in memory and cleared on restart.

## Frontend Integration

### Example: Import and Display Dataset

```javascript
// 1. Create dataset from image
async function createDataset(imageUrl, name, category, subject) {
  const response = await fetch('http://localhost:8000/api/datasets', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      url: imageUrl,
      name: name,
      description: 'Custom uploaded image',
      category: category,
      subject: subject
    })
  });
  
  const result = await response.json();
  return result.dataset_id;
}

// 2. Poll for processing completion with progress updates
async function pollDatasetStatus(datasetId, onProgress) {
  const maxAttempts = 180; // 6 minutes with 2-second intervals
  
  for (let i = 0; i < maxAttempts; i++) {
    const response = await fetch(`http://localhost:8000/api/datasets/${datasetId}/status`);
    const status = await response.json();
    
    // Update UI with progress
    if (onProgress) {
      onProgress({
        percentage: status.percentage || 0,
        message: status.message || 'Processing...',
        progress: status.progress
      });
    }
    
    if (status.status === 'ready') {
      console.log('Dataset ready!');
      return true;
    }
    
    if (status.status === 'failed') {
      throw new Error(status.error || 'Processing failed');
    }
    
    // Wait 2 seconds before next check
    await new Promise(resolve => setTimeout(resolve, 2000));
  }
  
  throw new Error('Processing timeout');
}

// 3. Use the custom dataset
async function loadCustomDataset(datasetId) {
  // Get dataset details
  const response = await fetch(`http://localhost:8000/api/datasets/${datasetId}`);
  const dataset = await response.json();
  
  // Get variant with tile URL
  const variantResponse = await fetch(
    `http://localhost:8000/api/datasets/${datasetId}/variants/default`
  );
  const { variant } = await variantResponse.json();
  
  // Create Leaflet tile layer
  const tileLayer = L.tileLayer(variant.tile_url, {
    minZoom: variant.min_zoom,
    maxZoom: variant.max_zoom,
    attribution: 'Custom Image'
  });
  
  // Add to map
  tileLayer.addTo(map);
}

// Complete workflow with progress UI
async function uploadAndDisplay(imageUrl, name, category, subject) {
  try {
    // Create dataset
    console.log('Creating dataset...');
    const datasetId = await createDataset(imageUrl, name, category, subject);
    
    // Poll with progress updates
    await pollDatasetStatus(datasetId, (progress) => {
      console.log(`${progress.percentage}%: ${progress.message}`);
      // Update UI: progress bar, status text, etc.
    });
    
    // Load and display
    console.log('Loading dataset...');
    await loadCustomDataset(datasetId);
    
    console.log('Custom image displayed!');
  } catch (error) {
    console.error('Error:', error);
  }
}
```

### Example: Import Form

```html
<form id="custom-image-form">
  <label>
    Image URL:
    <input type="url" id="image-url" required 
           placeholder="https://example.com/image.jpg">
  </label>
  
  <label>
    Name:
    <input type="text" id="image-name" required 
           placeholder="My Custom Image">
  </label>
  
  <label>
    Description:
    <textarea id="image-description" 
              placeholder="Optional description"></textarea>
  </label>
  
  <button type="submit">Upload Image</button>
  <div id="upload-status"></div>
</form>

<script>
document.getElementById('custom-image-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const imageUrl = document.getElementById('image-url').value;
  const name = document.getElementById('image-name').value;
  const description = document.getElementById('image-description').value;
  const statusDiv = document.getElementById('upload-status');
  
  statusDiv.textContent = 'Uploading...';
  
  try {
    const response = await fetch('http://localhost:8000/api/custom-images', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        image_url: imageUrl,
        name: name,
        description: description
      })
    });
    
    const result = await response.json();
    
    if (result.status === 'processing') {
      statusDiv.textContent = 'Processing tiles... This may take a few minutes.';
      // Implement polling here
    } else {
      statusDiv.textContent = `Success! Dataset ID: ${result.dataset_id}`;
      // Load the dataset
      await loadCustomDataset(result.dataset_id);
    }
  } catch (error) {
    statusDiv.textContent = `Error: ${error.message}`;
  }
});
</script>
```

## Requirements

### Backend Requirements

1. **GDAL** must be installed:
   ```bash
   # macOS
   brew install gdal
   
   # Ubuntu/Debian
   sudo apt-get install gdal-bin python3-gdal
   ```

2. **Verify GDAL**:
   ```bash
   gdal2tiles.py --help
   ```

### Image Requirements

- **Format**: JPG, PNG, TIFF, or any GDAL-supported format
- **Size**: Any size (will be tiled automatically)
- **URL**: Must be publicly accessible
- **Recommended**: High-resolution images work best

## File Storage

### Directory Structure

```
backend/
├── app/
│   ├── services/                        # Custom image & tile processing logic
│   ├── api/routes/                      # Custom image API endpoints
│   └── models/                          # Data schemas
│
├── tiles_cache/                         # Generated tiles (served statically)
│   ├── {tile_id}/                       # One directory per image
│   │   ├── 0/, 1/, 2/, ...             # Zoom levels
│   │   │   └── {x}/{y}.png             # Tile images
│   │   └── tile_index.json             # Tile metadata
│
└── downloads/                           # Downloaded source images
    └── {tile_id}.{ext}                  # Original images (cached)
```

### Disk Space

- **Source images**: Stored in `downloads/`
- **Tiles**: Stored in `tiles_cache/`
- **Cleanup**: Old tiles can be cleaned up manually or via maintenance script

## Advanced Usage

### Custom Categories

You can categorize custom images:

```json
{
  "image_url": "https://example.com/galaxy.jpg",
  "name": "Custom Galaxy",
  "category": "galaxies",
  "subject": "custom"
}
```

### Batch Import

Import multiple images:

```javascript
const images = [
  { url: 'https://example.com/img1.jpg', name: 'Image 1' },
  { url: 'https://example.com/img2.jpg', name: 'Image 2' },
  { url: 'https://example.com/img3.jpg', name: 'Image 3' }
];

const results = await Promise.all(
  images.map(img => uploadCustomImage(img.url, img.name))
);

console.log(`Imported ${results.length} images`);
```

## Technical Implementation

### Processing Pipeline

The tile generation follows a multi-stage pipeline:

1. **Download** (0-20%):
   - Downloads image from URL to `downloads/{tile_id}.{ext}`
   - Tracks download progress
   - Skips if file already exists (resumable)

2. **Georeferencing** (20-40%):
   - Uses `gdal_translate` to georeference image to world bounds
   - Converts to EPSG:4326 with bounds: `-180, 90, 180, -90`
   - Creates `downloads/{tile_id}_georef.tif`
   - Skips if file already exists (resumable)

3. **Tile Generation** (40-95%):
   - Uses `gdal2tiles.py` with `--profile=mercator --xyz`
   - Calculates optimal zoom levels: `max_zoom = ceil(log2(max_dimension / 256))`
   - Generates tiles in XYZ format (Leaflet-compatible)
   - Real-time progress tracking by counting generated tiles
   - Updates every 2 seconds with tile count
   - Creates `tiles_cache/{tile_id}/{z}/{x}/{y}.png`
   - Skips if tiles already exist (resumable)

4. **Finalization** (95-100%):
   - Saves `tile_index.json` with metadata
   - Updates dataset with tile URLs
   - Sets `min_zoom` and `max_zoom` from generated tiles
   - Marks status as "ready"

### Key Features

**Resumable Processing**: If the backend restarts during processing, the pipeline can resume from any step:
- Checks for existing downloaded image
- Checks for existing georeferenced file
- Checks for existing tiles

**Non-Daemon Threads**: Background threads use `daemon=False` to ensure they complete even if the backend auto-reloads during development.

**Dynamic Zoom Calculation**: Zoom levels are calculated based on image dimensions, not hardcoded:
```python
max_zoom = math.ceil(math.log2(max_dimension / 256))
```

**Progressive Feedback**: Real-time tile counting provides accurate progress:
```python
tile_count = sum(1 for _ in output_dir.rglob('*.png'))
progress_pct = 40 + int((tile_count / estimated_total) * 55)
```

### Benefits

✅ **Instant response**: POST endpoint returns in milliseconds  
✅ **Better UX**: Users get immediate feedback with dataset ID  
✅ **Progressive feedback**: Real-time tile count and percentage updates  
✅ **Scalable**: Multiple images can process concurrently  
✅ **Transparent**: Status endpoint shows detailed progress information  
✅ **Resilient**: Failed processing doesn't crash the API  
✅ **Non-blocking**: Server can handle other requests while processing  
✅ **Resumable**: Can continue from any step (download, georeference, tiles)  
✅ **Dynamic zoom levels**: Automatically calculated based on image dimensions

## Troubleshooting

### GDAL Not Found
```
Error: gdal2tiles.py not found
```
**Solution**: Install GDAL (see Requirements section)

### Image Download Failed
```
Error: Failed to download image
```
**Solution**: Ensure the URL is publicly accessible and returns an image

### Processing Timeout
```
Error: Tile processing timeout
```
**Solution**: Large images may take longer. Increase polling timeout or check server logs.

### Tiles Not Displaying
**Check**:
1. Tile processing completed (`GET /api/tile-status/{tile_id}`)
2. Tiles exist in `tiles_cache/{tile_id}/`
3. Static file serving is enabled
4. Correct tile URL template is used

## Security Considerations

1. **URL Validation**: Only allow trusted image URLs
2. **File Size Limits**: Consider implementing size limits
3. **Rate Limiting**: Limit upload frequency per user
4. **Storage Quotas**: Implement per-user storage limits
5. **Authentication**: Require authentication for uploads

## Future Enhancements

- [ ] Direct file upload (not just URL)
- [ ] Image preprocessing (crop, rotate, adjust)
- [ ] Custom zoom level configuration
- [ ] Tile format options (PNG, JPEG, WebP)
- [ ] Progress tracking during tile generation
- [ ] Automatic cleanup of old tiles
- [ ] User storage quotas
- [ ] Image metadata extraction (EXIF, dimensions)
