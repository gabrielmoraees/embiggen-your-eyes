# API Quick Reference

## 🚀 Quick Start

```bash
pip install -r requirements.txt
python main.py
# API Docs: http://localhost:8000/docs
```

## 📡 Endpoints

**Base URL:** `http://localhost:8000`

### Get Available Layers

```javascript
GET /api/layers

// Response
{
  "layers": [
    {
      "id": "VIIRS_TRUE_COLOR",
      "value": "VIIRS_SNPP_CorrectedReflectance_TrueColor",
      "display_name": "Viirs True Color",
      "satellite": "VIIRS SNPP",
      "type": "True Color (Natural)",
      "description": "VIIRS SNPP - True Color (Natural)"
    },
    // ... more layers
  ],
  "total": 4
}

// Usage in frontend
const response = await fetch('/api/layers');
const data = await response.json();

// Populate dropdown
data.layers.forEach(layer => {
  const option = document.createElement('option');
  option.value = layer.value;  // Use for search
  option.textContent = layer.description;  // Display to user
  select.appendChild(option);
});
```


### Search & Display

```javascript
POST /api/search/images
{
  "layer": "MODIS_Terra_CorrectedReflectance_TrueColor",
  "date_start": "2024-10-01",
  "date_end": "2024-10-04",
  "projection": "epsg3857",  // or "epsg4326"
  "limit": 10
}

// Response includes tile_url with {z}/{x}/{y} template
// Use directly with Leaflet/OpenLayers
L.tileLayer(image.tile_url, { maxZoom: image.max_zoom }).addTo(map);
```

### Annotations

```javascript
// 1. Create annotation
POST /api/annotations
{
  "image_id": "MODIS_Terra_..._2024-09-15",
  "type": "polygon",
  "coordinates": [
    {"lat": 40.7128, "lng": -74.0060},
    {"lat": 40.7580, "lng": -73.9855}
  ],
  "text": "Hurricane damage area",
  "color": "#FF0000"
}
→ Returns: Annotation with UUID

// 2. Get all annotations for an image
GET /api/annotations/image/{image_id}
→ Returns: Array of Annotations
```

### Image Links

```javascript
// 1. Create link between images
POST /api/links
{
  "source_image_id": "image_sept_1",
  "target_image_id": "image_sept_15",
  "relationship_type": "before_after",
  "description": "Hurricane progression"
}
→ Returns: Link with UUID

// 2. Get network graph
GET /api/links/graph/{image_id}?depth=2
→ Returns: Tree structure of all linked images
```

### Collections

```javascript
// 1. Create collection
POST /api/collections
{
  "name": "California Wildfires 2024",
  "description": "Monitoring wildfire spread",
  "image_ids": ["img1", "img2", "img3"]
}
→ Returns: Collection with UUID

// 2. Add more images
PUT /api/collections/{collection_id}/images
["img4", "img5"]
→ Returns: Updated Collection
```

### Image Comparison

```javascript
// 1. Prepare comparison
POST /api/images/compare
["image_A", "image_B", "image_C"]
→ Returns: Comparison config with modes

// 2. Frontend displays:
// - Side-by-side view
// - Overlay with opacity slider
// - Swipe comparison
// - Difference highlighting
```

## 🎯 Common Use Cases

### Use Case 1: Track Hurricane Path

```javascript
// Step 1: Search for images during hurricane season
const images = await fetch('/api/search/images', {
  method: 'POST',
  body: JSON.stringify({
    layer: 'MODIS_Terra_CorrectedReflectance_TrueColor',
    date_start: '2024-08-01',
    date_end: '2024-09-30',
    bbox: {
      north: 30, south: 20,
      east: -70, west: -90
    }
  })
});

// Step 2: Create annotations marking hurricane position
for (const [index, image] of images.entries()) {
  await fetch('/api/annotations', {
    method: 'POST',
    body: JSON.stringify({
      image_id: image.id,
      type: 'point',
      coordinates: [hurricanePositions[index]],
      text: `Day ${index + 1}`,
      properties: {
        wind_speed: windSpeeds[index],
        pressure: pressures[index]
      }
    })
  });
}

// Step 3: Link images in temporal sequence
for (let i = 0; i < images.length - 1; i++) {
  await fetch('/api/links', {
    method: 'POST',
    body: JSON.stringify({
      source_image_id: images[i].id,
      target_image_id: images[i + 1].id,
      relationship_type: 'temporal_sequence',
      description: 'Hurricane track progression'
    })
  });
}

// Step 4: Create collection
await fetch('/api/collections', {
  method: 'POST',
  body: JSON.stringify({
    name: 'Hurricane Maria Track',
    description: 'Daily progression from Aug 1 to Sept 30',
    image_ids: images.map(img => img.id)
  })
});

// Step 5: Get suggestions for related events
const suggestions = await fetch(`/api/suggestions/similar/${images[0].id}`);
// → Shows other hurricanes in same region/timeframe
```

