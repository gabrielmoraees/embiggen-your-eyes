"""
Catalog API routes for sources and categories discovery
"""
from fastapi import APIRouter
from typing import Optional

from app.models.enums import Category, Subject
from app.services.catalog_service import CatalogService

router = APIRouter()


@router.get("/categories")
def get_categories():
    """Get list of available categories"""
    return CatalogService.get_categories()


@router.get("/sources")
def get_sources(category: Optional[Category] = None, subject: Optional[Subject] = None):
    """Get list of sources, optionally filtered by category or subject"""
    return CatalogService.get_sources(category, subject)