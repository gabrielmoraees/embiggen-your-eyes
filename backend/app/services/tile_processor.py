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
        """Download source image from URL"""
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
        
        with open(local_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
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
            cmd = [
                gdal2tiles_cmd,
                '--profile=raster',  # Raster profile for non-georeferenced images
                '--zoom=0-8',  # Reasonable zoom range for web
                '--processes=4',  # Use multiple cores
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
        # Try different possible locations
        possible_commands = [
            'gdal2tiles.py',
            'gdal2tiles',
            '/usr/local/bin/gdal2tiles.py',
            '/opt/homebrew/bin/gdal2tiles.py',
            'python3 -m gdal2tiles'
        ]
        
        for cmd in possible_commands:
            try:
                result = subprocess.run(
                    f"{cmd} --help",
                    shell=True,
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return cmd
            except:
                continue
        
        raise RuntimeError(
            "gdal2tiles.py not found. Please install GDAL: "
            "pip install gdal or brew install gdal"
        )
    
    def _get_max_zoom(self, tiles_dir: Path) -> int:
        """Determine maximum zoom level from generated tiles"""
        zoom_dirs = [d for d in tiles_dir.iterdir() if d.is_dir() and d.name.isdigit()]
        if not zoom_dirs:
            return 5  # Default fallback
        return max(int(d.name) for d in zoom_dirs)
    
    def process_image(self, image_url: str, metadata: Dict) -> Dict:
        """
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