### Use Case 2: Before/After Deforestation Analysis

```javascript
// Step 1: Search for images 1 year apart
const before = await searchImages({
  layer: 'MODIS_Terra_CorrectedReflectance_TrueColor',
  date_start: '2023-01-01',
  date_end: '2023-01-31',
  bbox: amazonRainforestBbox
});

const after = await searchImages({
  layer: 'MODIS_Terra_CorrectedReflectance_TrueColor',
  date_start: '2024-01-01',
  date_end: '2024-01-31',
  bbox: amazonRainforestBbox
});

// Step 2: Create link
await fetch('/api/links', {
  method: 'POST',
  body: JSON.stringify({
    source_image_id: before[0].id,
    target_image_id: after[0].id,
    relationship_type: 'before_after',
    description: 'One year deforestation comparison'
  })
});

// Step 3: Annotate deforested areas on 'after' image
await fetch('/api/annotations', {
  method: 'POST',
  body: JSON.stringify({
    image_id: after[0].id,
    type: 'polygon',
    coordinates: deforestedAreaPolygon,
    text: 'Deforested area: ~500 km²',
    color: '#FF0000',
    properties: {
      area_km2: 500,
      forest_loss_percentage: 15
    }
  })
});

// Step 4: Prepare comparison view
const comparison = await fetch('/api/images/compare', {
  method: 'POST',
  body: JSON.stringify([before[0].id, after[0].id])
});
// → Use swipe mode for dramatic before/after reveal
```

### Use Case 3: Multi-Spectral Analysis

```javascript
// Step 1: Search for different layers on same date
const trueColor = await searchImages({
  layer: 'MODIS_Terra_CorrectedReflectance_TrueColor',
  date_start: '2024-09-15',
  date_end: '2024-09-15'
});

const falseColor = await searchImages({
  layer: 'MODIS_Terra_CorrectedReflectance_Bands721',
  date_start: '2024-09-15',
  date_end: '2024-09-15'
});

const fires = await searchImages({
  layer: 'MODIS_Terra_Thermal_Anomalies_All',
  date_start: '2024-09-15',
  date_end: '2024-09-15'
});

// Step 2: Link all layers
await fetch('/api/links', {
  method: 'POST',
  body: JSON.stringify({
    source_image_id: trueColor[0].id,
    target_image_id: falseColor[0].id,
    relationship_type: 'same_location',
    description: 'Multi-spectral analysis'
  })
});

await fetch('/api/links', {
  method: 'POST',
  body: JSON.stringify({
    source_image_id: trueColor[0].id,
    target_image_id: fires[0].id,
    relationship_type: 'same_location',
    description: 'Thermal overlay'
  })
});

// Step 3: Create collection
await fetch('/api/collections', {
  method: 'POST',
  body: JSON.stringify({
    name: 'Wildfire Analysis - Sept 15, 2024',
    description: 'Multi-spectral view with thermal anomalies',
    image_ids: [trueColor[0].id, falseColor[0].id, fires[0].id]
  })
});

// Step 4: Annotate fire hotspots
const fireHotspots = detectFiresFromThermal(fires[0]);
for (const hotspot of fireHotspots) {
  await fetch('/api/annotations', {
    method: 'POST',
    body: JSON.stringify({
      image_id: fires[0].id,
      type: 'circle',
      coordinates: [hotspot.center],
      text: `Fire detected: ${hotspot.intensity}°C`,
      color: '#FF4500',
      properties: {
        temperature: hotspot.intensity,
        radius_km: hotspot.radius
      }
    })
  });
}
```

## 🎨 Available NASA GIBS Layers

```javascript
// True Color (RGB)
"MODIS_Terra_CorrectedReflectance_TrueColor"
// → Natural view, like a photograph

// False Color (useful for vegetation)
"MODIS_Terra_CorrectedReflectance_Bands721"
// → Vegetation appears bright green

// Fire Detection
"MODIS_Terra_Thermal_Anomalies_All"
// → Shows thermal hotspots

// Snow Cover
"MODIS_Terra_Snow_Cover"
// → Highlights snow and ice

// Chlorophyll (ocean productivity)
"MODIS_Terra_Chlorophyll_A"
// → Marine biology visualization
```

