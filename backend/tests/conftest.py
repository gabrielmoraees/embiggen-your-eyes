"""
Pytest configuration and shared fixtures
"""
import pytest
from fastapi.testclient import TestClient
from typing import Generator
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app, annotations_db, links_db, collections_db, search_history


@pytest.fixture(scope="function")
def client() -> Generator[TestClient, None, None]:
    """
    Create a test client for the FastAPI app
    Clears all in-memory databases before each test
    """
    # Clear all in-memory storage before each test
    annotations_db.clear()
    links_db.clear()
    collections_db.clear()
    search_history.clear()
    
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
def sample_annotation_data():
    """Sample annotation data for testing"""
    return {
        "image_id": "test_image_123",
        "type": "point",
        "coordinates": [{"lat": 40.7128, "lng": -74.0060}],
        "text": "New York City",
        "color": "#FF0000"
    }


@pytest.fixture(scope="function")
def sample_link_data():
    """Sample link data for testing"""
    return {
        "source_image_id": "image_001",
        "target_image_id": "image_002",
        "relationship_type": "before_after",
        "description": "Hurricane comparison"
    }


@pytest.fixture(scope="function")
def sample_collection_data():
    """Sample collection data for testing"""
    return {
        "name": "Test Collection",
        "description": "A test collection",
        "image_ids": ["image_001", "image_002", "image_003"]
    }


@pytest.fixture(scope="function")
def sample_earth_search_query():
    """Sample Earth image search query"""
    return {
        "celestial_body": "earth",
        "layer": "VIIRS_SNPP_CorrectedReflectance_TrueColor",
        "date_start": "2024-08-15",
        "date_end": "2024-08-15",
        "projection": "epsg3857",
        "limit": 1
    }


@pytest.fixture(scope="function")
def sample_mars_search_query():
    """Sample Mars image search query"""
    return {
        "celestial_body": "mars",
        "layer": "opm_mars_basemap"
    }




@pytest.fixture(scope="function")
def sample_custom_image_data():
    """Sample custom image upload data"""
    return {
        "name": "Test Custom Image",
        "image_url": "https://images-assets.nasa.gov/image/PIA16695/PIA16695~orig.jpg",
        "description": "Test image for pytest",
        "max_zoom": 8
    }
