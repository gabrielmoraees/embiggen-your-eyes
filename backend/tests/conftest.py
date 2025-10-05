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

from app.core.app import create_app
from app.data.storage import annotations_db, links_db, collections_db, views_db

app = create_app()


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
    views_db.clear()
    
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
def sample_annotation_data():
    """Sample annotation data for testing"""
    return {
        "map_view_id": "test_view_123",
        "type": "point",
        "coordinates": [{"lat": 40.7128, "lng": -74.0060}],
        "text": "New York City",
        "color": "#FF0000"
    }


@pytest.fixture(scope="function")
def sample_link_data():
    """Sample link data for testing"""
    return {
        "source_view_id": "view_001",
        "target_view_id": "view_002",
        "relationship_type": "before_after",
        "description": "Hurricane comparison"
    }


@pytest.fixture(scope="function")
def sample_collection_data():
    """Sample collection data for testing"""
    return {
        "name": "Test Collection",
        "description": "A test collection",
        "view_ids": ["view_001", "view_002", "view_003"]
    }


@pytest.fixture(scope="function")
def sample_map_view_data():
    """Sample map view data for testing"""
    return {
        "name": "Test Dataset View",
        "description": "A test view of Earth",
        "dataset_id": "viirs_snpp",
        "variant_id": "true_color",
        "selected_date": "2025-10-04",
        "center_lat": 40.7128,
        "center_lng": -74.0060,
        "zoom_level": 8
    }
