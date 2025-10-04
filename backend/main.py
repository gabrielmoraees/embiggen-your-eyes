"""
Embiggen Your Eyes - Backend API
FastAPI backend for NASA imagery visualization with hierarchical data model
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum
from pathlib import Path
import uuid

# Import tile processor
from tile_processor import tile_processor

app = FastAPI(title="Embiggen Your Eyes API", version="1.0.0")

# Mount static tiles directory
tiles_cache_path = Path("./tiles_cache")
tiles_cache_path.mkdir(exist_ok=True)
app.mount("/tiles", StaticFiles(directory=str(tiles_cache_path)), name="tiles")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# ENUMS
# ============================================================================

class Category(str, Enum):
    """High-level astronomical object categories"""
    PLANETS = "planets"
    MOONS = "moons"
    DWARF_PLANETS = "dwarf_planets"
    GALAXIES = "galaxies"
    NEBULAE = "nebulae"
    STAR_CLUSTERS = "star_clusters"
    PHENOMENA = "phenomena"
    REGIONS = "regions"
    CUSTOM = "custom"

class Subject(str, Enum):
    """Specific astronomical objects or subjects"""
    # Planets
    EARTH = "earth"
    MARS = "mars"
    MERCURY = "mercury"
    VENUS = "venus"
    JUPITER = "jupiter"
    SATURN = "saturn"
    URANUS = "uranus"
    NEPTUNE = "neptune"
    
    # Moons
    MOON = "moon"  # Earth's moon
    EUROPA = "europa"
    TITAN = "titan"
    ENCELADUS = "enceladus"
    
    # Galaxies
    MILKY_WAY = "milky_way"
    ANDROMEDA = "andromeda"
    
    # Custom
    CUSTOM = "custom"

class SourceId(str, Enum):
    """Map data providers"""
    NASA_GIBS = "nasa_gibs"
    NASA_TREK = "nasa_trek"
    OPENPLANETARYMAP = "openplanetarymap"
    USGS = "usgs"
    CUSTOM = "custom"

class ProjectionType(str, Enum):
    """Supported map projections"""
    WEB_MERCATOR = "epsg3857"
    GEOGRAPHIC = "epsg4326"

class AnnotationType(str, Enum):
    """Annotation types"""
    POINT = "point"
    POLYGON = "polygon"
    RECTANGLE = "rectangle"
    CIRCLE = "circle"
    TEXT = "text"

# ============================================================================
# CORE DATA MODELS
# ============================================================================

class Source(BaseModel):
    """Data provider (NASA GIBS, OpenPlanetaryMap, etc.)"""
    id: SourceId
    name: str
    description: str
    attribution: str
    url: Optional[str] = None
    terms_of_use: Optional[str] = None

class Layer(BaseModel):
    """Overlayable data layer (labels, borders, elevation, etc.)"""
    id: str
    name: str
    description: str
    tile_url_template: str
    thumbnail_url: Optional[str] = None
    opacity: float = Field(default=1.0, ge=0.0, le=1.0)
    blend_mode: str = "normal"  # normal, multiply, overlay, etc.
    min_zoom: int = 0
    max_zoom: int = 18
    enabled_by_default: bool = False

class Variant(BaseModel):
    """Visualization variant of a map (true color, false color, etc.)"""
    id: str
    name: str
    description: str
    tile_url_template: str
    thumbnail_url: str
    min_zoom: int = 0
    max_zoom: int = 18
    is_default: bool = False

class Dataset(BaseModel):
    """A specific dataset/map product from a source"""
    id: str
    name: str
    description: str
    source_id: SourceId
    category: Category  # High-level: Planets, Moons, Galaxies, etc.
    subject: Subject    # Specific: Earth, Mars, Andromeda, etc.
    projection: ProjectionType = ProjectionType.WEB_MERCATOR
    supports_time_series: bool = False
    date_range_start: Optional[date] = None
    date_range_end: Optional[date] = None
    default_date: Optional[date] = None
    variants: List[Variant] = []
    available_layers: List[str] = []  # Layer IDs that can be overlaid
    bbox: Optional[Dict[str, float]] = None  # Geographic extent
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class View(BaseModel):
    """User-saved map configuration"""
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    dataset_id: str
    variant_id: str
    active_layers: List[str] = []  # Layer IDs
    selected_date: Optional[date] = None
    center_lat: float = 0.0
    center_lng: float = 0.0
    zoom_level: int = 3
    annotation_ids: List[str] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class BoundingBox(BaseModel):
    """Geographic bounding box"""
    north: float
    south: float
    east: float
    west: float

class DatasetSearchQuery(BaseModel):
    """Search criteria for datasets"""
    category: Optional[Category] = None
    subject: Optional[Subject] = None
    source_id: Optional[SourceId] = None
    supports_time_series: Optional[bool] = None
    date: Optional[date] = None
    bbox: Optional[BoundingBox] = None
    limit: int = 50

# ============================================================================
# ANNOTATION MODELS
# ============================================================================

class Annotation(BaseModel):
    id: Optional[str] = None
    map_view_id: Optional[str] = None  # Link to View
    type: AnnotationType
    coordinates: List[Dict[str, float]]
    properties: Dict[str, Any] = {}
    text: Optional[str] = None
    color: str = "#FF0000"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ImageLink(BaseModel):
    """Link between map views"""
    id: Optional[str] = None
    source_view_id: str
    target_view_id: str
    annotation_id: Optional[str] = None
    relationship_type: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None

class Collection(BaseModel):
    """Collection of map views"""
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    view_ids: List[str] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# ============================================================================
# IN-MEMORY STORAGE
# ============================================================================

# Catalogs
SOURCES: Dict[str, Source] = {}
DATASETS: Dict[str, Dataset] = {}
LAYERS: Dict[str, Layer] = {}

# User data
views_db: Dict[str, View] = {}
annotations_db: Dict[str, Annotation] = {}
links_db: Dict[str, ImageLink] = {}
collections_db: Dict[str, Collection] = {}

# ============================================================================
# DATA CATALOG INITIALIZATION
# ============================================================================

def initialize_catalog():
    """Initialize the catalog with all available maps, sources, and layers"""
    
    # ========== MAP SOURCES ==========
    SOURCES[SourceId.NASA_GIBS] = Source(
        id=SourceId.NASA_GIBS,
        name="NASA GIBS",
        description="NASA Global Imagery Browse Services - Near real-time satellite imagery",
        attribution="NASA EOSDIS",
        url="https://earthdata.nasa.gov/eosdis/science-system-description/eosdis-components/gibs",
        terms_of_use="Public domain"
    )
    
    SOURCES[SourceId.NASA_TREK] = Source(
        id=SourceId.NASA_TREK,
        name="NASA Trek",
        description="NASA Solar System Trek - Planetary mapping portal",
        attribution="NASA/JPL-Caltech",
        url="https://trek.nasa.gov",
        terms_of_use="Public domain"
    )
    
    SOURCES[SourceId.OPENPLANETARYMAP] = Source(
        id=SourceId.OPENPLANETARYMAP,
        name="OpenPlanetaryMap",
        description="Open planetary mapping project",
        attribution="OpenPlanetaryMap Contributors",
        url="https://www.openplanetary.org/opm",
        terms_of_use="CC BY-SA 4.0"
    )
    
    SOURCES[SourceId.USGS] = Source(
        id=SourceId.USGS,
        name="USGS Astrogeology",
        description="United States Geological Survey Astrogeology Science Center",
        attribution="USGS Astrogeology Science Center",
        url="https://astrogeology.usgs.gov",
        terms_of_use="Public domain"
    )
    
    SOURCES[SourceId.CUSTOM] = Source(
        id=SourceId.CUSTOM,
        name="Custom Images",
        description="User-uploaded custom gigapixel images",
        attribution="User-provided",
        terms_of_use="As specified by uploader"
    )
    
    # ========== EARTH DATASETS ==========
    
    # VIIRS SNPP Map
    DATASETS["viirs_snpp"] = Dataset(
        id="viirs_snpp",
        name="VIIRS SNPP",
        description="Visible Infrared Imaging Radiometer Suite on Suomi NPP satellite",
        source_id=SourceId.NASA_GIBS,
        category=Category.PLANETS,
        subject=Subject.EARTH,
        supports_time_series=True,
        date_range_start=date(2015, 11, 24),
        date_range_end=date.today(),
        default_date=date.today(),
        variants=[
            Variant(
                id="true_color",
                name="True Color",
                description="Natural color composite",
                tile_url_template="https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/VIIRS_SNPP_CorrectedReflectance_TrueColor/default/{date}/GoogleMapsCompatible_Level9/{z}/{y}/{x}.jpg",
                thumbnail_url="https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/VIIRS_SNPP_CorrectedReflectance_TrueColor/default/{date}/GoogleMapsCompatible_Level9/0/0/0.jpg",
                max_zoom=9,
                is_default=True
            ),
            Variant(
                id="false_color",
                name="False Color",
                description="False color composite (Bands M11-I2-I1)",
                tile_url_template="https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/VIIRS_SNPP_CorrectedReflectance_BandsM11-I2-I1/default/{date}/GoogleMapsCompatible_Level9/{z}/{y}/{x}.jpg",
                thumbnail_url="https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/VIIRS_SNPP_CorrectedReflectance_BandsM11-I2-I1/default/{date}/GoogleMapsCompatible_Level9/0/0/0.jpg",
                max_zoom=9
            )
        ]
    )
    
    # MODIS Terra Map
    DATASETS["modis_terra"] = Dataset(
        id="modis_terra",
        name="MODIS Terra",
        description="Moderate Resolution Imaging Spectroradiometer on Terra satellite",
        source_id=SourceId.NASA_GIBS,
        category=Category.PLANETS,
        subject=Subject.EARTH,
        supports_time_series=True,
        date_range_start=date(2000, 2, 24),
        date_range_end=date.today(),
        default_date=date.today(),
        variants=[
            Variant(
                id="true_color",
                name="True Color",
                description="Natural color composite",
                tile_url_template="https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/{date}/GoogleMapsCompatible_Level9/{z}/{y}/{x}.jpg",
                thumbnail_url="https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/{date}/GoogleMapsCompatible_Level9/0/0/0.jpg",
                max_zoom=9,
                is_default=True
            ),
            Variant(
                id="false_color",
                name="False Color (Bands 7-2-1)",
                description="False color composite emphasizing vegetation",
                tile_url_template="https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_Bands721/default/{date}/GoogleMapsCompatible_Level9/{z}/{y}/{x}.jpg",
                thumbnail_url="https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_Bands721/default/{date}/GoogleMapsCompatible_Level9/0/0/0.jpg",
                max_zoom=9
            )
        ]
    )
    
    # ========== MARS DATASETS ==========
    
    # Viking Mosaic
    DATASETS["mars_viking"] = Dataset(
        id="mars_viking",
        name="Mars Viking Mosaic",
        description="Viking Orbiter colorized mosaic (232m/pixel)",
        source_id=SourceId.NASA_TREK,
        category=Category.PLANETS,
        subject=Subject.MARS,
        supports_time_series=False,
        variants=[
            Variant(
                id="colorized",
                name="Colorized",
                description="Colorized global mosaic",
                tile_url_template="https://trek.nasa.gov/tiles/Mars/EQ/Mars_Viking_MDIM21_ClrMosaic_global_232m/1.0.0/default/default028mm/{z}/{y}/{x}.jpg",
                thumbnail_url="https://trek.nasa.gov/tiles/Mars/EQ/Mars_Viking_MDIM21_ClrMosaic_global_232m/1.0.0/default/default028mm/0/0/0.jpg",
                max_zoom=9,
                is_default=True
            )
        ]
    )
    
    # Mars OPM Basemap
    DATASETS["mars_opm_basemap"] = Dataset(
        id="mars_opm_basemap",
        name="Mars Basemap",
        description="OpenPlanetaryMap Mars basemap",
        source_id=SourceId.OPENPLANETARYMAP,
        category=Category.PLANETS,
        subject=Subject.MARS,
        supports_time_series=False,
        variants=[
            Variant(
                id="default",
                name="Default",
                description="Standard basemap",
                tile_url_template="https://cartocdn-gusc.global.ssl.fastly.net/opmbuilder/api/v1/map/named/opm-mars-basemap-v0-2/all/{z}/{x}/{y}.png",
                thumbnail_url="https://cartocdn-gusc.global.ssl.fastly.net/opmbuilder/api/v1/map/named/opm-mars-basemap-v0-2/all/0/0/0.png",
                max_zoom=18,
                is_default=True
            )
        ]
    )
    
    # ========== MOON DATASETS ==========
    
    # Moon OPM Basemap
    DATASETS["moon_opm_basemap"] = Dataset(
        id="moon_opm_basemap",
        name="Lunar Basemap",
        description="OpenPlanetaryMap lunar basemap",
        source_id=SourceId.OPENPLANETARYMAP,
        category=Category.MOONS,
        subject=Subject.MOON,
        supports_time_series=False,
        variants=[
            Variant(
                id="default",
                name="Default",
                description="Standard lunar basemap",
                tile_url_template="https://cartocdn-gusc.global.ssl.fastly.net/opmbuilder/api/v1/map/named/opm-moon-basemap-v0-1/all/{z}/{x}/{y}.png",
                thumbnail_url="https://cartocdn-gusc.global.ssl.fastly.net/opmbuilder/api/v1/map/named/opm-moon-basemap-v0-1/all/0/0/0.png",
                max_zoom=18,
                is_default=True
            )
        ]
    )
    
    # Moon USGS Geologic Map
    DATASETS["moon_usgs_geologic"] = Dataset(
        id="moon_usgs_geologic",
        name="Unified Geologic Map",
        description="USGS Unified Geologic Map of the Moon",
        source_id=SourceId.USGS,
        category=Category.MOONS,
        subject=Subject.MOON,
        supports_time_series=False,
        variants=[
            Variant(
                id="default",
                name="Geologic",
                description="Unified geologic map showing 49 lunar units",
                tile_url_template="https://bm2ms.rsl.wustl.edu/arcgis/rest/services/moon_c0/moon_bm_usgs_Unified_Geologic_Map_p2_c0/MapServer/tile/{z}/{y}/{x}",
                thumbnail_url="https://bm2ms.rsl.wustl.edu/arcgis/rest/services/moon_c0/moon_bm_usgs_Unified_Geologic_Map_p2_c0/MapServer/tile/0/0/0",
                max_zoom=18,
                is_default=True
            )
        ]
    )
    
    # ========== MERCURY DATASETS ==========
    
    # Mercury OPM Basemap
    DATASETS["mercury_opm_basemap"] = Dataset(
        id="mercury_opm_basemap",
        name="Mercury Basemap",
        description="OpenPlanetaryMap Mercury basemap (MESSENGER)",
        source_id=SourceId.OPENPLANETARYMAP,
        category=Category.PLANETS,
        subject=Subject.MERCURY,
        supports_time_series=False,
        variants=[
            Variant(
                id="default",
                name="Default",
                description="MESSENGER basemap",
                tile_url_template="https://cartocdn-gusc.global.ssl.fastly.net/opmbuilder/api/v1/map/named/opm-mercury-basemap-v0-1/all/{z}/{x}/{y}.png",
                thumbnail_url="https://cartocdn-gusc.global.ssl.fastly.net/opmbuilder/api/v1/map/named/opm-mercury-basemap-v0-1/all/0/0/0.png",
                max_zoom=18,
                is_default=True
            )
        ]
    )

# Initialize catalog on startup
initialize_catalog()

# ============================================================================
# API ENDPOINTS - MAP DISCOVERY
# ============================================================================

@app.get("/")
def root():
    """API root"""
    return {
        "name": "Embiggen Your Eyes API",
        "version": "1.0.0",
        "description": "Hierarchical map data model with sources, maps, variants, and layers"
    }

@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/api/categories")
def get_categories():
    """Get list of available categories"""
    categories = {}
    for dataset in DATASETS.values():
        cat = dataset.category.value
        if cat not in categories:
            categories[cat] = {
                "id": cat,
                "name": cat.replace('_', ' ').title(),
                "dataset_count": 0,
                "subjects": set(),
                "sources": set()
            }
        categories[cat]["dataset_count"] += 1
        categories[cat]["subjects"].add(dataset.subject.value)
        categories[cat]["sources"].add(dataset.source_id.value)
    
    # Convert sets to lists for JSON serialization
    for cat in categories.values():
        cat["subjects"] = list(cat["subjects"])
        cat["sources"] = list(cat["sources"])
    
    return {"categories": list(categories.values())}

@app.get("/api/sources")
def get_sources(category: Optional[Category] = None, subject: Optional[Subject] = None):
    """Get list of sources, optionally filtered by category or subject"""
    sources = []
    for source in SOURCES.values():
        # Count datasets for this source
        dataset_count = sum(
            1 for d in DATASETS.values()
            if d.source_id == source.id and (
                category is None or d.category == category
            ) and (
                subject is None or d.subject == subject
            )
        )
        
        if dataset_count > 0 or (category is None and subject is None):
            sources.append({
                **source.model_dump(),
                "dataset_count": dataset_count
            })
    
    return {"sources": sources}

@app.get("/api/datasets")
def get_datasets(
    category: Optional[Category] = None,
    subject: Optional[Subject] = None,
    source_id: Optional[SourceId] = None,
    supports_time_series: Optional[bool] = None
):
    """Get list of datasets with optional filters"""
    filtered_datasets = []
    
    for dataset in DATASETS.values():
        # Apply filters
        if category and dataset.category != category:
            continue
        if subject and dataset.subject != subject:
            continue
        if source_id and dataset.source_id != source_id:
            continue
        if supports_time_series is not None and dataset.supports_time_series != supports_time_series:
            continue
        
        filtered_datasets.append(dataset)
    
    return {"datasets": filtered_datasets, "count": len(filtered_datasets)}

@app.get("/api/datasets/{dataset_id}")
def get_dataset(dataset_id: str):
    """Get details for a specific dataset"""
    if dataset_id not in DATASETS:
        raise HTTPException(status_code=404, detail=f"Dataset not found: {dataset_id}")
    
    return DATASETS[dataset_id]

@app.get("/api/datasets/{dataset_id}/variants")
def get_dataset_variants(dataset_id: str):
    """Get variants for a specific dataset"""
    if dataset_id not in DATASETS:
        raise HTTPException(status_code=404, detail=f"Dataset not found: {dataset_id}")
    
    dataset = DATASETS[dataset_id]
    return {
        "dataset_id": dataset_id,
        "dataset_name": dataset.name,
        "variants": dataset.variants
    }

@app.get("/api/datasets/{dataset_id}/variants/{variant_id}")
def get_dataset_variant(dataset_id: str, variant_id: str, date_param: Optional[date] = None):
    """Get specific variant with resolved tile URLs"""
    if dataset_id not in DATASETS:
        raise HTTPException(status_code=404, detail=f"Dataset not found: {dataset_id}")
    
    dataset = DATASETS[dataset_id]
    variant = next((v for v in dataset.variants if v.id == variant_id), None)
    
    if not variant:
        raise HTTPException(status_code=404, detail=f"Variant not found: {variant_id}")
    
    # Resolve date for time-series maps
    selected_date = date_param or dataset.default_date or date.today()
    
    # Replace {date} placeholder in URLs if needed
    tile_url = variant.tile_url_template
    thumbnail_url = variant.thumbnail_url
    
    if dataset.supports_time_series:
        date_str = selected_date.strftime("%Y-%m-%d")
        tile_url = tile_url.replace("{date}", date_str)
        thumbnail_url = thumbnail_url.replace("{date}", date_str)
    
    return {
        "dataset_id": dataset_id,
        "variant": {
            **variant.model_dump(),
            "tile_url": tile_url,
            "thumbnail_url": thumbnail_url,
            "selected_date": selected_date if dataset.supports_time_series else None
        }
    }

# ============================================================================
# API ENDPOINTS - MAP VIEWS (User-Saved Configurations)
# ============================================================================

@app.post("/api/views", response_model=View)
def create_map_view(view: View):
    """Create a new saved map view"""
    view.id = str(uuid.uuid4())
    view.created_at = datetime.now()
    view.updated_at = datetime.now()
    
    # Validate map and variant exist
    if view.dataset_id not in DATASETS:
        raise HTTPException(status_code=404, detail=f"Map not found: {view.dataset_id}")
    
    dataset = DATASETS[view.dataset_id]
    if not any(v.id == view.variant_id for v in dataset.variants):
        raise HTTPException(status_code=404, detail=f"Variant not found: {view.variant_id}")
    
    views_db[view.id] = view
    return view

@app.get("/api/views")
def get_map_views():
    """Get all saved map views"""
    return {"views": list(views_db.values()), "count": len(views_db)}

@app.get("/api/views/{view_id}", response_model=View)
def get_map_view(view_id: str):
    """Get a specific map view"""
    if view_id not in views_db:
        raise HTTPException(status_code=404, detail="View not found")
    return views_db[view_id]

@app.put("/api/views/{view_id}", response_model=View)
def update_map_view(view_id: str, view: View):
    """Update a map view"""
    if view_id not in views_db:
        raise HTTPException(status_code=404, detail="View not found")
    
    view.id = view_id
    view.updated_at = datetime.now()
    views_db[view_id] = view
    return view

@app.delete("/api/views/{view_id}")
def delete_map_view(view_id: str):
    """Delete a map view"""
    if view_id not in views_db:
        raise HTTPException(status_code=404, detail="View not found")
    
    del views_db[view_id]
    return {"message": "View deleted successfully"}

# ============================================================================
# API ENDPOINTS - ANNOTATIONS
# ============================================================================

@app.post("/api/annotations", response_model=Annotation)
def create_annotation(annotation: Annotation):
    """Create a new annotation"""
    annotation.id = str(uuid.uuid4())
    annotation.created_at = datetime.now()
    annotation.updated_at = datetime.now()
    annotations_db[annotation.id] = annotation
    return annotation

@app.get("/api/annotations")
def get_annotations(map_view_id: Optional[str] = None):
    """Get annotations, optionally filtered by map view"""
    if map_view_id:
        filtered = [a for a in annotations_db.values() if a.map_view_id == map_view_id]
        return {"annotations": filtered}
    return {"annotations": list(annotations_db.values())}

@app.get("/api/annotations/{annotation_id}", response_model=Annotation)
def get_annotation(annotation_id: str):
    """Get a specific annotation"""
    if annotation_id not in annotations_db:
        raise HTTPException(status_code=404, detail="Annotation not found")
    return annotations_db[annotation_id]

@app.put("/api/annotations/{annotation_id}", response_model=Annotation)
def update_annotation(annotation_id: str, annotation: Annotation):
    """Update an annotation"""
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
    return {"message": "Annotation deleted successfully"}

# ============================================================================
# API ENDPOINTS - COLLECTIONS
# ============================================================================

@app.post("/api/collections", response_model=Collection)
def create_collection(collection: Collection):
    """Create a new collection"""
    collection.id = str(uuid.uuid4())
    collection.created_at = datetime.now()
    collection.updated_at = datetime.now()
    collections_db[collection.id] = collection
    return collection

@app.get("/api/collections")
def get_collections():
    """Get all collections"""
    return {"collections": list(collections_db.values())}

@app.get("/api/collections/{collection_id}", response_model=Collection)
def get_collection(collection_id: str):
    """Get a specific collection"""
    if collection_id not in collections_db:
        raise HTTPException(status_code=404, detail="Collection not found")
    return collections_db[collection_id]

@app.put("/api/collections/{collection_id}", response_model=Collection)
def update_collection(collection_id: str, collection: Collection):
    """Update a collection"""
    if collection_id not in collections_db:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    collection.id = collection_id
    collection.updated_at = datetime.now()
    collections_db[collection_id] = collection
    return collection

@app.delete("/api/collections/{collection_id}")
def delete_collection(collection_id: str):
    """Delete a collection"""
    if collection_id not in collections_db:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    del collections_db[collection_id]
    return {"message": "Collection deleted successfully"}

# ============================================================================
# STARTUP
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
