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
        Returns: (tiles_directory, max_zoom_level)
        """
        logger.info(f"Generating tiles for {image_path}")
        
        output_dir = self.tiles_dir / tile_id
        output_dir.mkdir(exist_ok=True, parents=True)
        
        # Check if gdal2tiles.py is available
        try:
            # Try common locations for gdal2tiles
            gdal2tiles_cmd = self._find_gdal2tiles()
            
            # Run gdal2tiles with raster profile (for non-georeferenced images)
            # Deep space images don't have geospatial metadata, so use raster profile
            # Use --xyz to generate tiles in XYZ/TMS format that Leaflet expects
            cmd = [
                gdal2tiles_cmd,
                '--profile=raster',  # Raster profile for non-georeferenced images
                '--xyz',             # Generate XYZ tiles (compatible with Leaflet)
                '--zoom=0-8',        # Reasonable zoom range for web
                '--processes=4',     # Use multiple cores
                '--webviewer=none',  # Don't generate viewer HTML
                str(image_path),
                str(output_dir)
            ]
            
            logger.info(f"Running: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"gdal2tiles failed: {result.stderr}")
            
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
    
    def _get_max_zoom(self, tiles_dir: Path) -> int:
        """Determine maximum zoom level from generated tiles"""
        zoom_dirs = [d for d in tiles_dir.iterdir() if d.is_dir() and d.name.isdigit()]
        if not zoom_dirs:
            return 5  # Default fallback
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
        thread = threading.Thread(
            target=self._process_image_background,
            args=(image_url, metadata),
            daemon=True
        )
        thread.start()
        logger.info(f"Queued processing for {tile_id}")
    
    def _process_image_background(self, image_url: str, metadata: Dict):
        """Background worker that processes the image"""
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
            
            # Step 1: Download image (0-30%)
            self.processing_status[tile_id].update({
                "progress": "downloading",
                "percentage": 0,
                "message": "Starting download..."
            })
            
            image_path = self.download_image(image_url, tile_id)
            
            # Step 2: Generate tiles (30-100%)
            self.processing_status[tile_id].update({
                "progress": "generating_tiles",
                "percentage": 30,
                "message": "Generating tiles... This may take a few minutes."
            })
            
            tiles_dir, max_zoom = self.generate_tiles(image_path, tile_id)
            
            # Step 3: Finalizing (95%)
            self.processing_status[tile_id].update({
                "progress": "finalizing",
                "percentage": 95,
                "message": "Finalizing..."
            })
            
            # Step 4: Update index
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
            
            # Mark as complete (100%)
            self.processing_status[tile_id].update({
                "progress": "completed",
                "percentage": 100,
                "message": "Processing complete!"
            })
            
            # Clear processing status after a short delay
            import time
            time.sleep(2)
            if tile_id in self.processing_status:
                del self.processing_status[tile_id]
            
            logger.info(f"Processing completed for {tile_id}")
            
            # Update dataset status if dataset_id is in metadata
            if "dataset_id" in metadata:
                self._update_dataset_status(metadata["dataset_id"], "ready")
            
        except Exception as e:
            logger.error(f"Processing failed for {tile_id}: {e}")
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
        
        if dataset_id in DATASETS:
            dataset = DATASETS[dataset_id]
            dataset.processing_status = status
            dataset.updated_at = datetime.now()
            
            # Update tile URL if ready
            if status == "ready" and hasattr(dataset, 'image_url'):
                try:
                    tile_url_template = self.get_tile_url_template(
                        dataset.image_url,
                        base_url="http://localhost:8000"
                    )
                    tile_id = self._generate_tile_id(dataset.image_url)
                    thumbnail_url = f"http://localhost:8000/tiles/{tile_id}/0/0/0.png"
                    
                    # Update variant URLs
                    if dataset.variants:
                        dataset.variants[0].tile_url_template = tile_url_template
                        dataset.variants[0].thumbnail_url = thumbnail_url
                        
                        # Update max_zoom from tile_info
                        tile_info = self.tile_index.get(tile_id)
                        if tile_info:
                            dataset.variants[0].max_zoom = tile_info.get('max_zoom', 8)
                    
                    logger.info(f"Updated dataset {dataset_id} to ready status")
                except Exception as e:
                    logger.error(f"Failed to update dataset URLs: {e}")
    
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

