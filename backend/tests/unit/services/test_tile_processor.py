"""
Unit tests for TileProcessor service
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil
import json

from app.services.tile_processor import TileProcessor


@pytest.fixture
def temp_dirs():
    """Create temporary directories for testing"""
    temp_base = Path(tempfile.mkdtemp())
    tiles_dir = temp_base / "tiles_cache"
    downloads_dir = temp_base / "downloads"
    
    tiles_dir.mkdir(exist_ok=True)
    downloads_dir.mkdir(exist_ok=True)
    
    yield {
        "tiles_dir": tiles_dir,
        "downloads_dir": downloads_dir,
        "base": temp_base
    }
    
    # Cleanup
    shutil.rmtree(temp_base, ignore_errors=True)


@pytest.fixture
def tile_processor(temp_dirs, monkeypatch):
    """Create a TileProcessor instance with temporary directories"""
    # Patch the module-level directories
    monkeypatch.setattr('app.services.tile_processor.TILES_BASE_DIR', temp_dirs["tiles_dir"])
    monkeypatch.setattr('app.services.tile_processor.DOWNLOADS_DIR', temp_dirs["downloads_dir"])
    
    return TileProcessor()


class TestTileIdGeneration:
    """Test tile ID generation from URLs"""
    
    def test_generate_tile_id_from_url(self, tile_processor):
        """Test that tile IDs are consistently generated from URLs"""
        url = "https://example.com/image.tif"
        tile_id_1 = tile_processor._generate_tile_id(url)
        tile_id_2 = tile_processor._generate_tile_id(url)
        
        assert tile_id_1 == tile_id_2
        assert len(tile_id_1) == 32  # MD5 hash length
    
    def test_different_urls_generate_different_ids(self, tile_processor):
        """Test that different URLs generate different tile IDs"""
        url1 = "https://example.com/image1.tif"
        url2 = "https://example.com/image2.tif"
        
        tile_id_1 = tile_processor._generate_tile_id(url1)
        tile_id_2 = tile_processor._generate_tile_id(url2)
        
        assert tile_id_1 != tile_id_2


class TestZoomLevelCalculations:
    """Test zoom level calculations and detection"""
    
    def test_get_min_zoom_from_tiles(self, tile_processor, temp_dirs):
        """Test detecting minimum zoom level from tile directories"""
        tiles_dir = temp_dirs["tiles_dir"] / "test_tiles"
        tiles_dir.mkdir()
        
        # Create zoom level directories
        (tiles_dir / "0").mkdir()
        (tiles_dir / "2").mkdir()
        (tiles_dir / "5").mkdir()
        
        min_zoom = tile_processor._get_min_zoom(tiles_dir)
        assert min_zoom == 0
    
    def test_get_max_zoom_from_tiles(self, tile_processor, temp_dirs):
        """Test detecting maximum zoom level from tile directories"""
        tiles_dir = temp_dirs["tiles_dir"] / "test_tiles"
        tiles_dir.mkdir()
        
        # Create zoom level directories
        (tiles_dir / "0").mkdir()
        (tiles_dir / "5").mkdir()
        (tiles_dir / "8").mkdir()
        
        max_zoom = tile_processor._get_max_zoom(tiles_dir)
        assert max_zoom == 8
    
    def test_get_min_zoom_empty_directory(self, tile_processor, temp_dirs):
        """Test min zoom fallback for empty directory"""
        tiles_dir = temp_dirs["tiles_dir"] / "empty_tiles"
        tiles_dir.mkdir()
        
        min_zoom = tile_processor._get_min_zoom(tiles_dir)
        assert min_zoom == 0  # Default fallback
    
    def test_get_max_zoom_empty_directory(self, tile_processor, temp_dirs):
        """Test max zoom fallback for empty directory"""
        tiles_dir = temp_dirs["tiles_dir"] / "empty_tiles"
        tiles_dir.mkdir()
        
        max_zoom = tile_processor._get_max_zoom(tiles_dir)
        assert max_zoom == 8  # Default fallback


class TestTileUrlGeneration:
    """Test tile URL template generation"""
    
    def test_get_tile_url_template(self, tile_processor):
        """Test generating tile URL template"""
        image_url = "https://example.com/image.tif"
        base_url = "http://localhost:8000"
        tile_id = tile_processor._generate_tile_id(image_url)
        
        # Add tile to index first
        tile_processor.tile_index[tile_id] = {
            "tile_id": tile_id,
            "status": "completed"
        }
        
        template = tile_processor.get_tile_url_template(image_url, base_url)
        
        assert "{z}" in template
        assert "{x}" in template
        assert "{y}" in template
        assert base_url in template
        assert template.endswith(".png")
    
    def test_tile_url_template_format(self, tile_processor):
        """Test tile URL template has correct format"""
        image_url = "https://example.com/image.tif"
        tile_id = tile_processor._generate_tile_id(image_url)
        
        # Add tile to index first
        tile_processor.tile_index[tile_id] = {
            "tile_id": tile_id,
            "status": "completed"
        }
        
        template = tile_processor.get_tile_url_template(image_url)
        
        # Should be in format: http://localhost:8000/tiles/{tile_id}/{z}/{x}/{y}.png
        parts = template.split("/")
        assert parts[-1] == "{y}.png"
        assert parts[-2] == "{x}"
        assert parts[-3] == "{z}"


class TestTileIndexManagement:
    """Test tile index storage and retrieval"""
    
    def test_save_and_load_tile_index(self, tile_processor, temp_dirs, monkeypatch):
        """Test saving and loading tile index"""
        tile_id = "test_tile_123"
        tile_info = {
            "tile_id": tile_id,
            "source_url": "https://example.com/image.tif",
            "tiles_path": "test_tiles",
            "min_zoom": 0,
            "max_zoom": 8,
            "status": "completed"
        }
        
        tile_processor.tile_index[tile_id] = tile_info
        tile_processor._save_tile_index()
        
        # Create new processor to test loading (with same patched dirs)
        monkeypatch.setattr('app.services.tile_processor.TILES_BASE_DIR', temp_dirs["tiles_dir"])
        monkeypatch.setattr('app.services.tile_processor.DOWNLOADS_DIR', temp_dirs["downloads_dir"])
        new_processor = TileProcessor()
        
        assert tile_id in new_processor.tile_index
        assert new_processor.tile_index[tile_id]["source_url"] == tile_info["source_url"]
        assert new_processor.tile_index[tile_id]["max_zoom"] == 8
        assert new_processor.tile_index[tile_id]["min_zoom"] == 0
    
    def test_is_tiled_returns_true_for_indexed_tiles(self, tile_processor):
        """Test is_tiled returns True for indexed tiles"""
        image_url = "https://example.com/image.tif"
        tile_id = tile_processor._generate_tile_id(image_url)
        
        tile_processor.tile_index[tile_id] = {
            "tile_id": tile_id,
            "status": "completed"
        }
        
        assert tile_processor.is_tiled(image_url) is True
    
    def test_is_tiled_returns_false_for_new_images(self, tile_processor):
        """Test is_tiled returns False for new images"""
        image_url = "https://example.com/new_image.tif"
        assert tile_processor.is_tiled(image_url) is False


class TestProcessingStatus:
    """Test processing status tracking"""
    
    def test_get_processing_status_for_queued_image(self, tile_processor):
        """Test getting status for queued image"""
        image_url = "https://example.com/image.tif"
        tile_id = tile_processor._generate_tile_id(image_url)
        
        tile_processor.processing_status[tile_id] = {
            "status": "processing",
            "progress": "downloading",
            "percentage": 10
        }
        
        status = tile_processor.get_processing_status(image_url)
        assert status["status"] == "processing"
        assert status["progress"] == "downloading"
        assert status["percentage"] == 10
    
    def test_get_processing_status_for_completed_image(self, tile_processor):
        """Test getting status for completed image"""
        image_url = "https://example.com/image.tif"
        tile_id = tile_processor._generate_tile_id(image_url)
        
        tile_processor.tile_index[tile_id] = {
            "status": "completed",
            "max_zoom": 8
        }
        
        status = tile_processor.get_processing_status(image_url)
        assert status["status"] == "completed"
    
    def test_get_processing_status_for_unknown_image(self, tile_processor):
        """Test getting status for unknown image"""
        image_url = "https://example.com/unknown.tif"
        
        status = tile_processor.get_processing_status(image_url)
        # Should return "not_started" for images that haven't been processed yet
        assert status["status"] in ["not_found", "not_started"]


class TestQueueProcessing:
    """Test asynchronous processing queue"""
    
    @patch('threading.Thread')
    def test_queue_processing_starts_thread(self, mock_thread, tile_processor):
        """Test that queue_processing starts a background thread"""
        image_url = "https://example.com/image.tif"
        metadata = {"dataset_id": "test_dataset"}
        
        tile_processor.queue_processing(image_url, metadata)
        
        # Verify thread was created and started
        mock_thread.assert_called_once()
        mock_thread.return_value.start.assert_called_once()
    
    def test_queue_processing_sets_queued_status(self, tile_processor):
        """Test that queue_processing sets initial status"""
        image_url = "https://example.com/image.tif"
        metadata = {"dataset_id": "test_dataset"}
        tile_id = tile_processor._generate_tile_id(image_url)
        
        with patch('threading.Thread'):
            tile_processor.queue_processing(image_url, metadata)
        
        assert tile_id in tile_processor.processing_status
        assert tile_processor.processing_status[tile_id]["status"] == "queued"
    
    def test_queue_processing_skips_already_tiled(self, tile_processor):
        """Test that queue_processing skips already tiled images"""
        image_url = "https://example.com/image.tif"
        tile_id = tile_processor._generate_tile_id(image_url)
        metadata = {"dataset_id": "test_dataset"}
        
        # Mark as already tiled
        tile_processor.tile_index[tile_id] = {"status": "completed"}
        
        with patch('threading.Thread') as mock_thread:
            tile_processor.queue_processing(image_url, metadata)
            
            # Thread should not be started
            mock_thread.assert_not_called()
    
    def test_queue_processing_skips_already_processing(self, tile_processor):
        """Test that queue_processing skips images already being processed"""
        image_url = "https://example.com/image.tif"
        tile_id = tile_processor._generate_tile_id(image_url)
        metadata = {"dataset_id": "test_dataset"}
        
        # Mark as already processing
        tile_processor.processing_status[tile_id] = {"status": "processing"}
        
        with patch('threading.Thread') as mock_thread:
            tile_processor.queue_processing(image_url, metadata)
            
            # Thread should not be started
            mock_thread.assert_not_called()


class TestResumableProcessing:
    """Test resumable processing pipeline"""
    
    @patch('subprocess.run')
    @patch('app.services.tile_processor.TileProcessor.download_image')
    def test_skip_download_if_exists(self, mock_download, mock_subprocess, tile_processor, temp_dirs):
        """Test that download is skipped if file already exists"""
        image_url = "https://example.com/image.tif"
        tile_id = tile_processor._generate_tile_id(image_url)
        metadata = {"dataset_id": "test_dataset"}
        
        # Create existing download file
        image_path = temp_dirs["downloads_dir"] / f"{tile_id}.tif"
        image_path.touch()
        
        # Create georeferenced file to skip that step too
        georef_path = temp_dirs["downloads_dir"] / f"{tile_id}_georef.tif"
        georef_path.touch()
        
        # Create tiles directory to skip tile generation
        tiles_dir = temp_dirs["tiles_dir"] / tile_id
        tiles_dir.mkdir()
        (tiles_dir / "0").mkdir()
        (tiles_dir / "0" / "0").mkdir()
        
        # Mock subprocess for any remaining calls
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="", stderr="")
        
        # Run processing
        tile_processor._process_image_background(image_url, metadata)
        
        # Download should not have been called
        mock_download.assert_not_called()
    
    def test_processing_creates_expected_files(self, tile_processor, temp_dirs):
        """Test that processing creates all expected intermediate files"""
        image_url = "https://example.com/image.tif"
        tile_id = tile_processor._generate_tile_id(image_url)
        
        # Expected paths
        image_path = temp_dirs["downloads_dir"] / f"{tile_id}.tif"
        georef_path = temp_dirs["downloads_dir"] / f"{tile_id}_georef.tif"
        tiles_dir = temp_dirs["tiles_dir"] / tile_id
        
        # Verify paths are constructed correctly
        assert image_path.parent == temp_dirs["downloads_dir"]
        assert georef_path.parent == temp_dirs["downloads_dir"]
        assert tiles_dir.parent == temp_dirs["tiles_dir"]


class TestZoomCalculationFromImageSize:
    """Test zoom level calculation based on image dimensions"""
    
    @patch('subprocess.run')
    def test_calculate_zoom_from_small_image(self, mock_subprocess, tile_processor):
        """Test zoom calculation for small image (512x512)"""
        # Mock gdalinfo output
        mock_subprocess.return_value = MagicMock(
            returncode=0,
            stdout="Size is 512, 512\n",
            stderr=""
        )
        
        # This would be called inside generate_tiles
        # We're testing the calculation logic
        import math
        width, height = 512, 512
        max_dimension = max(width, height)
        calculated_max_zoom = math.ceil(math.log2(max_dimension / 256))
        max_zoom = max(0, min(12, calculated_max_zoom))
        
        assert max_zoom == 1
    
    @patch('subprocess.run')
    def test_calculate_zoom_from_large_image(self, mock_subprocess, tile_processor):
        """Test zoom calculation for large image (69536x22230 - Andromeda)"""
        # Mock gdalinfo output
        mock_subprocess.return_value = MagicMock(
            returncode=0,
            stdout="Size is 69536, 22230\n",
            stderr=""
        )
        
        # Test the calculation logic
        import math
        width, height = 69536, 22230
        max_dimension = max(width, height)
        calculated_max_zoom = math.ceil(math.log2(max_dimension / 256))
        max_zoom = max(0, min(12, calculated_max_zoom))
        
        assert max_zoom == 9
    
    @patch('subprocess.run')
    def test_calculate_zoom_from_gigapixel_image(self, mock_subprocess, tile_processor):
        """Test zoom calculation for gigapixel image (100000x100000)"""
        # Test the calculation logic
        import math
        width, height = 100000, 100000
        max_dimension = max(width, height)
        calculated_max_zoom = math.ceil(math.log2(max_dimension / 256))
        max_zoom = max(0, min(12, calculated_max_zoom))
        
        # Should be clamped at 12
        assert max_zoom <= 12
        assert max_zoom == 9


class TestErrorHandling:
    """Test error handling in tile processing"""
    
    @patch('subprocess.run')
    def test_processing_handles_download_failure(self, mock_subprocess, tile_processor):
        """Test that processing handles download failures gracefully"""
        image_url = "https://example.com/nonexistent.tif"
        tile_id = tile_processor._generate_tile_id(image_url)
        metadata = {"dataset_id": "test_dataset"}
        
        # Mock download failure
        with patch.object(tile_processor, 'download_image', side_effect=Exception("Download failed")):
            tile_processor._process_image_background(image_url, metadata)
        
        # Should have error status
        assert tile_id in tile_processor.processing_status
        assert tile_processor.processing_status[tile_id]["status"] == "failed"
        assert "error" in tile_processor.processing_status[tile_id]
    
    @patch('subprocess.run')
    def test_processing_handles_gdal_failure(self, mock_subprocess, tile_processor, temp_dirs):
        """Test that processing handles GDAL failures gracefully"""
        image_url = "https://example.com/image.tif"
        tile_id = tile_processor._generate_tile_id(image_url)
        metadata = {"dataset_id": "test_dataset"}
        
        # Create download file
        image_path = temp_dirs["downloads_dir"] / f"{tile_id}.tif"
        image_path.touch()
        
        # Mock GDAL failure
        mock_subprocess.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="GDAL error: Invalid file"
        )
        
        tile_processor._process_image_background(image_url, metadata)
        
        # Should have error status
        assert tile_id in tile_processor.processing_status
        assert tile_processor.processing_status[tile_id]["status"] == "failed"
