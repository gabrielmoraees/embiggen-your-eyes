"""
URL detection utilities for identifying tile services and image files
"""
from typing import Tuple, Optional
from urllib.parse import urlparse


def is_tile_service_url(url: str) -> bool:
    """
    Detect if URL is a tile service (pre-tiled)
    
    Checks for:
    - XYZ tile patterns: {z}, {x}, {y}
    - WMS patterns: {bbox}
    - Known tile service domains
    """
    url_lower = url.lower()
    
    # Check for tile placeholders
    has_xyz = '{z}' in url and '{x}' in url and '{y}' in url
    has_bbox = '{bbox}' in url
    
    # Check for known tile service patterns
    known_services = [
        'wmts',
        'gibs.earthdata.nasa.gov',
        'trek.nasa.gov/tiles',
        'cartocdn',
        'openstreetmap',
        'mapbox',
        'arcgis'
    ]
    
    has_known_service = any(service in url_lower for service in known_services)
    
    return has_xyz or has_bbox or has_known_service


def is_image_url(url: str) -> bool:
    """
    Detect if URL is an image file
    
    Checks file extension for common image formats
    """
    url_lower = url.lower()
    
    image_extensions = (
        '.jpg', '.jpeg', '.png', '.gif', '.webp',
        '.tif', '.tiff', '.bmp'
    )
    
    # Check if URL ends with image extension (ignoring query params)
    parsed = urlparse(url_lower)
    path = parsed.path
    
    return path.endswith(image_extensions)


def detect_url_type(url: str) -> Tuple[str, Optional[str]]:
    """
    Detect URL type and return (type, reason)
    
    Returns:
        - ("tile_service", None) if pre-tiled service
        - ("image", None) if image file
        - ("unknown", reason) if neither
    """
    if is_tile_service_url(url):
        return ("tile_service", None)
    
    if is_image_url(url):
        return ("image", None)
    
    # Unknown type
    reason = "URL must be either a tile service (with {z}/{x}/{y} or {bbox}) or an image file (.jpg, .png, .tif, etc.)"
    return ("unknown", reason)


def detect_source_from_url(url: str) -> str:
    """
    Detect the source provider from URL
    
    Returns source_id string (e.g., "nasa_gibs", "nasa_trek")
    """
    url_lower = url.lower()
    
    if 'gibs.earthdata.nasa.gov' in url_lower:
        return "nasa_gibs"
    
    if 'trek.nasa.gov' in url_lower:
        return "nasa_trek"
    
    if 'cartocdn' in url_lower or 'openplanetarymap' in url_lower:
        return "openplanetarymap"
    
    if 'usgs.gov' in url_lower or 'astrogeology.usgs.gov' in url_lower:
        return "usgs"
    
    # Default to custom for unknown sources
    return "custom"
