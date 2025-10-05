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
    """Get list of available categories (only those with datasets)"""
    return CatalogService.get_categories()


@router.get("/categories/all")
def get_all_categories():
    """Get all possible categories from enums, regardless of dataset availability"""
    categories = []
    for category in Category:
        categories.append({
            "id": category.value,
            "name": category.value.replace('_', ' ').title()
        })
    return {"categories": categories}


@router.get("/subjects/all")
def get_all_subjects():
    """Get all possible subjects from enums, regardless of dataset availability"""
    subjects = []
    for subject in Subject:
        subjects.append({
            "id": subject.value,
            "name": subject.value.replace('_', ' ').title()
        })
    return {"subjects": subjects}


@router.get("/sources")
def get_sources(category: Optional[Category] = None, subject: Optional[Subject] = None):
    """Get list of sources, optionally filtered by category or subject"""
    return CatalogService.get_sources(category, subject)