"""
In-memory data storage
In a production environment, this would be replaced with a database
"""
from typing import Dict
from app.models.schemas import Source, Dataset, Layer, View, Annotation, ImageLink, Collection


# Catalogs
SOURCES: Dict[str, Source] = {}
DATASETS: Dict[str, Dataset] = {}
LAYERS: Dict[str, Layer] = {}

# User data
views_db: Dict[str, View] = {}
annotations_db: Dict[str, Annotation] = {}
links_db: Dict[str, ImageLink] = {}
collections_db: Dict[str, Collection] = {}
