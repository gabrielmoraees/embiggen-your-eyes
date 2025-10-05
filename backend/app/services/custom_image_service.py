"""
Custom image service for user-uploaded images
Handles image upload, tile processing, and dataset creation
"""
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

from app.models.schemas import Dataset, Variant, Source
from app.models.enums import Category, Subject, SourceId, ProjectionType
from app.data.storage import DATASETS, SOURCES
from app.services.tile_processor import tile_processor


class CustomImageService:
    """Service for managing custom user-uploaded images"""
    
    @staticmethod
    def create_custom_dataset_from_url(
        image_url: str,
        name: str,
        description: Optional[str] = None,
        category: Category = Category.CUSTOM,
        subject: Subject = Subject.CUSTOM
    ) -> Dict[str, Any]:
        """
        Create a custom dataset from an image URL
        This will:
        1. Process the image into tiles (if not already processed)
        2. Create a dataset entry
        3. Return the dataset with tile URL
        """
        
        # Generate unique dataset ID
        dataset_id = f"custom_{str(uuid.uuid4())[:8]}"
        
        # Check if image is already tiled
        if tile_processor.is_tiled(image_url):
            tile_info = tile_processor.get_tile_info(image_url)
            status = "ready"
        else:
            # Start tile processing
            metadata = {
                "name": name,
                "description": description or "",
                "uploaded_at": datetime.now().isoformat()
            }
            
            try:
                tile_info = tile_processor.process_image(image_url, metadata)
                status = "ready"
            except Exception as e:
                # Processing failed or in progress
                status = "processing"
                tile_info = {
                    "tile_id": tile_processor._generate_tile_id(image_url),
                    "source_url": image_url,
                    "status": "processing"
                }
        
        # Get tile URL template
        try:
            tile_url_template = tile_processor.get_tile_url_template(
                image_url,
                base_url="http://localhost:8000"
            )
            thumbnail_url = f"http://localhost:8000/tiles/{tile_info['tile_id']}/0/0/0.png"
        except ValueError:
            # Tiles not ready yet
            tile_url_template = f"http://localhost:8000/api/tile-placeholder/{tile_info['tile_id']}"
            thumbnail_url = tile_url_template
        
        # Create variant
        variant = Variant(
            id="default",
            name="Original",
            description="Original uploaded image",
            tile_url_template=tile_url_template,
            thumbnail_url=thumbnail_url,
            min_zoom=0,
            max_zoom=tile_info.get('max_zoom', 8),
            is_default=True
        )
        
        # Create dataset
        dataset = Dataset(
            id=dataset_id,
            name=name,
            description=description or f"Custom uploaded image: {name}",
            source_id=SourceId.CUSTOM,
            category=category,
            subject=subject,
            projection=ProjectionType.WEB_MERCATOR,
            supports_time_series=False,
            variants=[variant]
        )
        
        # Add to catalog
        DATASETS[dataset_id] = dataset
        
        return {
            "dataset": dataset,
            "status": status,
            "tile_info": tile_info,
            "message": "Dataset created successfully" if status == "ready" else "Dataset created, tiles processing in background"
        }
    
    @staticmethod
    def get_tile_status(tile_id: str) -> Dict[str, Any]:
        """Get the processing status of tiles"""
        # Check if tiles are ready
        tile_info = tile_processor.tile_index.get(tile_id)
        
        if tile_info and tile_info.get('status') == 'completed':
            return {
                "status": "ready",
                "tile_info": tile_info
            }
        
        # Check if currently processing
        processing_status = tile_processor.processing_status.get(tile_id)
        if processing_status:
            return {
                "status": "processing",
                "progress": processing_status.get('progress'),
                "started_at": processing_status.get('started_at')
            }
        
        return {
            "status": "not_found",
            "message": "Tile ID not found"
        }
    
    @staticmethod
    def list_custom_datasets() -> Dict[str, Any]:
        """List all custom user-uploaded datasets"""
        custom_datasets = [
            dataset for dataset in DATASETS.values()
            if dataset.source_id == SourceId.CUSTOM
        ]
        
        return {
            "datasets": custom_datasets,
            "count": len(custom_datasets)
        }
    
    @staticmethod
    def delete_custom_dataset(dataset_id: str) -> bool:
        """Delete a custom dataset"""
        if dataset_id in DATASETS and DATASETS[dataset_id].source_id == SourceId.CUSTOM:
            del DATASETS[dataset_id]
            # Note: Tiles are kept in cache for potential reuse
            return True
        return False
