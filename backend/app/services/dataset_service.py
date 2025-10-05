"""
Dataset service for creating and managing datasets
"""
from typing import Dict, Any
from datetime import datetime
import uuid

from app.models.schemas import Dataset, Variant, DatasetCreateRequest, DatasetUpdateRequest
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
            tile_url_template = tile_processor.get_tile_url_template(
                image_url,
                base_url="http://localhost:8000"
            )
            thumbnail_url = f"http://localhost:8000/tiles/{tile_info['tile_id']}/0/0/0.png"
        else:
            # Queue tile processing in background - don't wait for it
            metadata = {
                "name": request.name,
                "description": request.description or "",
                "uploaded_at": datetime.now().isoformat(),
                "dataset_id": dataset_id
            }
            
            # Start background processing (non-blocking)
            tile_processor.queue_processing(image_url, metadata)
            
            status = "processing"
            tile_info = {
                "tile_id": tile_id,
                "source_url": image_url,
                "status": "processing"
            }
            # Tiles not ready yet - URLs will be updated after processing
            # Use empty template that will be replaced when ready
            tile_url_template = ""
            thumbnail_url = ""
        
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
    
    @staticmethod
    def update_dataset(dataset_id: str, request: DatasetUpdateRequest) -> Dict[str, Any]:
        """
        Update an existing dataset's metadata
        
        Only allows updating metadata fields (name, description, category, subject).
        Cannot update URL or tile-related fields.
        Only custom datasets can be updated.
        """
        # Check if dataset exists
        if dataset_id not in DATASETS:
            return {
                "success": False,
                "error": f"Dataset not found: {dataset_id}"
            }
        
        dataset = DATASETS[dataset_id]
        
        # Only allow updating custom datasets
        if dataset.source_id != SourceId.CUSTOM:
            return {
                "success": False,
                "error": "Only custom datasets can be updated"
            }
        
        # Update fields if provided
        updated = False
        if request.name is not None:
            dataset.name = request.name
            updated = True
        
        if request.description is not None:
            dataset.description = request.description
            updated = True
        
        if request.category is not None:
            dataset.category = request.category
            updated = True
        
        if request.subject is not None:
            dataset.subject = request.subject
            updated = True
        
        if updated:
            dataset.updated_at = datetime.now()
        
        return {
            "success": True,
            "dataset": dataset,
            "dataset_id": dataset_id,
            "message": "Dataset updated successfully" if updated else "No changes made"
        }
