"""
Enumeration types for the application
"""
from enum import Enum


class Category(str, Enum):
    """High-level astronomical object categories"""
    PLANETS = "planets"
    SATELLITES = "satellites"
    DWARF_PLANETS = "dwarf_planets"
    GALAXIES = "galaxies"
    NEBULAE = "nebulae"
    STAR_CLUSTERS = "star_clusters"
    PHENOMENA = "phenomena"
    REGIONS = "regions"


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
    
    # Satellites (Moons)
    MOON = "moon"  # Earth's moon
    EUROPA = "europa"
    TITAN = "titan"
    ENCELADUS = "enceladus"
    
    # Galaxies
    MILKY_WAY = "milky_way"
    ANDROMEDA = "andromeda"


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
    LINK = "link"
