"""
Embiggen Your Eyes - MVP Backend
Simple FastAPI backend for NASA imagery visualization and annotation
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum
from pathlib import Path
import uuid
import asyncio
import hashlib

# Import tile processor
from tile_processor import tile_processor

app = FastAPI(title="Embiggen Your Eyes API", version="0.1.0")

# Mount static tiles directory
tiles_cache_path = Path("./tiles_cache")
tiles_cache_path.mkdir(exist_ok=True)
app.mount("/tiles", StaticFiles(directory=str(tiles_cache_path)), name="tiles")

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

class CelestialBody(str, Enum):
    """Available celestial bodies"""
    EARTH = "earth"
    MARS = "mars"
    MOON = "moon"
    MERCURY = "mercury"
    DEEP_SPACE = "deep_space"  # Pre-curated galaxies, nebulae, star clusters
    CUSTOM = "custom"  # User-uploaded custom gigapixel images

class ImageLayer(str, Enum):
    """Available imagery layers for all celestial bodies"""
    # Earth (NASA GIBS)
    VIIRS_TRUE_COLOR = "VIIRS_SNPP_CorrectedReflectance_TrueColor"
    VIIRS_FALSE_COLOR = "VIIRS_SNPP_CorrectedReflectance_BandsM11-I2-I1"
    MODIS_TERRA_TRUE_COLOR = "MODIS_Terra_CorrectedReflectance_TrueColor"
    MODIS_TERRA_FALSE_COLOR = "MODIS_Terra_CorrectedReflectance_Bands721"
    
    # Mars (Multiple sources)
    MARS_VIKING_COLOR = "Mars_Viking_MDIM21_ClrMosaic_global_232m"  # NASA Trek
    MARS_BASEMAP_OPM = "opm_mars_basemap"  # OpenPlanetaryMap
    
    # Moon (Public tile services)
    MOON_BASEMAP_OPM = "opm_moon_basemap"  # OpenPlanetaryMap
    MOON_BASEMAP_ARCGIS = "arcgis_moon_basemap"  # ESRI ArcGIS
    
    # Mercury (OpenPlanetaryMap)
    MERCURY_BASEMAP_OPM = "opm_mercury_basemap"
    
    # Deep Space (Pre-tiled gigapixel images only)
    GALAXY_ANDROMEDA_GIGAPIXEL = "andromeda_gigapixel"  # 1.5 GP pre-tiled
    # Add more pre-tiled gigapixel layers here
    
    # Custom (dynamically added by users - no predefined layers)

class BoundingBox(BaseModel):
    north: float
    south: float
    east: float
    west: float

class ImageSearchQuery(BaseModel):
    celestial_body: CelestialBody = CelestialBody.EARTH
    layer: Optional[str] = None  # Can be ImageLayer enum value or custom layer ID
    date_start: Optional[date] = None
    date_end: Optional[date] = None
    bbox: Optional[BoundingBox] = None
    projection: str = "epsg3857"  # epsg3857 (Web Mercator) or epsg4326 (Geographic)
    limit: int = 50

class ImageMetadata(BaseModel):
    id: str
    layer: str
    date: date
    bbox: BoundingBox
    tile_url: str  # Template URL with {z}/{x}/{y} placeholders
    thumbnail_url: str
    projection: str = "epsg3857"
    max_zoom: int = 9
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

# Deep Space Objects Catalog (Pre-curated, Pre-tiled Only)
# Curated collection of pre-tiled gigapixel images from galaxies, nebulae, and star clusters
# All entries must have tile_url_template (instant access, no processing)
# For images that need processing, use the Custom celestial body instead
DEEP_SPACE_CATALOG = {
    "andromeda_gigapixel": {
        "name": "Andromeda Galaxy (M31) - 1.5 Gigapixel",
        "type": "Spiral Galaxy",
        "distance": "2.5 million light-years",
        "telescope": "Hubble Space Telescope",
        "tile_url_template": "https://tile{s}.gigapan.com/gigapans0/48492/tiles/{z}_{x}_{y}.jpg",
        "tile_subdomains": ["0", "1", "2", "3"],
        "max_zoom": 12,
        "ra": 10.684,
        "dec": 41.269,
        "description": "1.5 gigapixel mosaic of our nearest major galactic neighbor",
        "attribution": "NASA/ESA Hubble Space Telescope via Gigapan"
    }
    # Add more pre-tiled gigapixel images here
    # For non-pre-tiled images, use the Custom celestial body
}

# Custom Images Catalog (User-uploaded)
# Dynamically populated when users upload custom gigapixel images
# All custom images are processed on-demand into tiles
CUSTOM_IMAGES_CATALOG: Dict[str, Dict[str, Any]] = {}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def generate_tile_url_template(
    celestial_body: CelestialBody, 
    layer: str, 
    date: date, 
    projection: str = "epsg3857"
) -> str:
    """
    Generate tile URL template for any celestial body
    The {z}/{x}/{y} placeholders will be replaced by the mapping library
    
    Supports:
    - Earth: NASA GIBS (time-series data)
    - Mars: NASA Trek (static mosaics)
    - Moon: NASA Trek (static mosaics)
    """
    
    # Earth - use NASA GIBS
    if celestial_body == CelestialBody.EARTH:
        date_str = date.strftime("%Y-%m-%d")
        tile_matrix = "GoogleMapsCompatible_Level9" if projection == "epsg3857" else "250m"
        return (
            f"https://gibs.earthdata.nasa.gov/wmts/{projection}/best/"
            f"{layer}/default/{date_str}/{tile_matrix}/{{z}}/{{y}}/{{x}}.jpg"
        )
    
    # Mars - multiple sources
    elif celestial_body == CelestialBody.MARS:
        if layer == "opm_mars_basemap":
            # OpenPlanetaryMap Mars basemap
            return "https://cartocdn-gusc.global.ssl.fastly.net/opmbuilder/api/v1/map/named/opm-mars-basemap-v0-2/all/{z}/{x}/{y}.png"
        else:
            # NASA Trek WMTS format (Viking)
            return (
                f"https://trek.nasa.gov/tiles/Mars/EQ/{layer}/1.0.0/"
                f"default/default028mm/{{z}}/{{y}}/{{x}}.jpg"
            )
    
    # Moon - use public tile services
    elif celestial_body == CelestialBody.MOON:
        if layer == "opm_moon_basemap":
            # OpenPlanetaryMap Moon basemap
            return "https://cartocdn-gusc.global.ssl.fastly.net/opmbuilder/api/v1/map/named/opm-moon-basemap-v0-1/all/{z}/{x}/{y}.png"
        elif layer == "arcgis_moon_basemap":
            # ESRI ArcGIS Moon basemap
            return "https://tiles.arcgis.com/tiles/WQ9KVmV6xGGMnCiQ/arcgis/rest/services/Moon_Basemap/MapServer/tile/{z}/{y}/{x}"
        else:
            raise ValueError(f"Unknown Moon layer: {layer}")
    
    # Mercury - OpenPlanetaryMap
    elif celestial_body == CelestialBody.MERCURY:
        if layer == "opm_mercury_basemap":
            return "https://cartocdn-gusc.global.ssl.fastly.net/opmbuilder/api/v1/map/named/opm-mercury-basemap-v0-1/all/{z}/{x}/{y}.png"
        else:
            raise ValueError(f"Unknown Mercury layer: {layer}")
    
    # Deep Space - pre-curated galaxies and nebulae (pre-tiled only)
    elif celestial_body == CelestialBody.DEEP_SPACE:
        if layer not in DEEP_SPACE_CATALOG:
            raise ValueError(f"Unknown deep space object: {layer}")
        
        obj = DEEP_SPACE_CATALOG[layer]
        
        # Deep Space only supports pre-tiled gigapixel images (instant access)
        if "tile_url_template" in obj:
            # Return the pre-existing tile URL template
            # Note: {s} subdomain placeholder will be handled by frontend
            return obj["tile_url_template"].replace("{s}", "0")  # Default to subdomain 0
        else:
            raise ValueError(f"Deep space object {layer} must be pre-tiled. Use custom celestial body for processing images.")
    
    # Custom - user-uploaded gigapixel images
    elif celestial_body == CelestialBody.CUSTOM:
        if layer not in CUSTOM_IMAGES_CATALOG:
            raise ValueError(f"Unknown custom image: {layer}")
        
        obj = CUSTOM_IMAGES_CATALOG[layer]
        image_url = obj["image_url"]
        
        # Check if tiles are ready
        if tile_processor.is_tiled(image_url):
            # Return tile URL template
            return tile_processor.get_tile_url_template(image_url)
        else:
            # Tiles not ready - return placeholder
            return f"/api/tile-placeholder/{layer}"
    
    raise ValueError(f"Unsupported celestial body: {celestial_body}")

def generate_thumbnail_url(
    celestial_body: CelestialBody,
    layer: str, 
    date: date, 
    projection: str = "epsg3857"
) -> str:
    """Generate thumbnail URL at zoom level 0"""
    
    # Earth - use GIBS
    if celestial_body == CelestialBody.EARTH:
        date_str = date.strftime("%Y-%m-%d")
        tile_matrix = "GoogleMapsCompatible_Level9" if projection == "epsg3857" else "250m"
        return (
            f"https://gibs.earthdata.nasa.gov/wmts/{projection}/best/"
            f"{layer}/default/{date_str}/{tile_matrix}/0/0/0.jpg"
        )
    
    # Mars - multiple sources
    elif celestial_body == CelestialBody.MARS:
        if layer == "opm_mars_basemap":
            return "https://cartocdn-gusc.global.ssl.fastly.net/opmbuilder/api/v1/map/named/opm-mars-basemap-v0-2/all/0/0/0.png"
        else:
            return (
                f"https://trek.nasa.gov/tiles/Mars/EQ/{layer}/1.0.0/"
                f"default/default028mm/0/0/0.jpg"
            )
    
    # Moon - public tile services
    elif celestial_body == CelestialBody.MOON:
        if layer == "opm_moon_basemap":
            return "https://cartocdn-gusc.global.ssl.fastly.net/opmbuilder/api/v1/map/named/opm-moon-basemap-v0-1/all/0/0/0.png"
        elif layer == "arcgis_moon_basemap":
            return "https://tiles.arcgis.com/tiles/WQ9KVmV6xGGMnCiQ/arcgis/rest/services/Moon_Basemap/MapServer/tile/0/0/0"
        else:
            raise ValueError(f"Unknown Moon layer: {layer}")
    
    # Mercury - OpenPlanetaryMap
    elif celestial_body == CelestialBody.MERCURY:
        if layer == "opm_mercury_basemap":
            return "https://cartocdn-gusc.global.ssl.fastly.net/opmbuilder/api/v1/map/named/opm-mercury-basemap-v0-1/all/0/0/0.png"
        else:
            raise ValueError(f"Unknown Mercury layer: {layer}")
    
    # Deep Space - use tile at zoom 0 as thumbnail (pre-tiled only)
    elif celestial_body == CelestialBody.DEEP_SPACE:
        if layer not in DEEP_SPACE_CATALOG:
            raise ValueError(f"Unknown deep space object: {layer}")
        
        obj = DEEP_SPACE_CATALOG[layer]
        
        # Deep Space only supports pre-tiled gigapixel images
        if "tile_url_template" in obj:
            # Use zoom 0 tile from pre-tiled source
            return obj["tile_url_template"].replace("{s}", "0").replace("{z}", "0").replace("{x}", "0").replace("{y}", "0")
        else:
            raise ValueError(f"Deep space object {layer} must be pre-tiled. Use custom celestial body for processing images.")
    
    # Custom - user-uploaded images
    elif celestial_body == CelestialBody.CUSTOM:
        if layer not in CUSTOM_IMAGES_CATALOG:
            raise ValueError(f"Unknown custom image: {layer}")
        
        obj = CUSTOM_IMAGES_CATALOG[layer]
        image_url = obj["image_url"]
        
        # If tiles exist, use zoom 0 tile as thumbnail
        if tile_processor.is_tiled(image_url):
            tile_id = tile_processor._generate_tile_id(image_url)
            return f"/tiles/{tile_id}/0/0/0.png"
        else:
            # Tiles not ready - return placeholder
            return f"/api/tile-placeholder/{layer}"
    
    raise ValueError(f"Unsupported celestial body: {celestial_body}")

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Embiggen Your Eyes API",
        "version": "0.1.0",
        "tile_processor": "enabled"
    }

# ----------------------------------------------------------------------------
# TILE PROCESSING ENDPOINTS
# ----------------------------------------------------------------------------

@app.get("/api/tile-status/{layer}")
def get_tile_status(layer: str):
    """
    Check if tiles are ready for a deep space object
    Returns processing status: not_started, processing, completed, failed
    
    All deep space objects use tiles - no exceptions
    """
    if layer not in DEEP_SPACE_CATALOG:
        raise HTTPException(status_code=404, detail="Layer not found")
    
    obj = DEEP_SPACE_CATALOG[layer]
    image_url = obj["image_url"]
    status = tile_processor.get_processing_status(image_url)
    
    return {
        "layer": layer,
        "status": status.get("status", "not_started"),
        "tile_info": status if status.get("status") == "completed" else None
    }

@app.post("/api/process-tiles/{layer}")
async def trigger_tile_processing(layer: str, background_tasks: BackgroundTasks):
    """
    Trigger tile processing for a deep space object
    Processing happens in background
    
    Only works for custom images (not pre-tiled gigapixel images)
    """
    if layer not in DEEP_SPACE_CATALOG:
        raise HTTPException(status_code=404, detail="Layer not found")
    
    obj = DEEP_SPACE_CATALOG[layer]
    
    # Check if it's a pre-tiled image
    if "tile_url_template" in obj:
        raise HTTPException(status_code=400, detail="This layer uses pre-tiled gigapixel images. No processing needed.")
    
    if "image_url" not in obj:
        raise HTTPException(status_code=400, detail="Layer has no image URL to process")
    
    image_url = obj["image_url"]
    
    # Check if already processed or processing
    if tile_processor.is_tiled(image_url):
        return {
            "message": "Tiles already exist",
            "status": "completed",
            "layer": layer
        }
    
    status = tile_processor.get_processing_status(image_url)
    if status.get("status") == "processing":
        return {
            "message": "Processing already in progress",
            "status": "processing",
            "layer": layer
        }
    
    # Trigger background processing
    def process_in_background():
        try:
            tile_processor.process_image(image_url, obj)
        except Exception as e:
            print(f"Tile processing failed for {layer}: {e}")
    
    background_tasks.add_task(process_in_background)
    
    return {
        "message": "Tile processing started",
        "status": "processing",
        "layer": layer,
        "check_status_url": f"/api/tile-status/{layer}"
    }

class CustomImageRequest(BaseModel):
    """Request to add a custom gigapixel image"""
    name: str
    image_url: str
    description: Optional[str] = None
    type: Optional[str] = "Custom Image"
    telescope: Optional[str] = "Unknown"
    distance: Optional[str] = "Unknown"
    ra: Optional[float] = 0.0
    dec: Optional[float] = 0.0
    max_zoom: Optional[int] = 8

@app.post("/api/custom-image")
async def add_custom_image(request: CustomImageRequest, background_tasks: BackgroundTasks):
    """
    Add a custom gigapixel image from any URL
    The image will be downloaded and converted to tiles automatically
    
    Custom images are stored separately from pre-curated deep space objects
    """
    # Generate a unique layer ID
    layer_id = f"custom_{hashlib.md5(request.image_url.encode()).hexdigest()[:12]}"
    
    # Check if already exists in custom catalog
    if layer_id in CUSTOM_IMAGES_CATALOG:
        return {
            "message": "Image already added",
            "layer_id": layer_id,
            "status": "exists",
            "celestial_body": "custom"
        }
    
    # Add to custom images catalog
    CUSTOM_IMAGES_CATALOG[layer_id] = {
        "name": request.name,
        "type": request.type,
        "distance": request.distance,
        "telescope": request.telescope,
        "image_url": request.image_url,
        "ra": request.ra,
        "dec": request.dec,
        "description": request.description or f"Custom image: {request.name}",
        "max_zoom_tiling": request.max_zoom
    }
    
    # Trigger background processing
    def process_in_background():
        try:
            tile_processor.process_image(request.image_url, CUSTOM_IMAGES_CATALOG[layer_id])
        except Exception as e:
            print(f"Tile processing failed for custom image {layer_id}: {e}")
    
    background_tasks.add_task(process_in_background)
    
    return {
        "message": "Custom image added and processing started",
        "layer_id": layer_id,
        "celestial_body": "custom",
        "status": "processing",
        "check_status_url": f"/api/tile-status-by-url?url={request.image_url}",
        "search_query": {
            "celestial_body": "custom",
            "layer": layer_id
        }
    }

# ----------------------------------------------------------------------------
@app.get("/api/layers")
def get_available_layers(celestial_body: Optional[CelestialBody] = None):
    """
    Get list of available imagery layers, optionally filtered by celestial body
    Returns layer information including name, value, celestial body, and description
    """
    
    # Define layer metadata
    layer_info = {
        # Earth layers
        ImageLayer.VIIRS_TRUE_COLOR: {
            "celestial_body": CelestialBody.EARTH,
            "satellite": "VIIRS SNPP",
            "type": "True Color"
        },
        ImageLayer.VIIRS_FALSE_COLOR: {
            "celestial_body": CelestialBody.EARTH,
            "satellite": "VIIRS SNPP",
            "type": "False Color"
        },
        ImageLayer.MODIS_TERRA_TRUE_COLOR: {
            "celestial_body": CelestialBody.EARTH,
            "satellite": "MODIS Terra",
            "type": "True Color"
        },
        ImageLayer.MODIS_TERRA_FALSE_COLOR: {
            "celestial_body": CelestialBody.EARTH,
            "satellite": "MODIS Terra",
            "type": "False Color"
        },
        # Mars layers
        ImageLayer.MARS_VIKING_COLOR: {
            "celestial_body": CelestialBody.MARS,
            "satellite": "Viking Orbiter (Trek)",
            "type": "Colorized Mosaic (232m/px)"
        },
        ImageLayer.MARS_BASEMAP_OPM: {
            "celestial_body": CelestialBody.MARS,
            "satellite": "OpenPlanetaryMap",
            "type": "Mars Basemap"
        },
        # Moon layers
        ImageLayer.MOON_BASEMAP_OPM: {
            "celestial_body": CelestialBody.MOON,
            "satellite": "OpenPlanetaryMap",
            "type": "Lunar Basemap"
        },
        ImageLayer.MOON_BASEMAP_ARCGIS: {
            "celestial_body": CelestialBody.MOON,
            "satellite": "ESRI ArcGIS",
            "type": "Lunar Basemap"
        },
        # Mercury layers
        ImageLayer.MERCURY_BASEMAP_OPM: {
            "celestial_body": CelestialBody.MERCURY,
            "satellite": "OpenPlanetaryMap",
            "type": "Mercury Basemap (MESSENGER)"
        },
        # Deep Space layers (pre-tiled gigapixel only)
        ImageLayer.GALAXY_ANDROMEDA_GIGAPIXEL: {
            "celestial_body": CelestialBody.DEEP_SPACE,
            "satellite": "Hubble Space Telescope via Gigapan",
            "type": "1.5 Gigapixel Spiral Galaxy"
        }
    }
    
    layers = []
    for layer in ImageLayer:
        info = layer_info.get(layer, {
            "celestial_body": CelestialBody.EARTH,
            "satellite": "Unknown",
            "type": "Unknown"
        })
        
        # Filter by celestial body if specified
        if celestial_body and info["celestial_body"] != celestial_body:
            continue
        
        name = layer.name.replace('_', ' ').title()
        
        layers.append({
            "id": layer.name,
            "value": layer.value,
            "display_name": name,
            "celestial_body": info["celestial_body"].value,
            "satellite": info["satellite"],
            "type": info["type"],
            "description": f"{info['celestial_body'].value.title()} - {info['satellite']} {info['type']}"
        })
    
    return {
        "layers": layers,
        "total": len(layers),
        "celestial_body": celestial_body.value if celestial_body else "all"
    }

# SEARCH & DISCOVERY
# ----------------------------------------------------------------------------

@app.post("/api/search/images", response_model=List[ImageMetadata])
async def search_images(query: ImageSearchQuery, background_tasks: BackgroundTasks):
    """
    Search for NASA imagery based on criteria
    Returns metadata for matching images (tiles served by NASA GIBS or processed on-demand)
    
    For deep space objects with tiling enabled:
    - If tiles exist: returns tile URL
    - If tiles don't exist: triggers processing in background and returns placeholder
    """
    results = []
    
    # For custom images, automatically trigger tile processing if needed
    if query.celestial_body == CelestialBody.CUSTOM and query.layer in CUSTOM_IMAGES_CATALOG:
        obj = CUSTOM_IMAGES_CATALOG[query.layer]
        image_url = obj["image_url"]
        
        # If not yet tiled, trigger background processing
        if not tile_processor.is_tiled(image_url):
            status = tile_processor.get_processing_status(image_url)
            if status.get("status") != "processing":
                # Trigger processing in background
                def process_in_background():
                    try:
                        tile_processor.process_image(image_url, obj)
                    except Exception as e:
                        print(f"Tile processing failed for custom image {query.layer}: {e}")
                
                background_tasks.add_task(process_in_background)
    
    # Default date range if not specified
    date_start = query.date_start or date(2024, 1, 1)
    date_end = query.date_end or date.today()
    
    # For MVP, generate sample results
    # In production, query NASA CMR API or maintain an index
    current_date = date_start
    count = 0
    
    # Determine max_zoom based on celestial body and layer
    if query.celestial_body == CelestialBody.EARTH:
        max_zoom = 9  # GIBS supports up to zoom 9 for most layers
    elif query.celestial_body == CelestialBody.MARS:
        max_zoom = 12  # Mars high-res layers
    elif query.celestial_body == CelestialBody.MOON:
        max_zoom = 10
    elif query.celestial_body == CelestialBody.MERCURY:
        max_zoom = 10  # Mercury basemap
    elif query.celestial_body == CelestialBody.DEEP_SPACE:
        # Deep Space only has pre-tiled images with explicit max_zoom
        if query.layer in DEEP_SPACE_CATALOG:
            obj = DEEP_SPACE_CATALOG[query.layer]
            max_zoom = obj.get("max_zoom", 12)  # Default to 12 for gigapixel
        else:
            max_zoom = 12
    elif query.celestial_body == CelestialBody.CUSTOM:
        # Custom images - check processing status
        if query.layer in CUSTOM_IMAGES_CATALOG:
            obj = CUSTOM_IMAGES_CATALOG[query.layer]
            image_url = obj["image_url"]
            tile_info = tile_processor.get_tile_info(image_url)
            if tile_info and tile_info.get("status") == "completed":
                max_zoom = tile_info.get("max_zoom", 8)
            else:
                max_zoom = 8  # Default while processing
        else:
            max_zoom = 8
    else:
        max_zoom = 9
    
    # For non-Earth bodies (static images/mosaics), only return one result since there's no time-series
    limit = 1 if query.celestial_body != CelestialBody.EARTH else query.limit
    
    while current_date <= date_end and count < limit:
        image_id = f"{query.celestial_body.value}_{query.layer}_{current_date.isoformat()}"
        
        # Default bbox (global view)
        bbox = query.bbox or BoundingBox(north=90, south=-90, east=180, west=-180)
        
        # Generate description with rich metadata
        if query.celestial_body == CelestialBody.DEEP_SPACE and query.layer in DEEP_SPACE_CATALOG:
            obj = DEEP_SPACE_CATALOG[query.layer]
            description = f"{obj['name']} - {obj['type']}, {obj['distance']} away. Captured by {obj['telescope']}. {obj['description']}"
        elif query.celestial_body == CelestialBody.CUSTOM and query.layer in CUSTOM_IMAGES_CATALOG:
            obj = CUSTOM_IMAGES_CATALOG[query.layer]
            description = f"{obj['name']} - {obj['type']}. {obj['description']}"
        else:
            description = f"{query.celestial_body.value.title()} - {query.layer} imagery from {current_date}"
        
        results.append(ImageMetadata(
            id=image_id,
            layer=query.layer,
            date=current_date,
            bbox=bbox,
            tile_url=generate_tile_url_template(query.celestial_body, query.layer, current_date, query.projection),
            thumbnail_url=generate_thumbnail_url(query.celestial_body, query.layer, current_date, query.projection),
            projection=query.projection,
            max_zoom=max_zoom,
            description=description
        ))
        
        # Skip to next week for Earth time-series
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
    layer_counts = Counter(query.layer for query in search_history if query.layer)
    return [{"layer": layer, "count": count} 
            for layer, count in layer_counts.most_common(5)]

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