## 🔧 Frontend Integration Example (Leaflet)

```javascript
import L from 'leaflet';

// 1. Initialize map
const map = L.map('map').setView([0, 0], 2);

// 2. Search for images
const response = await fetch('http://localhost:8000/api/search/images', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    layer: 'MODIS_Terra_CorrectedReflectance_TrueColor',
    date_start: '2024-09-01',
    date_end: '2024-09-30',
    limit: 1
  })
});
const images = await response.json();

// 3. Add NASA GIBS layer directly to map
const layer = L.tileLayer(
  images[0].tile_url.replace('/0/0/0', '/{z}/{y}/{x}'),
  {
    maxZoom: 9,
    attribution: 'NASA GIBS'
  }
);
layer.addTo(map);

// 4. Load and display annotations
const annotationsResponse = await fetch(
  `http://localhost:8000/api/annotations/image/${images[0].id}`
);
const annotations = await annotationsResponse.json();

annotations.forEach(ann => {
  if (ann.type === 'polygon') {
    L.polygon(
      ann.coordinates.map(c => [c.lat, c.lng]),
      { color: ann.color }
    ).bindPopup(ann.text).addTo(map);
  } else if (ann.type === 'point') {
    L.marker([ann.coordinates[0].lat, ann.coordinates[0].lng])
      .bindPopup(ann.text)
      .addTo(map);
  }
});

// 5. Show suggestions
const suggestionsResponse = await fetch(
  `http://localhost:8000/api/suggestions/similar/${images[0].id}`
);
const suggestions = await suggestionsResponse.json();

console.log('You might also want to view:', suggestions);
```

## 📊 Response Examples

### Image Metadata
```json
{
  "id": "MODIS_Terra_CorrectedReflectance_TrueColor_2024-09-15",
  "layer": "MODIS_Terra_CorrectedReflectance_TrueColor",
  "date": "2024-09-15",
  "bbox": {
    "north": 90,
    "south": -90,
    "east": 180,
    "west": -180
  },
  "tile_url": "https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/2024-09-15/250m/{z}/{y}/{x}.jpg",
  "thumbnail_url": "...",
  "description": "MODIS_Terra_CorrectedReflectance_TrueColor imagery from 2024-09-15"
}
```

### Annotation
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "image_id": "MODIS_Terra_..._2024-09-15",
  "type": "polygon",
  "coordinates": [
    {"lat": 40.7128, "lng": -74.0060},
    {"lat": 40.7580, "lng": -73.9855},
    {"lat": 40.7489, "lng": -73.9680}
  ],
  "text": "Area of interest",
  "color": "#FF0000",
  "properties": {
    "category": "urban",
    "area_km2": 25.5
  },
  "created_at": "2024-10-04T12:00:00",
  "updated_at": "2024-10-04T12:00:00"
}
```

### Link Graph
```json
{
  "root_image_id": "image_A",
  "graph": [
    {
      "link": {
        "id": "link-1",
        "source_image_id": "image_A",
        "target_image_id": "image_B",
        "relationship_type": "before_after"
      },
      "target_image_id": "image_B",
      "children": [
        {
          "link": {...},
          "target_image_id": "image_C",
          "children": []
        }
      ]
    }
  ],
  "total_nodes": 3
}
```

## 🎯 Pro Tips

1. **Search Smart**: Use smaller date ranges for faster results
2. **Link Everything**: Create rich connections between related images
3. **Use Collections**: Organize images by project/event
4. **Annotate Richly**: Add metadata in `properties` for later analysis
5. **Leverage Suggestions**: Let the API guide you to related content
6. **Graph Navigation**: Use `depth` parameter to control how deep to search

## 🐛 Troubleshooting

```bash
# Server won't start?
pip install --upgrade fastapi uvicorn pydantic

# Can't connect from frontend?
# Check CORS settings in main.py

# No images returned?
# NASA GIBS has data from 2000-present
# Make sure date range is valid

# Annotations not showing?
# Check that image_id matches exactly
# Use GET /api/annotations/image/{id} to debug
```

## 📚 Next Steps

1. ✅ Start the backend: `python main.py`
2. ✅ Explore API docs: http://localhost:8000/docs
3. ✅ Run examples: `python example_usage.py`
4. ✅ Build your frontend!

Happy coding! 🚀

