# Embiggen Your Eyes - Backend MVP

A minimal backend API for NASA imagery visualization, annotation, and smart navigation.

## 🎯 Features

### Core Functionality
- **Search NASA Imagery**: Query NASA GIBS layers by date, location, and type
- **Smart Annotations**: Create, edit, and manage annotations on images
- **Image Links**: Create relationships between images (before/after, same location, etc.)
- **Collections**: Organize images into custom collections
- **Comparison Tools**: Prepare images for side-by-side comparison
- **Suggestions**: Get AI-suggested similar/related images

### UX-Focused Features
- **Graph Navigation**: Explore linked images as a network graph
- **Search History**: Track and revisit previous searches
- **Analytics**: View usage patterns and popular content
- **Fast API**: Minimal backend logic, NASA serves tiles directly

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip

### Installation

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

The API will be available at `http://localhost:8000`

### API Documentation
Once running, visit:
- **Interactive API docs**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc

## 📡 API Endpoints

### Search & Discovery
```
GET    /api/layers                   Get available NASA GIBS layers
POST   /api/search/images          Search for imagery
GET    /api/search/history          View search history
POST   /api/images/compare          Prepare images for comparison
GET    /api/suggestions/similar/{id} Get similar image suggestions
```

### Annotations
```
POST   /api/annotations             Create annotation
GET    /api/annotations/image/{id}  Get annotations for an image
PUT    /api/annotations/{id}        Update annotation
DELETE /api/annotations/{id}        Delete annotation
```

### Image Links
```
POST   /api/links                   Create link between images
GET    /api/links/image/{id}        Get links for an image
GET    /api/links/graph/{id}        Get network graph of linked images
DELETE /api/links/{id}              Delete link
```

### Collections
```
POST   /api/collections             Create collection
GET    /api/collections             List all collections
GET    /api/collections/{id}        Get specific collection
PUT    /api/collections/{id}/images Add images to collection
DELETE /api/collections/{id}        Delete collection
```

### Analytics
```
GET    /api/analytics/user-activity View usage statistics
```

## 🗂️ Data Models

### Image Search Query
```json
{
  "layer": "MODIS_Terra_CorrectedReflectance_TrueColor",
  "date_start": "2024-01-01",
  "date_end": "2024-10-01",
  "bbox": {
    "north": 45,
    "south": 35,
    "east": -100,
    "west": -110
  },
  "limit": 50
}
```

### Annotation
```json
{
  "image_id": "MODIS_Terra_..._2024-01-01",
  "type": "polygon",
  "coordinates": [
    {"lat": 40.7128, "lng": -74.0060},
    {"lat": 40.7580, "lng": -73.9855}
  ],
  "text": "Urban area expansion",
  "color": "#FF0000",
  "properties": {
    "category": "urban_growth",
    "confidence": 0.95
  }
}
```

### Image Link
```json
{
  "source_image_id": "image_2024-01-01",
  "target_image_id": "image_2024-06-01",
  "relationship_type": "before_after",
  "description": "Shows forest regrowth over 6 months"
}
```

## 🏗️ Architecture

```
┌─────────────────┐
│   Frontend      │
│  (React/Vue)    │
└────────┬────────┘
         │ HTTP/REST
┌────────▼────────┐
│  FastAPI        │
│  Backend (You)  │
│  - Annotations  │
│  - Links        │
│  - Collections  │
└────────┬────────┘
         │
    ┌────┴─────┬───────────┐
    │          │           │
┌───▼───┐  ┌───▼────┐  ┌──▼──────┐
│In-Mem │  │ NASA   │  │ NASA    │
│Storage│  │ GIBS   │  │ CMR API │
│(MVP)  │  │(Tiles) │  │(Search) │
└───────┘  └────────┘  └─────────┘
```

### Why This Architecture?

**✅ For MVP:**
- In-memory storage (fast, simple, no DB setup)
- NASA serves all tiles directly (no tile processing needed)
- Focus on UX features, not infrastructure

**🔄 For Production:**
- Replace in-memory dicts with PostgreSQL/MongoDB
- Add authentication (JWT tokens)
- Implement caching layer (Redis)
- Add rate limiting

## 🎨 Available NASA GIBS Layers

```python
TRUE_COLOR = "MODIS_Terra_CorrectedReflectance_TrueColor"
FALSE_COLOR = "MODIS_Terra_CorrectedReflectance_Bands721"
FIRES = "MODIS_Terra_Thermal_Anomalies_All"
SNOW_COVER = "MODIS_Terra_Snow_Cover"
CHLOROPHYLL = "MODIS_Terra_Chlorophyll_A"
```

More layers available at: https://worldview.earthdata.nasa.gov/

## 🧪 Testing the API

### Using curl
```bash
# Health check
curl http://localhost:8000/

# Search for images
curl -X POST http://localhost:8000/api/search/images \
  -H "Content-Type: application/json" \
  -d '{
    "layer": "MODIS_Terra_CorrectedReflectance_TrueColor",
    "date_start": "2024-01-01",
    "date_end": "2024-03-01",
    "limit": 10
  }'

# Create annotation
curl -X POST http://localhost:8000/api/annotations \
  -H "Content-Type: application/json" \
  -d '{
    "image_id": "test_image_123",
    "type": "point",
    "coordinates": [{"lat": 40.7128, "lng": -74.0060}],
    "text": "Test annotation",
    "color": "#FF0000"
  }'
```

### Using Python
```python
import requests

# Search images
response = requests.post("http://localhost:8000/api/search/images", json={
    "layer": "MODIS_Terra_CorrectedReflectance_TrueColor",
    "date_start": "2024-01-01",
    "date_end": "2024-03-01",
    "limit": 10
})
images = response.json()

# Create annotation
response = requests.post("http://localhost:8000/api/annotations", json={
    "image_id": images[0]["id"],
    "type": "polygon",
    "coordinates": [
        {"lat": 40.7128, "lng": -74.0060},
        {"lat": 40.7580, "lng": -73.9855}
    ],
    "text": "Area of interest"
})
annotation = response.json()
```

## 🚀 Next Steps for Production

1. **Add Database**: Replace in-memory storage with PostgreSQL
   ```bash
   pip install sqlalchemy psycopg2-binary
   ```

2. **Add Authentication**: Implement JWT-based auth
   ```bash
   pip install python-jose[cryptography] passlib[bcrypt]
   ```

3. **Add Caching**: Implement Redis for performance
   ```bash
   pip install redis
   ```

4. **Add Testing**: Write unit tests
   ```bash
   pip install pytest pytest-asyncio httpx
   ```

5. **Deploy**: Use Docker for containerization
   ```dockerfile
   FROM python:3.9
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

## 📝 Notes

- **MVP Focus**: This backend prioritizes speed and simplicity for hackathon development
- **No Database**: All data stored in-memory (lost on restart) - fine for demo
- **NASA GIBS**: Tiles are served directly by NASA, we just provide tile URLs
- **CORS**: Currently allows all origins - restrict in production
- **No Auth**: No user authentication - add for production

## 🤝 Contributing

For the NASA Space Apps Challenge, focus on:
1. Improving smart suggestions algorithm
2. Adding more annotation types
3. Enhancing the link graph visualization
4. Implementing ML-based image similarity

## 📄 License

See LICENSE file in root directory.

