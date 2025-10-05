"""
Tile Processor
Converts large images to tile pyramids on-demand using GDAL
"""
import os
import requests
import subprocess
import json
from pathlib import Path
from typing import Dict, Optional, Tuple
import hashlib
from datetime import datetime
import logging
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
TILES_BASE_DIR = Path("./tiles_cache")
DOWNLOADS_DIR = Path("./downloads")
TILES_BASE_DIR.mkdir(exist_ok=True)
DOWNLOADS_DIR.mkdir(exist_ok=True)

class TileProcessor:
    """Handles on-demand tile generation from gigapixel images"""
    
    def __init__(self):
        self.tiles_dir = TILES_BASE_DIR
        self.downloads_dir = DOWNLOADS_DIR
        self.processing_status: Dict[str, Dict] = {}
        self._load_tile_index()
    
    def _load_tile_index(self):
        """Load index of already processed tiles"""
        index_file = self.tiles_dir / "tile_index.json"
        if index_file.exists():
            with open(index_file, 'r') as f:
                self.tile_index = json.load(f)
        else:
            self.tile_index = {}
    
    def _save_tile_index(self):
        """Save tile index to disk"""
        index_file = self.tiles_dir / "tile_index.json"
        with open(index_file, 'w') as f:
            json.dump(self.tile_index, f, indent=2)
    
    def _generate_tile_id(self, image_url: str) -> str:
        """Generate unique ID for an image based on URL"""
        return hashlib.md5(image_url.encode()).hexdigest()
    
    def is_tiled(self, image_url: str) -> bool:
        """Check if image has already been converted to tiles"""
        tile_id = self._generate_tile_id(image_url)
        return tile_id in self.tile_index and self.tile_index[tile_id].get('status') == 'completed'
    
    def get_tile_info(self, image_url: str) -> Optional[Dict]:
        """Get tile information for a processed image"""
        tile_id = self._generate_tile_id(image_url)
        return self.tile_index.get(tile_id)
    
    def get_processing_status(self, image_url: str) -> Dict:
        """Get current processing status"""
        tile_id = self._generate_tile_id(image_url)
        if tile_id in self.processing_status:
            return self.processing_status[tile_id]
        if tile_id in self.tile_index:
            return self.tile_index[tile_id]
        return {"status": "not_started"}
    
    def download_image(self, image_url: str, tile_id: str) -> Path:
        """Download source image from URL with progress tracking"""
        logger.info(f"Downloading image from {image_url}")
        
        # Determine file extension from URL
        ext = Path(image_url).suffix or '.jpg'
        local_file = self.downloads_dir / f"{tile_id}{ext}"
        
        if local_file.exists():
            logger.info(f"Image already downloaded: {local_file}")
            return local_file
        
        # Download with streaming for large files
        response = requests.get(image_url, stream=True, timeout=60)
        response.raise_for_status()
        
        # Get total file size if available
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0
        
        with open(local_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded_size += len(chunk)
                
                # Update progress (0-30% for download phase)
                if total_size > 0 and tile_id in self.processing_status:
                    download_percent = (downloaded_size / total_size) * 30
                    self.processing_status[tile_id]["percentage"] = int(download_percent)
                    self.processing_status[tile_id]["progress"] = "downloading"
                    self.processing_status[tile_id]["message"] = f"Downloading image... {int(download_percent)}%"
        
        logger.info(f"Downloaded to {local_file}")
        return local_file
    
    def generate_tiles(self, image_path: Path, tile_id: str) -> Tuple[Path, int]:
        """
        Generate tile pyramid using GDAL's gdal2tiles.py
        Expects a georeferenced image (EPSG:4326 with world bounds)
        Calculates optimal zoom levels based on image dimensions
        Returns: (tiles_directory, max_zoom_level)
        """
        logger.info(f"Generating tiles for {image_path}")
        
        output_dir = self.tiles_dir / tile_id
        output_dir.mkdir(exist_ok=True, parents=True)
        
        # Check if gdal2tiles.py is available
        try:
            # Try common locations for gdal2tiles
            gdal2tiles_cmd = self._find_gdal2tiles()
            
            # Use absolute paths to avoid path resolution issues
            abs_image_path = image_path.resolve()
            abs_output_dir = output_dir.resolve()
            
            # Calculate optimal zoom levels based on image size
            # Use gdalinfo to get image dimensions
            gdalinfo_result = subprocess.run(
                ['gdalinfo', str(abs_image_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse image dimensions from gdalinfo output
            import re
            size_match = re.search(r'Size is (\d+), (\d+)', gdalinfo_result.stdout)
            if size_match:
                width = int(size_match.group(1))
                height = int(size_match.group(2))
                
                # Calculate max zoom based on largest dimension
                # At zoom 0, we have 256x256 pixels for the world
                # Each zoom level doubles the resolution
                # max_zoom = log2(max_dimension / 256)
                import math
                max_dimension = max(width, height)
                calculated_max_zoom = math.ceil(math.log2(max_dimension / 256))
                
                # Clamp between reasonable values (0-12)
                max_zoom = max(0, min(12, calculated_max_zoom))
                
                logger.info(f"Image size: {width}x{height}, calculated max zoom: {max_zoom}")
            else:
                # Fallback if we can't parse dimensions
                max_zoom = 8
                logger.warning(f"Could not determine image size, using default max_zoom={max_zoom}")
            
            # Generate tiles from georeferenced image
            cmd = [
                gdal2tiles_cmd,
                '--profile=mercator',  # Mercator profile for web display
                '--xyz',               # XYZ tile scheme (Leaflet-compatible, not TMS)
                f'--zoom=0-{max_zoom}',  # Dynamic zoom range based on image size
                '--processes=4',       # Use multiple cores
                '--webviewer=none',    # Don't generate viewer HTML
                str(abs_image_path),
                str(abs_output_dir)
            ]
            
            logger.info(f"Running: {' '.join(cmd)}")
            
            # Run gdal2tiles in a subprocess and monitor progress
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Monitor progress by counting generated tiles
            import time
            start_time = time.time()
            last_count = 0
            
            while process.poll() is None:
                # Check how many tiles have been generated
                if output_dir.exists():
                    tile_count = sum(1 for _ in output_dir.rglob('*.png'))
                    
                    # Estimate progress (rough estimate: 87k tiles for Andromeda)
                    # Progress from 40% to 95% during tile generation
                    estimated_total = 100000  # Rough estimate
                    progress_pct = 40 + int((tile_count / estimated_total) * 55)
                    progress_pct = min(95, progress_pct)  # Cap at 95%
                    
                    if tile_count != last_count:
                        # Use the tile_id parameter passed to this method
                        if tile_id in self.processing_status:
                            self.processing_status[tile_id].update({
                                "percentage": progress_pct,
                                "message": f"Generating tiles... {tile_count:,} tiles created"
                            })
                        last_count = tile_count
                
                time.sleep(2)  # Check every 2 seconds
            
            # Get any remaining output
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                raise RuntimeError(f"gdal2tiles failed: {stderr}")
            
            # Determine max zoom from generated directories
            max_zoom = self._get_max_zoom(output_dir)
            
            logger.info(f"Tiles generated successfully. Max zoom: {max_zoom}")
            return output_dir, max_zoom
            
        except Exception as e:
            logger.error(f"Tile generation failed: {e}")
            raise
    
    def _find_gdal2tiles(self) -> str:
        """Find gdal2tiles command"""
        # Try different possible locations (in order of preference)
        possible_commands = [
            '/opt/homebrew/bin/gdal2tiles.py',  # Homebrew on Apple Silicon
            '/usr/local/bin/gdal2tiles.py',      # Homebrew on Intel Mac
            'gdal2tiles.py',                     # In PATH
            'gdal2tiles',                        # Alternative name
        ]
        
        for cmd in possible_commands:
            try:
                # Test if command exists and works
                test_cmd = f"{cmd} --help"
                result = subprocess.run(
                    test_cmd,
                    shell=True,
                    capture_output=True,
                    timeout=5,
                    text=True
                )
                if result.returncode == 0:
                    logger.info(f"Found gdal2tiles at: {cmd}")
                    return cmd
            except subprocess.TimeoutExpired:
                logger.warning(f"Timeout checking: {cmd}")
                continue
            except Exception as e:
                logger.debug(f"Failed to check {cmd}: {e}")
                continue
        
        # If we get here, GDAL wasn't found
        error_msg = (
            "gdal2tiles.py not found. Please install GDAL:\n"
            "  brew install gdal\n"
            f"Tried locations: {', '.join(possible_commands)}"
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    
    def _get_min_zoom(self, tiles_dir: Path) -> int:
        """Determine minimum zoom level from generated tiles"""
        zoom_dirs = [d for d in tiles_dir.iterdir() if d.is_dir() and d.name.isdigit()]
        if not zoom_dirs:
            return 0  # Default fallback
        return min(int(d.name) for d in zoom_dirs)
    
    def _get_max_zoom(self, tiles_dir: Path) -> int:
        """Determine maximum zoom level from generated tiles"""
        zoom_dirs = [d for d in tiles_dir.iterdir() if d.is_dir() and d.name.isdigit()]
        if not zoom_dirs:
            return 8  # Default fallback
        return max(int(d.name) for d in zoom_dirs)
    
    def queue_processing(self, image_url: str, metadata: Dict):
        """
        Queue image processing in a background thread (non-blocking)
        Returns immediately, processing happens asynchronously
        """
        tile_id = self._generate_tile_id(image_url)
        
        # Check if already processed or processing
        if self.is_tiled(image_url):
            logger.info(f"Image already tiled: {tile_id}")
            return
        
        if tile_id in self.processing_status:
            logger.info(f"Image already being processed: {tile_id}")
            return
        
        # Mark as queued
        self.processing_status[tile_id] = {
            "status": "queued",
            "queued_at": datetime.now().isoformat()
        }
        
        # Start background thread
        # Note: daemon=False so thread can complete even if main process reloads
        thread = threading.Thread(
            target=self._process_image_background,
            args=(image_url, metadata),
            daemon=False
        )
        thread.start()
        logger.info(f"Queued processing for {tile_id}")
    
    def _process_image_background(self, image_url: str, metadata: Dict):
        """
        Background worker that processes the image
        Resumable at any step: download, georeference, or tile generation
        """
        tile_id = self._generate_tile_id(image_url)
        
        try:
            # Update processing status - initial state
            self.processing_status[tile_id] = {
                "status": "processing",
                "started_at": datetime.now().isoformat(),
                "progress": "queued",
                "percentage": 0,
                "message": "Queued for processing..."
            }
            
            # Determine file extension
            ext = Path(image_url).suffix or '.tif'
            image_path = self.downloads_dir / f"{tile_id}{ext}"
            georef_path = self.downloads_dir / f"{tile_id}_georef.tif"
            tiles_dir = self.tiles_dir / tile_id
            
            # Step 1: Download image (0-20%) - Skip if already downloaded
            if not image_path.exists():
                self.processing_status[tile_id].update({
                    "progress": "downloading",
                    "percentage": 0,
                    "message": "Downloading image..."
                })
                image_path = self.download_image(image_url, tile_id)
                logger.info(f"Download complete: {image_path}")
            else:
                logger.info(f"Download already exists, skipping: {image_path}")
            
            self.processing_status[tile_id].update({
                "percentage": 20,
                "message": "Download complete"
            })
            
            # Step 2: Georeference image (20-40%) - Skip if already georeferenced
            if not georef_path.exists():
                self.processing_status[tile_id].update({
                    "progress": "georeferencing",
                    "percentage": 20,
                    "message": "Georeferencing image to world bounds..."
                })
                
                logger.info(f"Georeferencing image to world bounds...")
                georef_cmd = [
                    'gdal_translate',
                    '-of', 'GTiff',
                    '-a_srs', 'EPSG:4326',
                    '-a_ullr', '-180', '90', '180', '-90',
                    str(image_path.resolve()),
                    str(georef_path.resolve())
                ]
                
                georef_result = subprocess.run(
                    georef_cmd,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if georef_result.returncode != 0:
                    raise RuntimeError(f"gdal_translate failed: {georef_result.stderr}")
                
                logger.info(f"Georeferencing complete: {georef_path}")
            else:
                logger.info(f"Georeferenced file already exists, skipping: {georef_path}")
            
            self.processing_status[tile_id].update({
                "percentage": 40,
                "message": "Georeferencing complete"
            })
            
            # Step 3: Generate tiles (40-100%) - Skip if tiles already exist
            if not tiles_dir.exists() or not any(tiles_dir.iterdir()):
                self.processing_status[tile_id].update({
                    "progress": "generating_tiles",
                    "percentage": 40,
                    "message": "Generating tiles... This may take several minutes."
                })
                
                tiles_dir, max_zoom = self.generate_tiles(georef_path, tile_id)
                logger.info(f"Tile generation complete: {tiles_dir}")
            else:
                logger.info(f"Tiles already exist, skipping generation: {tiles_dir}")
                max_zoom = self._get_max_zoom(tiles_dir)
            
            # Get min zoom from generated tiles
            min_zoom = self._get_min_zoom(tiles_dir)
            
            # Step 4: Finalizing (95%)
            self.processing_status[tile_id].update({
                "progress": "finalizing",
                "percentage": 95,
                "message": "Finalizing..."
            })
            
            # Step 5: Update index
            tile_info = {
                "tile_id": tile_id,
                "source_url": image_url,
                "tiles_path": str(tiles_dir.relative_to(self.tiles_dir)),
                "min_zoom": min_zoom,
                "max_zoom": max_zoom,
                "status": "completed",
                "metadata": metadata,
                "created_at": datetime.now().isoformat()
            }
            
            self.tile_index[tile_id] = tile_info
            self._save_tile_index()
            
            # Mark as complete (100%)
            self.processing_status[tile_id].update({
                "progress": "completed",
                "percentage": 100,
                "message": "Processing complete!",
                "status": "completed"
            })
            
            logger.info(f"Processing completed for {tile_id}")
            
            # Update dataset status if dataset_id is in metadata
            if "dataset_id" in metadata:
                self._update_dataset_status(metadata["dataset_id"], "ready")
            
        except Exception as e:
            logger.error(f"Processing failed for {tile_id}: {e}")
            import traceback
            traceback.print_exc()
            self.processing_status[tile_id] = {
                "status": "failed",
                "progress": "failed",
                "percentage": 0,
                "error": str(e),
                "message": f"Processing failed: {str(e)}",
                "failed_at": datetime.now().isoformat()
            }
            
            # Update dataset status if dataset_id is in metadata
            if "dataset_id" in metadata:
                self._update_dataset_status(metadata["dataset_id"], "failed")
    
    def _update_dataset_status(self, dataset_id: str, status: str):
        """Update dataset status after processing completes"""
        from app.data.storage import DATASETS
        from app.models.schemas import Dataset, Variant
        
        if dataset_id in DATASETS:
            dataset = DATASETS[dataset_id]
            
            # Update tile URL if ready
            if status == "ready" and hasattr(dataset, 'image_url'):
                try:
                    tile_url_template = self.get_tile_url_template(
                        dataset.image_url,
                        base_url="http://localhost:8000"
                    )
                    tile_id = self._generate_tile_id(dataset.image_url)
                    
                    # Get zoom levels from tile_info
                    tile_info = self.tile_index.get(tile_id)
                    min_zoom = tile_info.get('min_zoom', 0) if tile_info else 0
                    max_zoom = tile_info.get('max_zoom', 8) if tile_info else 8
                    
                    # Thumbnail URL should use the minimum zoom level
                    thumbnail_url = f"http://localhost:8000/tiles/{tile_id}/{min_zoom}/0/0.png"
                    
                    # Update variant with new zoom levels (Pydantic requires creating new objects)
                    if dataset.variants:
                        old_variant = dataset.variants[0]
                        new_variant = Variant(
                            id=old_variant.id,
                            name=old_variant.name,
                            description=old_variant.description,
                            tile_url_template=tile_url_template,
                            thumbnail_url=thumbnail_url,
                            min_zoom=min_zoom,
                            max_zoom=max_zoom,
                            is_default=old_variant.is_default
                        )
                        
                        # Create new dataset with updated variant (copy all fields)
                        new_dataset = Dataset(
                            id=dataset.id,
                            name=dataset.name,
                            description=dataset.description,
                            source_id=dataset.source_id,
                            category=dataset.category,
                            subject=dataset.subject,
                            projection=dataset.projection,
                            supports_time_series=dataset.supports_time_series,
                            date_range_start=dataset.date_range_start,
                            date_range_end=dataset.date_range_end,
                            default_date=dataset.default_date,
                            variants=[new_variant],
                            available_layers=dataset.available_layers,
                            bbox=dataset.bbox,
                            created_at=dataset.created_at,
                            updated_at=datetime.now(),
                            processing_status=status,
                            tile_id=dataset.tile_id,
                            image_url=dataset.image_url
                        )
                        
                        # Replace in storage
                        DATASETS[dataset_id] = new_dataset
                    
                    logger.info(f"Updated dataset {dataset_id} to ready status with min_zoom={min_zoom}, max_zoom={max_zoom}")
                except Exception as e:
                    logger.error(f"Failed to update dataset URLs: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
    
    def process_image(self, image_url: str, metadata: Dict) -> Dict:
        """
        Synchronous processing (kept for backward compatibility)
        Main processing pipeline: download -> convert to tiles -> update index
        Returns tile information
        """
        tile_id = self._generate_tile_id(image_url)
        
        # Check if already processed
        if self.is_tiled(image_url):
            logger.info(f"Image already tiled: {tile_id}")
            return self.tile_index[tile_id]
        
        # Update processing status
        self.processing_status[tile_id] = {
            "status": "processing",
            "started_at": datetime.now().isoformat(),
            "progress": "downloading"
        }
        
        try:
            # Step 1: Download image
            image_path = self.download_image(image_url, tile_id)
            
            self.processing_status[tile_id]["progress"] = "generating_tiles"
            
            # Step 2: Generate tiles
            tiles_dir, max_zoom = self.generate_tiles(image_path, tile_id)
            
            # Step 3: Update index
            tile_info = {
                "tile_id": tile_id,
                "source_url": image_url,
                "tiles_path": str(tiles_dir.relative_to(self.tiles_dir)),
                "max_zoom": max_zoom,
                "status": "completed",
                "metadata": metadata,
                "created_at": datetime.now().isoformat()
            }
            
            self.tile_index[tile_id] = tile_info
            self._save_tile_index()
            
            # Clear processing status
            if tile_id in self.processing_status:
                del self.processing_status[tile_id]
            
            logger.info(f"Processing completed for {tile_id}")
            return tile_info
            
        except Exception as e:
            logger.error(f"Processing failed for {tile_id}: {e}")
            self.processing_status[tile_id] = {
                "status": "failed",
                "error": str(e),
                "failed_at": datetime.now().isoformat()
            }
            raise
    
    def get_tile_url_template(self, image_url: str, base_url: str = "http://localhost:8000") -> str:
        """Get tile URL template for a processed image"""
        tile_id = self._generate_tile_id(image_url)
        tile_info = self.tile_index.get(tile_id)
        
        if not tile_info or tile_info['status'] != 'completed':
            raise ValueError(f"Tiles not ready for {tile_id}")
        
        # Return URL template that points to our tile serving endpoint
        return f"{base_url}/tiles/{tile_id}/{{z}}/{{x}}/{{y}}.png"
    
    def cleanup_old_tiles(self, days: int = 30):
        """Remove tiles older than specified days (optional maintenance)"""
        # Implementation for cleanup if needed
        pass


# Global instance
tile_processor = TileProcessor()

