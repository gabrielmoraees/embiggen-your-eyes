# Backend Architecture - MVP

## 🎯 Design Philosophy

**Keep it Simple, Focus on UX**

This MVP backend is intentionally minimal - it handles only what NASA doesn't provide:
- User-generated content (annotations, links, collections)
- Smart features (suggestions, graph navigation)
- Search orchestration

NASA handles the heavy lifting:
- Tile storage and serving
- Image processing
- Global infrastructure

## 📐 Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (Your UI)                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │  Search  │  │   Map    │  │Annotate │  │Compare  │ │
│  │Interface │  │  Viewer  │  │  Tools  │  │  View   │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬────┘ │
│       │             │              │             │      │
└───────┼─────────────┼──────────────┼─────────────┼──────┘
        │             │              │             │
        │ REST API    │ Direct       │ REST API    │ REST API
        │             │ Tile Request │             │
┌───────▼─────────────┼──────────────▼─────────────▼──────┐
│                     │     YOUR BACKEND (FastAPI)        │
│  ┌──────────────┐   │   ┌────────────┐  ┌─────────────┐│
│  │   Search     │   │   │Annotations │  │   Links     ││
│  │  Endpoint    │   │   │  Manager   │  │   Manager   ││
│  └──────────────┘   │   └────────────┘  └─────────────┘│
│  ┌──────────────┐   │   ┌────────────┐  ┌─────────────┐│
│  │ Collections  │   │   │Suggestions │  │  Analytics  ││
│  │   Manager    │   │   │   Engine   │  │   Service   ││
│  └──────────────┘   │   └────────────┘  └─────────────┘│
│         │           │          │               │        │
│         └───────────┼──────────┴───────────────┘        │
│                     │          │                        │
│         ┌───────────▼──────────▼─────────────┐          │
│         │    In-Memory Storage (MVP)         │          │
│         │  - annotations_db: Dict            │          │
│         │  - links_db: Dict                  │          │
│         │  - collections_db: Dict            │          │
│         │  - search_history: List            │          │
│         └────────────────────────────────────┘          │
└───────────────────────┬─────────────────────────────────┘
                        │
        ┌───────────────┴────────────────┐
        │                                │
┌───────▼────────┐              ┌────────▼────────┐
│   NASA GIBS    │              │   NASA CMR      │
│  Tile Service  │              │  Search API     │
│                │              │                 │
│ - Pre-rendered │              │ - Image metadata│
│   tiles        │              │ - Spatial query │
│ - Multiple     │              │ - Temporal query│
│   layers       │              │                 │
│ - Daily updates│              │                 │
└────────────────┘              └─────────────────┘
```

## 🔄 Data Flow Examples

### 1. Search & Display Images

```
User searches for "fires in California, Sept 2024"
    │
    ▼
Frontend sends POST /api/search/images
    │
    ▼
Backend processes query:
  - Parses date range
  - Sets layer to "FIRES"
  - Sets bounding box for California
    │
    ▼
Backend generates image metadata with NASA GIBS URLs
    │
    ▼
Frontend receives list of images
    │
    ▼
Frontend directly requests tiles from NASA GIBS
  (Backend never touches actual image data)
    │
    ▼
Map displays imagery
```

### 2. Create Annotation

```
User draws polygon on map
    │
    ▼
Frontend sends POST /api/annotations
    │
    ▼
Backend:
  - Generates UUID
  - Stores in annotations_db
  - Returns annotation object
    │
    ▼
Frontend displays annotation on map
```

### 3. Link Images (Before/After)

```
User views Image A (2024-01-01)
    │
    ▼
Backend suggests similar images via /api/suggestions/similar/{id}
    │
    ▼
User selects Image B (2024-06-01) to link
    │
    ▼
Frontend sends POST /api/links
    │
    ▼
Backend creates link:
  - source: Image A
  - target: Image B
  - type: "before_after"
    │
    ▼
User clicks "Show linked images"
    │
    ▼
Frontend requests GET /api/links/graph/{id}
    │
    ▼
Backend builds graph of all linked images (depth=2)
    │
    ▼
Frontend displays network visualization
```

### 4. Smart Suggestions

```
User views Image X
    │
    ▼
Frontend requests GET /api/suggestions/similar/{id}
    │
    ▼
Backend analyzes:
  ┌─────────────────────────────────────┐
  │ Rule-based suggestions (MVP):       │
  │ 1. Same location, ±7 days           │
  │ 2. Same location, ±1 month          │
  │ 3. Linked images from graph         │
  │ 4. Images in same collection        │
  └─────────────────────────────────────┘
    │
    ▼
Returns ranked suggestions
    │
    ▼
Frontend displays "You might also want to view..."
```

## 📦 Data Models

### In-Memory Storage Structure

```python
# Annotations: User-drawn shapes and notes
annotations_db = {
    "uuid-1": {
        "id": "uuid-1",
        "image_id": "MODIS_Terra_..._2024-01-01",
        "type": "polygon",
        "coordinates": [...],
        "text": "Deforestation area",
        "color": "#FF0000",
        "properties": {"area_km2": 150}
    }
}

