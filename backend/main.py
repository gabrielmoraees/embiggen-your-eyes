"""
Embiggen Your Eyes - MVP Backend
Simple FastAPI backend for NASA imagery visualization and annotation
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum
import uuid

app = FastAPI(title="Embiggen Your Eyes API", version="0.1.0")

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# DATA MODELS
# ============================================================================

class ImageLayer(str, Enum):
    """Available NASA GIBS layers"""
    TRUE_COLOR = "MODIS_Terra_CorrectedReflectance_TrueColor"
    FALSE_COLOR = "MODIS_Terra_CorrectedReflectance_Bands721"
    FIRES = "MODIS_Terra_Thermal_Anomalies_All"
    SNOW_COVER = "MODIS_Terra_Snow_Cover"
    CHLOROPHYLL = "MODIS_Terra_Chlorophyll_A"

class BoundingBox(BaseModel):
    north: float
    south: float
    east: float
    west: float

class ImageSearchQuery(BaseModel):
    layer: Optional[ImageLayer] = ImageLayer.TRUE_COLOR
    date_start: Optional[date] = None
    date_end: Optional[date] = None
    bbox: Optional[BoundingBox] = None
    limit: int = 50

class ImageMetadata(BaseModel):
    id: str
    layer: str
    date: date
    bbox: BoundingBox
    tile_url: str
    thumbnail_url: str
    description: Optional[str] = None

class AnnotationType(str, Enum):
    POINT = "point"
    POLYGON = "polygon"
    RECTANGLE = "rectangle"
    CIRCLE = "circle"
    TEXT = "text"

class Annotation(BaseModel):
    id: Optional[str] = None
    image_id: str
    type: AnnotationType
    coordinates: List[Dict[str, float]]  # [{"lat": x, "lng": y}, ...]
    properties: Dict[str, Any] = {}
    text: Optional[str] = None
    color: str = "#FF0000"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ImageLink(BaseModel):
    id: Optional[str] = None
    source_image_id: str
    target_image_id: str
    annotation_id: Optional[str] = None
    relationship_type: str  # e.g., "before_after", "same_location", "related_event"
    description: Optional[str] = None
    created_at: Optional[datetime] = None

class Collection(BaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    image_ids: List[str] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# ============================================================================
# IN-MEMORY STORAGE (for MVP - replace with DB in production)
# ============================================================================

annotations_db: Dict[str, Annotation] = {}
links_db: Dict[str, ImageLink] = {}
collections_db: Dict[str, Collection] = {}
search_history: List[ImageSearchQuery] = []

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def generate_gibs_url(layer: str, date: date, z: int, x: int, y: int) -> str:
    """Generate NASA GIBS tile URL"""
    date_str = date.strftime("%Y-%m-%d")
    return (
        f"https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/"
        f"{layer}/default/{date_str}/250m/{z}/{y}/{x}.jpg"
    )

def generate_thumbnail_url(layer: str, date: date) -> str:
    """Generate thumbnail URL (simplified)"""
    date_str = date.strftime("%Y-%m-%d")
    return (
        f"https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/"
        f"{layer}/default/{date_str}/250m/0/0/0.jpg"
    )

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Embiggen Your Eyes API",
        "version": "0.1.0"
    }

# ----------------------------------------------------------------------------
# SEARCH & DISCOVERY
# ----------------------------------------------------------------------------

@app.post("/api/search/images", response_model=List[ImageMetadata])
def search_images(query: ImageSearchQuery):
    """
    Search for NASA imagery based on criteria
    Returns metadata for matching images (tiles served by NASA GIBS)
    """
    results = []
    
    # Default date range if not specified
    date_start = query.date_start or date(2024, 1, 1)
    date_end = query.date_end or date.today()
    
    # For MVP, generate sample results
    # In production, query NASA CMR API or maintain an index
    current_date = date_start
    count = 0
    
    while current_date <= date_end and count < query.limit:
        image_id = f"{query.layer.value}_{current_date.isoformat()}"
        
        # Default bbox (global view)
        bbox = query.bbox or BoundingBox(north=90, south=-90, east=180, west=-180)
        
        results.append(ImageMetadata(
            id=image_id,
            layer=query.layer.value,
            date=current_date,
            bbox=bbox,
            tile_url=generate_gibs_url(query.layer.value, current_date, 0, 0, 0),
            thumbnail_url=generate_thumbnail_url(query.layer.value, current_date),
            description=f"{query.layer.value} imagery from {current_date}"
        ))
        
        # Skip to next week for MVP
        from datetime import timedelta
        current_date += timedelta(days=7)
        count += 1
    
    # Store search history
    search_history.append(query)
    
    return results

@app.get("/api/search/history")
def get_search_history():
    """Get recent search queries"""
    return search_history[-10:]  # Last 10 searches

@app.post("/api/images/compare")
def compare_images(image_ids: List[str]):
    """
    Prepare multiple images for side-by-side comparison
    Returns configuration for overlay/comparison view
    """
    if len(image_ids) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 images to compare")
    
    return {
        "comparison_id": str(uuid.uuid4()),
        "image_ids": image_ids,
        "comparison_modes": ["side-by-side", "overlay", "swipe", "difference"],
        "recommended_mode": "swipe" if len(image_ids) == 2 else "side-by-side"
    }

# ----------------------------------------------------------------------------
# ANNOTATIONS
# ----------------------------------------------------------------------------

@app.post("/api/annotations", response_model=Annotation)
def create_annotation(annotation: Annotation):
    """Create a new annotation on an image"""
    annotation.id = str(uuid.uuid4())
    annotation.created_at = datetime.now()
    annotation.updated_at = datetime.now()
    
    annotations_db[annotation.id] = annotation
    return annotation

@app.get("/api/annotations/image/{image_id}", response_model=List[Annotation])
def get_image_annotations(image_id: str):
    """Get all annotations for a specific image"""
    return [
        ann for ann in annotations_db.values()
        if ann.image_id == image_id
    ]

@app.put("/api/annotations/{annotation_id}", response_model=Annotation)
def update_annotation(annotation_id: str, annotation: Annotation):
    """Update an existing annotation"""
    if annotation_id not in annotations_db:
        raise HTTPException(status_code=404, detail="Annotation not found")
    
    annotation.id = annotation_id
    annotation.updated_at = datetime.now()
    annotations_db[annotation_id] = annotation
    return annotation

@app.delete("/api/annotations/{annotation_id}")
def delete_annotation(annotation_id: str):
    """Delete an annotation"""
    if annotation_id not in annotations_db:
        raise HTTPException(status_code=404, detail="Annotation not found")
    
    del annotations_db[annotation_id]
    return {"status": "deleted", "id": annotation_id}

# ----------------------------------------------------------------------------
# IMAGE LINKS & RELATIONSHIPS
# ----------------------------------------------------------------------------

@app.post("/api/links", response_model=ImageLink)
def create_link(link: ImageLink):
    """Create a link between two images"""
    link.id = str(uuid.uuid4())
    link.created_at = datetime.now()
    
    links_db[link.id] = link
    return link

@app.get("/api/links/image/{image_id}", response_model=List[ImageLink])
def get_image_links(image_id: str):
    """Get all links for an image (both source and target)"""
    return [
        link for link in links_db.values()
        if link.source_image_id == image_id or link.target_image_id == image_id
    ]

@app.delete("/api/links/{link_id}")
def delete_link(link_id: str):
    """Delete a link between images"""
    if link_id not in links_db:
        raise HTTPException(status_code=404, detail="Link not found")
    
    del links_db[link_id]
    return {"status": "deleted", "id": link_id}

@app.get("/api/links/graph/{image_id}")
def get_link_graph(image_id: str, depth: int = 2):
    """
    Get a graph of linked images starting from an image
    Useful for visualizing related image networks
    """
    def build_graph(current_id: str, current_depth: int, visited: set):
        if current_depth > depth or current_id in visited:
            return []
        
        visited.add(current_id)
        related = []
        
        for link in links_db.values():
            if link.source_image_id == current_id:
                related.append({
                    "link": link,
                    "target_image_id": link.target_image_id,
                    "children": build_graph(link.target_image_id, current_depth + 1, visited)
                })
            elif link.target_image_id == current_id:
                related.append({
                    "link": link,
                    "target_image_id": link.source_image_id,
                    "children": build_graph(link.source_image_id, current_depth + 1, visited)
                })
        
        return related
    
    graph = build_graph(image_id, 0, set())
    return {
        "root_image_id": image_id,
        "graph": graph,
        "total_nodes": len(set(link.source_image_id for link in links_db.values()) | 
                           set(link.target_image_id for link in links_db.values()))
    }

# ----------------------------------------------------------------------------
# COLLECTIONS (for organizing images)
# ----------------------------------------------------------------------------

@app.post("/api/collections", response_model=Collection)
def create_collection(collection: Collection):
    """Create a new collection of images"""
    collection.id = str(uuid.uuid4())
    collection.created_at = datetime.now()
    collection.updated_at = datetime.now()
    
    collections_db[collection.id] = collection
    return collection

@app.get("/api/collections", response_model=List[Collection])
def get_collections():
    """Get all collections"""
    return list(collections_db.values())

@app.get("/api/collections/{collection_id}", response_model=Collection)
def get_collection(collection_id: str):
    """Get a specific collection"""
    if collection_id not in collections_db:
        raise HTTPException(status_code=404, detail="Collection not found")
    return collections_db[collection_id]

@app.put("/api/collections/{collection_id}/images", response_model=Collection)
def add_images_to_collection(collection_id: str, image_ids: List[str]):
    """Add images to a collection"""
    if collection_id not in collections_db:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    collection = collections_db[collection_id]
    collection.image_ids.extend(image_ids)
    collection.image_ids = list(set(collection.image_ids))  # Remove duplicates
    collection.updated_at = datetime.now()
    
    return collection

@app.delete("/api/collections/{collection_id}")
def delete_collection(collection_id: str):
    """Delete a collection"""
    if collection_id not in collections_db:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    del collections_db[collection_id]
    return {"status": "deleted", "id": collection_id}

# ----------------------------------------------------------------------------
# SMART FEATURES
# ----------------------------------------------------------------------------

@app.get("/api/suggestions/similar/{image_id}")
def suggest_similar_images(image_id: str, limit: int = 5):
    """
    Suggest similar images based on location, date, or linked images
    (MVP: simple rule-based, can be enhanced with ML)
    """
    # Parse image_id to extract metadata
    parts = image_id.split("_")
    if len(parts) < 2:
        raise HTTPException(status_code=400, detail="Invalid image_id format")
    
    layer = "_".join(parts[:-1])
    date_str = parts[-1]
    
    suggestions = []
    
    # Suggest same location, different dates
    from datetime import timedelta, date as date_type
    try:
        base_date = date_type.fromisoformat(date_str)
        for days in [-7, -1, 1, 7]:
            new_date = base_date + timedelta(days=days)
            suggestions.append({
                "image_id": f"{layer}_{new_date.isoformat()}",
                "reason": f"{abs(days)} days {'before' if days < 0 else 'after'}",
                "confidence": 0.9
            })
    except ValueError:
        pass
    
    # Suggest linked images
    linked = get_image_links(image_id)
    for link in linked[:limit]:
        target_id = (link.target_image_id if link.source_image_id == image_id 
                    else link.source_image_id)
        suggestions.append({
            "image_id": target_id,
            "reason": f"Linked: {link.relationship_type}",
            "confidence": 0.95
        })
    
    return suggestions[:limit]

@app.get("/api/analytics/user-activity")
def get_user_activity():
    """Get user activity analytics"""
    return {
        "total_annotations": len(annotations_db),
        "total_links": len(links_db),
        "total_collections": len(collections_db),
        "total_searches": len(search_history),
        "most_annotated_images": _get_most_annotated_images(),
        "popular_layers": _get_popular_layers()
    }

def _get_most_annotated_images():
    """Helper to find most annotated images"""
    from collections import Counter
    image_counts = Counter(ann.image_id for ann in annotations_db.values())
    return [{"image_id": img_id, "count": count} 
            for img_id, count in image_counts.most_common(5)]

def _get_popular_layers():
    """Helper to find most searched layers"""
    from collections import Counter
    layer_counts = Counter(query.layer.value for query in search_history)
    return [{"layer": layer, "count": count} 
            for layer, count in layer_counts.most_common(5)]

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

