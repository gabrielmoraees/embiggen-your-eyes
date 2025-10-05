"""
Pydantic schemas for data validation and serialization
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date

from .enums import (
    Category, Subject, SourceId, ProjectionType, AnnotationType
)


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


class DatasetCreateRequest(BaseModel):
    """Request to create a new dataset"""
    name: str
    description: Optional[str] = None
    category: Category
    subject: Subject
    url: str  # Can be tile service URL or image URL


class DatasetUpdateRequest(BaseModel):
    """Request to update an existing dataset"""
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[Category] = None
    subject: Optional[Subject] = None
