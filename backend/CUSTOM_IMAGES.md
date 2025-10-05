## Custom Image Upload

This guide explains how users can upload their own images and use them as tile-based datasets in the application.

## Overview

The custom image system allows users to:
1. **Upload an image from a URL**
2. **Automatic tile processing** - The system converts the image into a tile pyramid
3. **Use as a dataset** - The image becomes available like any other dataset in the catalog

## How It Works

### Architecture Flow

```
User uploads image URL
         ↓
API receives request
         ↓
Custom Image Service
         ├─→ Check if already processed
         ├─→ Download image
         ├─→ Generate tiles (GDAL)
         ├─→ Create dataset entry
         └─→ Return dataset ID
         ↓
Image available in catalog
```

### Tile Processing

The system uses **GDAL** to convert large images into a tile pyramid:
- **Zoom levels**: 0-8 (configurable)
- **Format**: PNG tiles
- **Projection**: Web Mercator (EPSG:3857)
- **Storage**: `tiles_cache/{tile_id}/{z}/{x}/{y}.png`

## API Endpoints

### 1. Upload Custom Image

**Endpoint**: `POST /api/custom-images`

**Request Body**:
```json
{
  "image_url": "https://example.com/my-image.jpg",
  "name": "My Custom Image",
  "description": "Description of my image",
  "category": "custom",
  "subject": "custom"
}
```

**Response**:
```json
{
  "success": true,
  "dataset_id": "custom_abc123",
  "dataset": {
    "id": "custom_abc123",
    "name": "My Custom Image",
    "source_id": "custom",
    "category": "custom",
    "subject": "custom",
    "variants": [{
      "id": "default",
      "name": "Original",
      "tile_url_template": "http://localhost:8000/tiles/{tile_id}/{z}/{x}/{y}.png",
      "thumbnail_url": "http://localhost:8000/tiles/{tile_id}/0/0/0.png"
    }]
  },
  "status": "ready",
  "message": "Dataset created successfully"
}
```

**Status Values**:
- `"ready"` - Tiles are processed and ready to use
- `"processing"` - Tiles are being generated in the background

### 2. List Custom Images

**Endpoint**: `GET /api/custom-images`

**Response**:
```json
{
  "datasets": [
    {
      "id": "custom_abc123",
      "name": "My Custom Image",
      ...
    }
  ],
  "count": 1
}
```

### 3. Check Tile Processing Status

**Endpoint**: `GET /api/tile-status/{tile_id}`

**Response** (Processing):
```json
{
  "status": "processing",
  "progress": "generating_tiles",
  "started_at": "2024-01-01T12:00:00"
}
```

**Response** (Ready):
```json
{
  "status": "ready",
  "tile_info": {
    "tile_id": "abc123",
    "max_zoom": 8,
    "created_at": "2024-01-01T12:05:00"
  }
}
```

### 4. Delete Custom Image

**Endpoint**: `DELETE /api/custom-images/{dataset_id}`

**Response**:
```json
{
  "message": "Custom dataset deleted successfully"
}
```

## Frontend Integration

### Example: Upload and Display Custom Image

```javascript
// 1. Upload custom image
async function uploadCustomImage(imageUrl, name) {
  const response = await fetch('http://localhost:8000/api/custom-images', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      image_url: imageUrl,
      name: name,
      description: 'My custom uploaded image'
    })
  });
  
  const result = await response.json();
  
  if (result.status === 'processing') {
    // Poll for completion
    await pollTileStatus(result.tile_info.tile_id);
  }
  
  return result.dataset_id;
}

// 2. Poll for tile processing completion
async function pollTileStatus(tileId) {
  const maxAttempts = 60; // 5 minutes with 5-second intervals
  
  for (let i = 0; i < maxAttempts; i++) {
    const response = await fetch(`http://localhost:8000/api/tile-status/${tileId}`);
    const status = await response.json();
    
    if (status.status === 'ready') {
      console.log('Tiles ready!');
      return true;
    }
    
    if (status.status === 'failed') {
      throw new Error('Tile processing failed');
    }
    
    // Wait 5 seconds before next check
    await new Promise(resolve => setTimeout(resolve, 5000));
  }
  
  throw new Error('Tile processing timeout');
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

// Complete workflow
async function uploadAndDisplay(imageUrl, name) {
  try {
    console.log('Uploading image...');
    const datasetId = await uploadCustomImage(imageUrl, name);
    
    console.log('Loading dataset...');
    await loadCustomDataset(datasetId);
    
    console.log('Custom image displayed!');
  } catch (error) {
    console.error('Error:', error);
  }
}
```

### Example: Upload Form

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

### Batch Upload

Upload multiple images:

```javascript
const images = [
  { url: 'https://example.com/img1.jpg', name: 'Image 1' },
  { url: 'https://example.com/img2.jpg', name: 'Image 2' },
  { url: 'https://example.com/img3.jpg', name: 'Image 3' }
];

const results = await Promise.all(
  images.map(img => uploadCustomImage(img.url, img.name))
);

console.log(`Uploaded ${results.length} images`);
```

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
