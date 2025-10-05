# Async Image Processing

## Problem
Previously, when creating a dataset from an image URL, the POST endpoint would block while:
1. Downloading the entire image (could be gigabytes)
2. Generating all tile pyramids (could take minutes)

This resulted in very long HTTP request times and poor user experience.

## Solution
The dataset creation now works asynchronously:

1. **POST /api/datasets** returns immediately with:
   - `dataset_id`: The new dataset ID
   - `status: "processing"`: Indicates background processing
   - The dataset is created in the catalog right away

2. **Background Processing** happens in a separate thread:
   - Downloads the image
   - Generates tile pyramids
   - Updates the dataset status when complete

3. **GET /api/datasets/{dataset_id}/status** allows polling:
   - Shows current processing status
   - Returns progress information
   - Updates to `"ready"` when complete

## Usage Example

### 1. Create a dataset (returns immediately)
```bash
curl -X POST http://localhost:8000/api/datasets \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Space Image",
    "description": "High-res space photo",
    "category": "planets",
    "subject": "earth",
    "url": "https://example.com/large-image.jpg"
  }'
```

Response (immediate):
```json
{
  "success": true,
  "dataset_id": "custom_a1b2c3d4",
  "status": "processing",
  "message": "Dataset created, processing tiles"
}
```

### 2. Check processing status
```bash
curl http://localhost:8000/api/datasets/custom_a1b2c3d4/status
```

While processing:
```json
{
  "dataset_id": "custom_a1b2c3d4",
  "status": "processing",
  "progress": "generating_tiles",
  "started_at": "2025-10-05T14:30:00"
}
```

When complete:
```json
{
  "dataset_id": "custom_a1b2c3d4",
  "status": "ready",
  "tile_info": {
    "tile_id": "abc123...",
    "max_zoom": 8,
    "status": "completed"
  }
}
```

## Implementation Details

### Key Changes

1. **`dataset_service.py`**:
   - Changed `_create_image_dataset()` to call `queue_processing()` instead of `process_image()`
   - Returns immediately with `status: "processing"`
   - Creates dataset with placeholder tile URLs

2. **`tile_processor.py`**:
   - Added `queue_processing()`: Non-blocking method that starts background thread
   - Added `_process_image_background()`: Worker that does the actual processing
   - Added `_update_dataset_status()`: Updates dataset when processing completes
   - Kept `process_image()` for backward compatibility

3. **Background Thread**:
   - Uses Python's `threading` module
   - Daemon thread (won't block app shutdown)
   - Updates `processing_status` dict for status queries
   - Automatically updates dataset when complete

### Status Flow

```
POST /api/datasets
  ↓
Dataset created with status="processing"
  ↓
Background thread starts
  ↓
Status: "queued" → "processing" → "ready" (or "failed")
  ↓
Dataset tile URLs updated automatically
```

## Frontend Integration

The frontend should:

1. **On dataset creation**:
   - Show "Processing..." indicator
   - Store the `dataset_id`

2. **Poll for status**:
   ```javascript
   async function waitForDataset(datasetId) {
     while (true) {
       const status = await fetch(`/api/datasets/${datasetId}/status`);
       const data = await status.json();
       
       if (data.status === 'ready') {
         return data; // Processing complete!
       }
       
       if (data.status === 'failed') {
         throw new Error('Processing failed');
       }
       
       // Show progress if available
       console.log(`Progress: ${data.progress}`);
       
       // Wait before polling again
       await new Promise(r => setTimeout(r, 2000));
     }
   }
   ```

3. **Display progress**:
   - Show "Downloading..." when `progress: "downloading"`
   - Show "Generating tiles..." when `progress: "generating_tiles"`
   - Show success when `status: "ready"`

## Benefits

✅ **Instant response**: POST endpoint returns in milliseconds
✅ **Better UX**: Users get immediate feedback with dataset ID
✅ **Scalable**: Multiple images can process concurrently
✅ **Transparent**: Status endpoint shows real-time progress
✅ **Resilient**: Failed processing doesn't crash the API
✅ **Non-blocking**: Server can handle other requests while processing

## Testing

Run the test script:
```bash
cd backend
./test_async_dataset.sh
```

This will:
1. Create a dataset with a real image URL
2. Verify it returns immediately with "processing" status
3. Check the status endpoint
4. Show how to poll for completion
