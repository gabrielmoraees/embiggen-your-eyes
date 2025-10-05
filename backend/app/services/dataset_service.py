"""
Dataset service for creating and managing datasets
"""
from typing import Dict, Any
from datetime import datetime
import uuid

from app.models.schemas import Dataset, Variant, DatasetCreateRequest
from app.models.enums import Category, Subject, SourceId, ProjectionType
from app.data.storage import DATASETS
from app.services.url_detector import detect_url_type, detect_source_from_url
from app.services.tile_processor import tile_processor


class DatasetService:
    """Service for dataset creation and management"""
    
    @staticmethod
    def create_dataset(request: DatasetCreateRequest) -> Dict[str, Any]:
        """
        Create a new dataset from URL
        
        Automatically detects if URL is:
        - Pre-tiled service (use as-is)
        - Image file (process into tiles)
        """
        url = request.url
        
        # Detect URL type
        url_type, error_reason = detect_url_type(url)
        
        if url_type == "unknown":
            return {
                "success": False,
                "error": error_reason
            }
        
        # Detect source
        source_id_str = detect_source_from_url(url)
        try:
            source_id = SourceId(source_id_str)
        except ValueError:
            source_id = SourceId.CUSTOM
        
        if url_type == "tile_service":
            return DatasetService._create_tiled_dataset(request, source_id, url)
        
        elif url_type == "image":
            return DatasetService._create_image_dataset(request, source_id, url)
    
    @staticmethod
    def _create_tiled_dataset(
        request: DatasetCreateRequest,
        source_id: SourceId,
        url: str
    ) -> Dict[str, Any]:
        """Create dataset from pre-tiled service"""
        
        # Generate dataset ID
        dataset_id = f"{request.subject.value}_{str(uuid.uuid4())[:8]}"
        
        # Create variant
        variant = Variant(
            id="default",
            name="Default",
            description="Default view",
            tile_url_template=url,
            thumbnail_url=url.replace("{z}", "0").replace("{y}", "0").replace("{x}", "0") if "{z}" in url else url,
            min_zoom=0,
            max_zoom=18,
            is_default=True
        )
        
        # Create dataset
        dataset = Dataset(
            id=dataset_id,
            name=request.name,
            description=request.description or f"{request.name} dataset",
            source_id=source_id,
            category=request.category,
            subject=request.subject,
            projection=ProjectionType.WEB_MERCATOR,
            supports_time_series="{date}" in url,
            variants=[variant],
            processing_status="ready"
        )
        
        # Add to catalog
        DATASETS[dataset_id] = dataset
        
        return {
            "success": True,
            "dataset": dataset,
            "dataset_id": dataset_id,
            "status": "ready",
            "message": "Dataset created successfully"
        }
    
    @staticmethod
    def _create_image_dataset(
        request: DatasetCreateRequest,
        source_id: SourceId,
        image_url: str
    ) -> Dict[str, Any]:
        """Create dataset from image file (requires tile processing)"""
        
        # Generate tile_id from URL
        tile_id = tile_processor._generate_tile_id(image_url)
        
        # Check if this image already exists
        existing_dataset = next(
            (ds for ds in DATASETS.values() 
             if ds.source_id == SourceId.CUSTOM and 
             hasattr(ds, 'tile_id') and 
             ds.tile_id == tile_id),
            None
        )
        
        if existing_dataset:
            return {
                "success": True,
                "dataset": existing_dataset,
                "dataset_id": existing_dataset.id,
                "status": existing_dataset.processing_status or "ready",
                "message": "This image already exists in the catalog",
                "is_duplicate": True
            }
        
        # Generate dataset ID
        dataset_id = f"custom_{str(uuid.uuid4())[:8]}"
        
        # Check if image is already tiled
        if tile_processor.is_tiled(image_url):
            tile_info = tile_processor.get_tile_info(image_url)
            status = "ready"
        else:
            # Start tile processing
            metadata = {
                "name": request.name,
                "description": request.description or "",
                "uploaded_at": datetime.now().isoformat()
            }
            
            try:
                tile_info = tile_processor.process_image(image_url, metadata)
                status = "ready"
            except Exception as e:
                # Processing failed or in progress
                status = "processing"
                tile_info = {
                    "tile_id": tile_id,
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
            name=request.name,
            description=request.description or f"Custom uploaded image: {request.name}",
            source_id=SourceId.CUSTOM,
            category=request.category,
            subject=request.subject,
            projection=ProjectionType.WEB_MERCATOR,
            supports_time_series=False,
            variants=[variant],
            processing_status=status,
            tile_id=tile_id,
            image_url=image_url
        )
        
        # Add to catalog
        DATASETS[dataset_id] = dataset
        
        return {
            "success": True,
            "dataset": dataset,
            "dataset_id": dataset_id,
            "status": status,
            "tile_info": tile_info,
            "message": "Dataset created successfully" if status == "ready" else "Dataset created, processing tiles",
            "is_duplicate": False
        }
