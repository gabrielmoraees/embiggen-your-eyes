"""
Enumeration types for the application
"""
from enum import Enum


class Category(str, Enum):
    """
    High-level astronomical object categories
    Note: Order of definition determines display order in UI
    """
    PLANETS = "planets"
    SATELLITES = "satellites"
    GALAXIES = "galaxies"
    DWARF_PLANETS = "dwarf_planets"
    NEBULAE = "nebulae"
    STAR_CLUSTERS = "star_clusters"
    PHENOMENA = "phenomena"
    REGIONS = "regions"


class Subject(str, Enum):
    """
    Specific astronomical objects or subjects
    Note: Order of definition determines display order in UI
    """
    # Planets (in display order)
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


def get_enum_order(enum_class: type[Enum], value: str) -> int:
    """
    Get the ordinal position of an enum value.
    Returns 999 if not found (for sorting unrecognized values last).
    """
    for i, member in enumerate(enum_class):
        if member.value == value:
            return i
    return 999


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