# Links: Relationships between images
links_db = {
    "uuid-2": {
        "id": "uuid-2",
        "source_image_id": "image_A",
        "target_image_id": "image_B",
        "relationship_type": "before_after",
        "description": "Shows forest regrowth"
    }
}

# Collections: Organized image sets
collections_db = {
    "uuid-3": {
        "id": "uuid-3",
        "name": "Amazon Deforestation 2024",
        "image_ids": ["img1", "img2", "img3"]
    }
}

# Search History: User search patterns
search_history = [
    {
        "layer": "TRUE_COLOR",
        "date_start": "2024-01-01",
        "bbox": {...}
    }
]
```

## 🎨 Key Features Explained

### 1. **Annotations** - Draw on images
- Types: point, polygon, rectangle, circle, text
- Properties: color, text, custom metadata
- Use cases: Mark areas of interest, add notes, highlight changes

### 2. **Links** - Connect related images
- Types: before_after, same_location, related_event, comparison
- Graph navigation: Explore image networks
- Use cases: Time series, change detection, storytelling

### 3. **Collections** - Organize images
- Like playlists for images
- Share with team
- Use cases: Project organization, presentations, monitoring

### 4. **Smart Suggestions** - AI-assisted discovery
- Time-based: Same place, different dates
- Link-based: Follow annotation connections
- Pattern-based: Similar viewing patterns
- Use cases: Guided exploration, serendipitous discovery

### 5. **Comparison Tools** - Side-by-side analysis
- Modes: side-by-side, overlay, swipe, difference
- Sync navigation
- Use cases: Change detection, before/after, multi-spectral

## ⚡ Performance Considerations

### What Makes This Fast

1. **No Image Processing**
   - NASA handles tile generation
   - We only serve metadata (KB, not GB)
   - Response times: <50ms

2. **In-Memory Storage**
   - Dict lookups: O(1)
   - No database overhead
   - Perfect for hackathon demo

3. **Direct Tile Access**
   - Frontend requests tiles from NASA
   - No proxy overhead
   - Leverages NASA's CDN

4. **Minimal Business Logic**
   - Simple CRUD operations
   - Basic graph traversal
   - Rule-based suggestions

### What Would Need Optimization (Production)

1. **Database Migration**
   - PostgreSQL for persistence
   - Indexes on image_id, dates
   - Full-text search on annotations

2. **Caching Layer**
   - Redis for frequent queries
   - Cache suggestion results
   - Store search results

3. **Async Processing**
   - Queue for heavy computations
   - Background jobs for ML inference
   - Batch processing for analytics

## 🔮 Future Enhancements (Post-MVP)

### Phase 2: Smart Features
```python
# ML-based suggestions
def suggest_similar_images_ml(image_id):
    # Use image embeddings (ResNet, CLIP)
    # Vector similarity search
    # Return visually similar images
    pass

# Automated annotation
def auto_annotate_features(image_id):
    # Run object detection (ships, buildings, etc.)
    # Create annotations automatically
    # User can review and edit
    pass
```

### Phase 3: Collaboration
```python
# Multi-user support
class User:
    id: str
    annotations: List[str]
    collections: List[str]

# Real-time collaboration
# WebSocket for live annotation updates
# Shared viewing sessions
```

### Phase 4: Analytics
```python
# Advanced analytics
def analyze_temporal_changes(image_ids):
    # Detect changes over time
    # Generate insights
    # Create visualizations
    pass
```

## 🛠️ Technology Choices

| Component | Choice | Why |
|-----------|--------|-----|
| **Framework** | FastAPI | Fast, modern, auto-docs, async support |
| **Data Validation** | Pydantic | Type safety, validation, serialization |
| **Storage (MVP)** | In-memory Dict | Simple, fast, no setup |
| **Storage (Prod)** | PostgreSQL + PostGIS | Spatial queries, reliability |
| **API Style** | REST | Standard, easy to consume |
| **Docs** | OpenAPI/Swagger | Auto-generated, interactive |

## 📊 Scalability Path

### MVP (Now) → 100 users
- In-memory storage
- Single server
- No auth
- **Cost: $0 (local dev)**

### Phase 1 → 1,000 users
- PostgreSQL database
- Basic auth (JWT)
- Heroku/Railway deployment
- **Cost: ~$10/month**

### Phase 2 → 10,000 users
- PostgreSQL + Redis
- Load balancer
- Multiple servers
- AWS/GCP deployment
- **Cost: ~$100/month**

### Phase 3 → 100,000 users
- Database replication
- Microservices
- Kubernetes
- CDN for API
- **Cost: ~$1,000/month**

## 🎯 Success Metrics (MVP)

Focus on these for the hackathon:

1. **Search Speed**: < 100ms response time
2. **Annotation UX**: Create annotation in < 5 clicks
3. **Link Creation**: Link images in < 3 clicks
4. **Smart Suggestions**: Show 5 relevant suggestions
5. **Graph Navigation**: Display link graph in < 1 second

## 📝 Summary

This backend is **intentionally minimal** because:

✅ NASA provides the hard parts (tiles, storage, processing)  
✅ Focus is on UX features (annotations, links, navigation)  
✅ Simple = fast development = more time for frontend polish  
✅ In-memory storage = perfect for demo/hackathon  

The value-add is in the **smart features** and **user experience**, not in rebuilding NASA's infrastructure!

