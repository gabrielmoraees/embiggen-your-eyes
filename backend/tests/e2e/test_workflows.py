"""
E2E Tests: Frontend User Workflows

This test suite simulates complete frontend user workflows:
1. Discovering celestial bodies and map sources
2. Browsing and selecting datasets and variants
3. Creating and managing saved map views
4. Adding annotations to views
5. Creating collections of views
6. Verifying all tile URLs are accessible

Tests the entire hierarchical structure from a frontend perspective.
"""
import pytest
from fastapi.testclient import TestClient
import requests
from datetime import date
from unittest.mock import patch
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.data.storage import DATASETS
from app.models.enums import SourceId


@pytest.mark.e2e
class TestMapDiscoveryWorkflow:
    """E2E: Test complete map discovery workflow"""
    
    def setup_method(self):
        """Clear custom datasets before each test"""
        custom_ids = [
            dataset_id for dataset_id, dataset in DATASETS.items()
            if dataset.source_id == SourceId.CUSTOM
        ]
        for dataset_id in custom_ids:
            del DATASETS[dataset_id]
    
    def test_discover_categories(self, client: TestClient):
        """E2E: User discovers available celestial bodies"""
        response = client.get("/api/categories")
        assert response.status_code == 200
        
        data = response.json()
        assert "categories" in data
        
        categories = data["categories"]
        assert len(categories) >= 2  # At least Planets and Moons
        
        # Verify each category has required info
        for category in categories:
            assert "id" in category
            assert "name" in category
            assert "dataset_count" in category
            assert "sources" in category
            assert "subjects" in category
            assert category["dataset_count"] > 0
        
        # Verify we have planets and satellites
        category_ids = [c["id"] for c in categories]
        assert "planets" in category_ids
        assert "satellites" in category_ids
        
        print(f"\n✓ Found {len(categories)} categories with subjects")
    
    def test_browse_datasets_for_category(self, client: TestClient):
        """E2E: User selects Moon and browses available datasets"""
        # Step 1: Get Moon datasets
        response = client.get("/api/datasets?subject=moon")
        assert response.status_code == 200
        
        data = response.json()
        datasets = data["datasets"]
        assert len(datasets) >= 2  # Multiple Moon datasets
        
        print(f"\n✓ Found {len(datasets)} Moon datasets:")
        for dataset in datasets:
            print(f"  • {dataset['name']} ({dataset['source_id']})")
            assert "variants" in dataset
            assert len(dataset["variants"]) > 0
    
    def test_select_map_and_view_variants(self, client: TestClient):
        """E2E: User selects a map and views its variants"""
        # Step 1: Get VIIRS SNPP map
        response = client.get("/api/datasets/viirs_snpp")
        assert response.status_code == 200
        
        dataset = response.json()
        assert dataset["name"] == "VIIRS SNPP"
        assert dataset["supports_time_series"] is True
        
        # Step 2: Get variants
        response = client.get("/api/datasets/viirs_snpp/variants")
        assert response.status_code == 200
        
        data = response.json()
        variants = data["variants"]
        assert len(variants) >= 2  # Multiple variants available
        
        print(f"\n✓ VIIRS SNPP has {len(variants)} variants:")
        for variant in variants:
            print(f"  • {variant['name']}")
    
    def test_get_variant_with_resolved_urls(self, client: TestClient):
        """E2E: User gets variant with resolved tile URLs"""
        # Get variant with specific date
        response = client.get("/api/datasets/viirs_snpp/variants/true_color?date_param=2025-10-04")
        assert response.status_code == 200
        
        data = response.json()
        variant = data["variant"]
        
        # Verify URLs are resolved (no {date} placeholder)
        assert "2025-10-04" in variant["tile_url"]
        assert "2025-10-04" in variant["thumbnail_url"]
        assert "{z}" in variant["tile_url"]  # But z/x/y placeholders remain
        assert "{x}" in variant["tile_url"]
        assert "{y}" in variant["tile_url"]
        
        print(f"\n✓ Variant URLs resolved with date: 2025-10-04")


@pytest.mark.e2e
class TestViewWorkflow:
    """E2E: Test user-saved map view workflow"""
    
    def setup_method(self):
        """Clear custom datasets before each test"""
        custom_ids = [
            dataset_id for dataset_id, dataset in DATASETS.items()
            if dataset.source_id == SourceId.CUSTOM
        ]
        for dataset_id in custom_ids:
            del DATASETS[dataset_id]
    
    def test_complete_map_view_lifecycle(self, client: TestClient):
        """E2E: Create, read, update, delete a map view"""
        # Step 1: Create a map view
        view_data = {
            "name": "My Favorite Earth View",
            "description": "Beautiful view of New York",
            "dataset_id": "viirs_snpp",
            "variant_id": "true_color",
            "selected_date": "2025-10-04",
            "center_lat": 40.7128,
            "center_lng": -74.0060,
            "zoom_level": 10
        }
        
        create_response = client.post("/api/views", json=view_data)
        assert create_response.status_code == 200
        
        created_view = create_response.json()
        view_id = created_view["id"]
        assert created_view["name"] == view_data["name"]
        assert created_view["zoom_level"] == 10
        
        print(f"\n✓ Created map view: {created_view['name']}")
        
        # Step 2: Retrieve the view
        get_response = client.get(f"/api/views/{view_id}")
        assert get_response.status_code == 200
        
        retrieved_view = get_response.json()
        assert retrieved_view["id"] == view_id
        assert retrieved_view["name"] == view_data["name"]
        
        print(f"✓ Retrieved map view: {view_id}")
        
        # Step 3: Update the view
        updated_data = view_data.copy()
        updated_data["name"] = "Updated View Name"
        updated_data["zoom_level"] = 12
        
        update_response = client.put(f"/api/views/{view_id}", json=updated_data)
        assert update_response.status_code == 200
        
        updated_view = update_response.json()
        assert updated_view["name"] == "Updated View Name"
        assert updated_view["zoom_level"] == 12
        
        print(f"✓ Updated map view: {updated_view['name']}")
        
        # Step 4: List all views
        list_response = client.get("/api/views")
        assert list_response.status_code == 200
        
        views_data = list_response.json()
        assert views_data["count"] > 0
        assert any(v["id"] == view_id for v in views_data["views"])
        
        print(f"✓ Listed all views: {views_data['count']} total")
        
        # Step 5: Delete the view
        delete_response = client.delete(f"/api/views/{view_id}")
        assert delete_response.status_code == 200
        
        # Verify it's gone
        get_after_delete = client.get(f"/api/views/{view_id}")
        assert get_after_delete.status_code == 404
        
        print(f"✓ Deleted map view: {view_id}")


@pytest.mark.e2e
class TestAnnotationWorkflow:
    """E2E: Test annotation workflow with map views"""
    
    def setup_method(self):
        """Clear custom datasets before each test"""
        custom_ids = [
            dataset_id for dataset_id, dataset in DATASETS.items()
            if dataset.source_id == SourceId.CUSTOM
        ]
        for dataset_id in custom_ids:
            del DATASETS[dataset_id]
    
    def test_add_annotations_to_map_view(self, client: TestClient):
        """E2E: User creates a view and adds annotations to it"""
        # Step 1: Create a map view
        view_data = {
            "name": "Annotated Mars View",
            "dataset_id": "mars_viking",
            "variant_id": "colorized",
            "center_lat": 0.0,
            "center_lng": 0.0,
            "zoom_level": 5
        }
        
        view_response = client.post("/api/views", json=view_data)
        view_id = view_response.json()["id"]
        
        print(f"\n✓ Created map view for annotations: {view_id}")
        
        # Step 2: Add annotations to the view
        annotation1 = {
            "map_view_id": view_id,
            "type": "point",
            "coordinates": [{"lat": 10.0, "lng": 20.0}],
            "text": "Olympus Mons",
            "color": "#FF0000"
        }
        
        ann1_response = client.post("/api/annotations", json=annotation1)
        assert ann1_response.status_code == 200
        ann1_id = ann1_response.json()["id"]
        
        print(f"✓ Added annotation 1: {annotation1['text']}")
        
        annotation2 = {
            "map_view_id": view_id,
            "type": "circle",
            "coordinates": [{"lat": -5.0, "lng": 30.0}],
            "text": "Valles Marineris",
            "color": "#00FF00"
        }
        
        ann2_response = client.post("/api/annotations", json=annotation2)
        assert ann2_response.status_code == 200
        ann2_id = ann2_response.json()["id"]
        
        print(f"✓ Added annotation 2: {annotation2['text']}")
        
        # Step 3: Get all annotations for the view
        filter_response = client.get(f"/api/annotations?map_view_id={view_id}")
        assert filter_response.status_code == 200
        
        annotations = filter_response.json()["annotations"]
        assert len(annotations) == 2
        
        print(f"✓ Retrieved {len(annotations)} annotations for view")
        
        # Step 4: Update the view to reference annotations
        view_update = view_data.copy()
        view_update["annotation_ids"] = [ann1_id, ann2_id]
        
        update_response = client.put(f"/api/views/{view_id}", json=view_update)
        assert update_response.status_code == 200
        
        updated_view = update_response.json()
        assert len(updated_view["annotation_ids"]) == 2
        
        print(f"✓ Linked annotations to view")


@pytest.mark.e2e
class TestCollectionWorkflow:
    """E2E: Test collection workflow"""
    
    def setup_method(self):
        """Clear custom datasets before each test"""
        custom_ids = [
            dataset_id for dataset_id, dataset in DATASETS.items()
            if dataset.source_id == SourceId.CUSTOM
        ]
        for dataset_id in custom_ids:
            del DATASETS[dataset_id]
    
    def test_create_collection_of_views(self, client: TestClient):
        """E2E: User creates multiple views and groups them in a collection"""
        # Step 1: Create multiple map views
        view_ids = []
        
        views_to_create = [
            {"name": "Earth View 1", "dataset_id": "viirs_snpp", "variant_id": "true_color"},
            {"name": "Mars View 1", "dataset_id": "mars_viking", "variant_id": "colorized"},
            {"name": "Moon View 1", "dataset_id": "moon_opm_basemap", "variant_id": "default"}
        ]
        
        for view_data in views_to_create:
            response = client.post("/api/views", json=view_data)
            view_ids.append(response.json()["id"])
        
        print(f"\n✓ Created {len(view_ids)} map views")
        
        # Step 2: Create a collection
        collection_data = {
            "name": "Solar System Tour",
            "description": "A tour of Earth, Mars, and Moon",
            "view_ids": view_ids
        }
        
        create_response = client.post("/api/collections", json=collection_data)
        assert create_response.status_code == 200
        
        collection = create_response.json()
        collection_id = collection["id"]
        assert len(collection["view_ids"]) == 3
        
        print(f"✓ Created collection: {collection['name']}")
        
        # Step 3: Retrieve the collection
        get_response = client.get(f"/api/collections/{collection_id}")
        assert get_response.status_code == 200
        
        retrieved = get_response.json()
        assert retrieved["name"] == collection_data["name"]
        assert len(retrieved["view_ids"]) == 3
        
        print(f"✓ Retrieved collection with {len(retrieved['view_ids'])} views")


@pytest.mark.e2e
class TestTileAccessibility:
    """E2E: Test that all map variant tiles are accessible"""
    
    def setup_method(self):
        """Clear custom datasets before each test"""
        custom_ids = [
            dataset_id for dataset_id, dataset in DATASETS.items()
            if dataset.source_id == SourceId.CUSTOM
        ]
        for dataset_id in custom_ids:
            del DATASETS[dataset_id]
    
    def test_all_map_variants_have_accessible_tiles(self, client: TestClient):
        """E2E: Verify all map variants return valid image tiles"""
        # Get all datasets
        datasets_response = client.get("/api/datasets")
        datasets = datasets_response.json()["datasets"]
        
        print("\n" + "=" * 60)
        print("TESTING TILE ACCESSIBILITY FOR ALL MAP VARIANTS")
        print("=" * 60)
        
        failed_variants = []
        tested_count = 0
        
        for dataset in datasets:
            dataset_id = dataset["id"]
            dataset_name = dataset["name"]
            supports_time_series = dataset["supports_time_series"]
            
            for variant in dataset["variants"]:
                variant_id = variant["id"]
                tested_count += 1
                
                # Get variant with resolved URLs
                params = {}
                if supports_time_series:
                    params["date_param"] = "2025-10-04"
                
                variant_response = client.get(
                    f"/api/datasets/{dataset_id}/variants/{variant_id}",
                    params=params
                )
                
                if variant_response.status_code != 200:
                    failed_variants.append(f"{dataset_name}/{variant['name']} - HTTP {variant_response.status_code}")
                    continue
                
                variant_data = variant_response.json()["variant"]
                
                # Test tile URL at zoom 0
                tile_url = variant_data["tile_url"].replace("{z}", "0").replace("{y}", "0").replace("{x}", "0")
                
                try:
                    tile_response = requests.head(tile_url, timeout=10)
                    content_type = tile_response.headers.get("content-type", "")
                    
                    if tile_response.status_code != 200:
                        failed_variants.append(f"{dataset_name}/{variant['name']} - Tile HTTP {tile_response.status_code}")
                    elif "image" not in content_type.lower():
                        failed_variants.append(f"{dataset_name}/{variant['name']} - Invalid content-type: {content_type}")
                    else:
                        print(f"  ✓ {dataset_name} / {variant['name']} - {content_type}")
                
                except Exception as e:
                    failed_variants.append(f"{dataset_name}/{variant['name']} - {str(e)}")
        
        print("=" * 60)
        
        if failed_variants:
            print(f"\n❌ FAILED VARIANTS ({len(failed_variants)}):")
            for failure in failed_variants:
                print(f"  - {failure}")
            pytest.fail(f"{len(failed_variants)} variants failed accessibility test")
        else:
            print(f"\n✅ All {tested_count} map variants passed tile accessibility test")


@pytest.mark.e2e
class TestCompleteUserJourney:
    """E2E: Test a complete user journey from discovery to saved view"""
    
    def setup_method(self):
        """Clear custom datasets before each test"""
        custom_ids = [
            dataset_id for dataset_id, dataset in DATASETS.items()
            if dataset.source_id == SourceId.CUSTOM
        ]
        for dataset_id in custom_ids:
            del DATASETS[dataset_id]
    
    def test_complete_user_journey(self, client: TestClient):
        """E2E: Simulate a complete user journey through the application"""
        print("\n" + "=" * 60)
        print("COMPLETE USER JOURNEY TEST")
        print("=" * 60)
        
        # Step 1: User discovers celestial bodies
        print("\n1. User discovers celestial bodies...")
        bodies_response = client.get("/api/categories")
        assert bodies_response.status_code == 200
        bodies = bodies_response.json()["categories"]
        print(f"   ✓ Found {len(bodies)} celestial bodies")
        
        # Step 2: User selects Earth and browses datasets
        print("\n2. User selects Earth and browses datasets...")
        datasets_response = client.get("/api/datasets?subject=earth")
        assert datasets_response.status_code == 200
        earth_datasets = datasets_response.json()["datasets"]
        print(f"   ✓ Found {len(earth_datasets)} Earth datasets")
        
        # Step 3: User selects VIIRS SNPP map
        print("\n3. User selects VIIRS SNPP map...")
        map_response = client.get("/api/datasets/viirs_snpp")
        assert map_response.status_code == 200
        viirs_map = map_response.json()
        print(f"   ✓ Selected: {viirs_map['name']}")
        
        # Step 4: User views variants
        print("\n4. User views available variants...")
        variants_response = client.get("/api/datasets/viirs_snpp/variants")
        assert variants_response.status_code == 200
        variants = variants_response.json()["variants"]
        print(f"   ✓ Found {len(variants)} variants")
        
        # Step 5: User selects true color variant with today's date
        print("\n5. User selects true color variant...")
        variant_response = client.get("/api/datasets/viirs_snpp/variants/true_color?date_param=2025-10-04")
        assert variant_response.status_code == 200
        variant = variant_response.json()["variant"]
        print(f"   ✓ Selected: {variant['name']}")
        print(f"   ✓ Tile URL ready: {variant['tile_url'][:50]}...")
        
        # Step 6: User saves the view
        print("\n6. User saves the map view...")
        view_data = {
            "name": "My Daily Earth View",
            "description": "VIIRS true color for today",
            "dataset_id": "viirs_snpp",
            "variant_id": "true_color",
            "selected_date": "2025-10-04",
            "center_lat": 40.7128,
            "center_lng": -74.0060,
            "zoom_level": 8
        }
        view_response = client.post("/api/views", json=view_data)
        assert view_response.status_code == 200
        saved_view = view_response.json()
        view_id = saved_view["id"]
        print(f"   ✓ Saved view: {saved_view['name']}")
        
        # Step 7: User adds an annotation
        print("\n7. User adds an annotation...")
        annotation_data = {
            "map_view_id": view_id,
            "type": "point",
            "coordinates": [{"lat": 40.7128, "lng": -74.0060}],
            "text": "New York City",
            "color": "#FF0000"
        }
        ann_response = client.post("/api/annotations", json=annotation_data)
        assert ann_response.status_code == 200
        annotation = ann_response.json()
        print(f"   ✓ Added annotation: {annotation['text']}")
        
        # Step 8: User retrieves their saved view
        print("\n8. User retrieves their saved view...")
        get_view_response = client.get(f"/api/views/{view_id}")
        assert get_view_response.status_code == 200
        retrieved_view = get_view_response.json()
        print(f"   ✓ Retrieved: {retrieved_view['name']}")
        
        # Step 9: User lists all their views
        print("\n9. User lists all their saved views...")
        list_response = client.get("/api/views")
        assert list_response.status_code == 200
        all_views = list_response.json()
        print(f"   ✓ Total saved views: {all_views['count']}")
        
        print("\n" + "=" * 60)
        print("✅ COMPLETE USER JOURNEY SUCCESSFUL")
        print("=" * 60)


@pytest.mark.e2e
class TestDataIntegrity:
    """E2E: Test data integrity across the data structure"""
    
    def setup_method(self):
        """Clear custom datasets before each test"""
        custom_ids = [
            dataset_id for dataset_id, dataset in DATASETS.items()
            if dataset.source_id == SourceId.CUSTOM
        ]
        for dataset_id in custom_ids:
            del DATASETS[dataset_id]
    
    def test_all_datasets_have_valid_structure(self, client: TestClient):
        """E2E: Verify all datasets in catalog have valid structure"""
        response = client.get("/api/datasets")
        datasets = response.json()["datasets"]
        
        print(f"\n✓ Testing {len(datasets)} datasets for data integrity...")
        
        for dataset in datasets:
            # Required fields
            assert "id" in dataset
            assert "name" in dataset
            assert "source_id" in dataset
            assert "category" in dataset
            assert "subject" in dataset
            assert "variants" in dataset
            assert "supports_time_series" in dataset
            
            # At least one variant
            assert len(dataset["variants"]) > 0
            
            # If time-series, should have date info
            if dataset["supports_time_series"]:
                assert dataset["default_date"] is not None
            
            # Each variant should have required fields
            for variant in dataset["variants"]:
                assert "id" in variant
                assert "name" in variant
                assert "tile_url_template" in variant
                assert "thumbnail_url" in variant
                assert "{z}" in variant["tile_url_template"]
                assert "{x}" in variant["tile_url_template"]
                assert "{y}" in variant["tile_url_template"]
        
        print(f"✓ All {len(datasets)} datasets have valid structure")
    
    def test_catalog_completeness(self, client: TestClient):
        """E2E: Verify the catalog is complete and consistent"""
        # Get all data
        bodies_response = client.get("/api/categories")
        sources_response = client.get("/api/sources")
        datasets_response = client.get("/api/datasets")
        
        bodies = bodies_response.json()["categories"]
        sources = sources_response.json()["sources"]
        datasets = datasets_response.json()["datasets"]
        
        print(f"\n📊 Catalog Summary:")
        print(f"   • Categories: {len(bodies)}")
        print(f"   • Dataset Sources: {len(sources)}")
        print(f"   • Datasets: {len(datasets)}")
        
        # Count variants
        total_variants = sum(len(m["variants"]) for m in datasets)
        print(f"   • Total Variants: {total_variants}")
        
        # Verify catalog has expected structure
        assert len(bodies) >= 2  # At least Planets and Moons
        assert len(sources) >= 4  # Multiple data sources
        assert len(datasets) >= 7  # Multiple datasets
        assert total_variants >= 9  # Multiple variants
        
        # Verify each category has subjects
        for category in bodies:
            assert "subjects" in category
            assert len(category["subjects"]) > 0
        
        print(f"\n✓ Catalog is complete and consistent")


@pytest.mark.e2e
class TestCustomImageUploadWorkflow:
    """E2E: Test complete custom image upload workflow"""
    
    def setup_method(self):
        """Clear custom datasets before each test"""
        custom_ids = [
            dataset_id for dataset_id, dataset in DATASETS.items()
            if dataset.source_id == SourceId.CUSTOM
        ]
        for dataset_id in custom_ids:
            del DATASETS[dataset_id]
    
    @patch('app.services.dataset_service.tile_processor')
    def test_complete_upload_workflow(self, mock_processor, client: TestClient):
        """
        E2E: Complete workflow from upload to display
        
        Steps:
        1. User creates dataset from image
        2. System processes tiles
        3. Dataset is created
        4. User can view dataset in catalog
        5. User can get tile URLs
        6. User can create a view with the custom image
        """
        print("\n" + "=" * 60)
        print("COMPLETE CUSTOM IMAGE UPLOAD WORKFLOW")
        print("=" * 60)
        
        # Mock tile processor
        mock_processor.is_tiled.return_value = True
        mock_processor.get_tile_info.return_value = {
            "tile_id": "test_workflow",
            "max_zoom": 8,
            "status": "completed"
        }
        mock_processor.get_tile_url_template.return_value = "http://localhost:8000/tiles/test_workflow/{z}/{x}/{y}.png"
        mock_processor._generate_tile_id.return_value = "test_workflow"
        
        # Step 1: Create dataset from image
        print("\n1. User creates dataset from image...")
        upload_response = client.post("/api/datasets", json={
            "url": "https://example.com/my-galaxy.jpg",
            "name": "My Galaxy Image",
            "description": "A beautiful galaxy I photographed",
            "category": "galaxies",
            "subject": "andromeda"
        })
        
        assert upload_response.status_code == 200
        upload_data = upload_response.json()
        
        assert upload_data["success"] is True
        dataset_id = upload_data["dataset_id"]
        print(f"   ✓ Image uploaded, dataset ID: {dataset_id}")
        print(f"   ✓ Status: {upload_data['status']}")
        
        # Step 2: Verify dataset in catalog
        print("\n2. User finds dataset in catalog...")
        catalog_response = client.get("/api/datasets")
        catalog_data = catalog_response.json()
        
        custom_datasets = [d for d in catalog_data["datasets"] if d["id"] == dataset_id]
        assert len(custom_datasets) == 1
        print(f"   ✓ Dataset found in catalog")
        
        # Step 3: Get dataset details
        print("\n3. User views dataset details...")
        dataset_response = client.get(f"/api/datasets/{dataset_id}")
        
        assert dataset_response.status_code == 200
        dataset = dataset_response.json()
        
        assert dataset["name"] == "My Galaxy Image"
        assert dataset["category"] == "galaxies"
        assert dataset["source_id"] == "custom"
        print(f"   ✓ Dataset: {dataset['name']}")
        print(f"   ✓ Category: {dataset['category']}")
        
        # Step 4: Get variant with tile URLs
        print("\n4. User gets tile URLs...")
        variant_response = client.get(f"/api/datasets/{dataset_id}/variants/default")
        
        assert variant_response.status_code == 200
        variant_data = variant_response.json()
        
        variant = variant_data["variant"]
        assert "{z}" in variant["tile_url"]
        assert "{x}" in variant["tile_url"]
        assert "{y}" in variant["tile_url"]
        print(f"   ✓ Tile URL: {variant['tile_url'][:50]}...")
        
        # Step 5: Create a view with the custom image
        print("\n5. User creates a saved view...")
        view_response = client.post("/api/views", json={
            "name": "My Galaxy View",
            "description": "View of my custom galaxy image",
            "dataset_id": dataset_id,
            "variant_id": "default",
            "center_lat": 0.0,
            "center_lng": 0.0,
            "zoom_level": 5
        })
        
        assert view_response.status_code == 200
        view = view_response.json()
        print(f"   ✓ View created: {view['name']}")
        
        # Step 6: Filter custom datasets
        print("\n6. User filters custom datasets...")
        list_response = client.get("/api/datasets?source_id=custom")
        
        assert list_response.status_code == 200
        list_data = list_response.json()
        
        assert list_data["count"] >= 1
        print(f"   ✓ Found {list_data['count']} custom dataset(s)")
        
        print("\n" + "=" * 60)
        print("✓ COMPLETE WORKFLOW SUCCESSFUL")
        print("=" * 60)
    
    @patch('app.services.dataset_service.tile_processor')
    def test_upload_and_delete_workflow(self, mock_processor, client: TestClient):
        """
        E2E: Upload and delete workflow
        
        Steps:
        1. Upload custom image
        2. Verify it exists
        3. Delete the image
        4. Verify it's gone
        """
        print("\n" + "=" * 60)
        print("UPLOAD AND DELETE WORKFLOW")
        print("=" * 60)
        
        # Mock tile processor
        mock_processor.is_tiled.return_value = True
        mock_processor.get_tile_info.return_value = {
            "tile_id": "test_delete_workflow",
            "max_zoom": 8,
            "status": "completed"
        }
        mock_processor.get_tile_url_template.return_value = "http://localhost:8000/tiles/test_delete_workflow/{z}/{x}/{y}.png"
        
        # Step 1: Upload
        print("\n1. Upload custom image...")
        mock_processor._generate_tile_id.return_value = "test_delete_workflow"
        
        upload_response = client.post("/api/datasets", json={
            "url": "https://example.com/temp-image.jpg",
            "name": "Temporary Image",
            "category": "galaxies",
            "subject": "andromeda"
        })
        
        dataset_id = upload_response.json()["dataset_id"]
        print(f"   ✓ Uploaded: {dataset_id}")
        
        # Step 2: Verify exists
        print("\n2. Verify image exists...")
        get_response = client.get(f"/api/datasets/{dataset_id}")
        assert get_response.status_code == 200
        print(f"   ✓ Image exists in catalog")
        
        # Step 3: Delete
        print("\n3. Delete image...")
        delete_response = client.delete(f"/api/datasets/{dataset_id}")
        assert delete_response.status_code == 200
        print(f"   ✓ Image deleted")
        
        # Step 4: Verify gone
        print("\n4. Verify image is gone...")
        get_after_delete = client.get(f"/api/datasets/{dataset_id}")
        assert get_after_delete.status_code == 404
        print(f"   ✓ Image no longer in catalog")
        
        print("\n" + "=" * 60)
        print("✓ DELETE WORKFLOW SUCCESSFUL")
        print("=" * 60)
    
    @patch('app.services.dataset_service.tile_processor')
    def test_multiple_images_workflow(self, mock_processor, client: TestClient):
        """
        E2E: Upload multiple custom images
        
        Steps:
        1. Upload multiple images
        2. List all custom images
        3. Verify all are accessible
        """
        print("\n" + "=" * 60)
        print("MULTIPLE IMAGES WORKFLOW")
        print("=" * 60)
        
        # Mock tile processor
        mock_processor.is_tiled.return_value = True
        mock_processor.get_tile_url_template.return_value = "http://localhost:8000/tiles/test/{z}/{x}/{y}.png"
        
        images = [
            {"url": "https://example.com/img1.jpg", "name": "Image 1"},
            {"url": "https://example.com/img2.jpg", "name": "Image 2"},
            {"url": "https://example.com/img3.jpg", "name": "Image 3"}
        ]
        
        uploaded_ids = []
        
        # Step 1: Upload multiple images
        print("\n1. Upload multiple images...")
        for i, img in enumerate(images, 1):
            mock_processor.get_tile_info.return_value = {
                "tile_id": f"test_multi_{i}",
                "max_zoom": 8,
                "status": "completed"
            }
            mock_processor._generate_tile_id.return_value = f"test_multi_{i}"
            
            response = client.post("/api/datasets", json={
                "url": img["url"],
                "name": img["name"],
                "category": "galaxies",
                "subject": "andromeda"
            })
            
            assert response.status_code == 200
            dataset_id = response.json()["dataset_id"]
            uploaded_ids.append(dataset_id)
            print(f"   ✓ Uploaded: {img['name']}")
        
        # Step 2: List all custom images
        print("\n2. List all custom images...")
        list_response = client.get("/api/datasets?source_id=custom")
        
        assert list_response.status_code == 200
        list_data = list_response.json()
        
        assert list_data["count"] == 3
        print(f"   ✓ Found {list_data['count']} custom images")
        
        # Step 3: Verify all are accessible
        print("\n3. Verify all images are accessible...")
        for dataset_id in uploaded_ids:
            response = client.get(f"/api/datasets/{dataset_id}")
            assert response.status_code == 200
            print(f"   ✓ {dataset_id} accessible")
        
        print("\n" + "=" * 60)
        print("✓ MULTIPLE IMAGES WORKFLOW SUCCESSFUL")
        print("=" * 60)
    
    def test_dataset_status_endpoint(self, client: TestClient):
        """
        E2E: Test dataset status endpoint functionality
        
        Steps:
        1. Check status of existing built-in dataset
        2. Check status of non-existent dataset
        3. Verify status endpoint structure
        """
        print("\n" + "=" * 60)
        print("DATASET STATUS ENDPOINT TEST")
        print("=" * 60)
        
        # Step 1: Check status of built-in dataset
        print("\n1. Check status of built-in dataset...")
        status_response = client.get("/api/datasets/viirs_snpp/status")
        
        assert status_response.status_code == 200
        status_data = status_response.json()
        
        assert "dataset_id" in status_data
        assert "status" in status_data
        assert status_data["dataset_id"] == "viirs_snpp"
        assert status_data["status"] == "ready"
        print(f"   ✓ Built-in dataset status: {status_data['status']}")
        
        # Step 2: Check non-existent dataset
        print("\n2. Check non-existent dataset...")
        not_found_response = client.get("/api/datasets/nonexistent/status")
        assert not_found_response.status_code == 404
        print(f"   ✓ Returns 404 for non-existent dataset")
        
        # Step 3: Verify status endpoint for all datasets
        print("\n3. Verify status endpoint works for all datasets...")
        datasets_response = client.get("/api/datasets")
        datasets = datasets_response.json()["datasets"]
        
        # Test a few datasets
        tested = 0
        for dataset in datasets[:3]:  # Test first 3
            dataset_id = dataset["id"]
            status_response = client.get(f"/api/datasets/{dataset_id}/status")
            assert status_response.status_code == 200
            status_data = status_response.json()
            assert status_data["dataset_id"] == dataset_id
            assert "status" in status_data
            tested += 1
        
        print(f"   ✓ Tested {tested} datasets, all have working status endpoints")
        
        print("\n" + "=" * 60)
        print("✓ DATASET STATUS ENDPOINT TEST SUCCESSFUL")
        print("=" * 60)
    
    def test_tile_service_dataset_workflow(self, client: TestClient):
        """
        E2E: Complete workflow for tile service dataset
        
        Steps:
        1. User creates dataset from pre-tiled service (no processing needed)
        2. Dataset is ready immediately
        3. User can view dataset in catalog
        4. User can get tile URLs
        5. User can create a view with the dataset
        """
        print("\n" + "=" * 60)
        print("TILE SERVICE DATASET WORKFLOW")
        print("=" * 60)
        
        # Step 1: Create dataset from tile service URL
        print("\n1. User creates dataset from tile service...")
        create_response = client.post("/api/datasets", json={
            "url": "https://tiles.example.com/mars/{z}/{x}/{y}.jpg",
            "name": "Custom Mars Tiles",
            "description": "Pre-tiled Mars imagery from external service",
            "category": "planets",
            "subject": "mars"
        })
        
        assert create_response.status_code == 200
        create_data = create_response.json()
        
        assert create_data["success"] is True
        assert create_data["status"] == "ready"  # Should be ready immediately
        dataset_id = create_data["dataset_id"]
        print(f"   ✓ Dataset created: {dataset_id}")
        print(f"   ✓ Status: {create_data['status']} (no processing needed)")
        
        # Step 2: Verify dataset in catalog
        print("\n2. User finds dataset in catalog...")
        catalog_response = client.get("/api/datasets")
        catalog_data = catalog_response.json()
        
        dataset_ids = [d["id"] for d in catalog_data["datasets"]]
        assert dataset_id in dataset_ids
        print(f"   ✓ Dataset appears in catalog")
        
        # Step 3: Get dataset details
        print("\n3. User gets dataset details...")
        dataset_response = client.get(f"/api/datasets/{dataset_id}")
        
        assert dataset_response.status_code == 200
        dataset = dataset_response.json()
        
        assert dataset["name"] == "Custom Mars Tiles"
        assert dataset["category"] == "planets"
        assert dataset["subject"] == "mars"
        assert dataset["source_id"] == "custom"
        assert len(dataset["variants"]) > 0
        print(f"   ✓ Dataset: {dataset['name']}")
        print(f"   ✓ Category: {dataset['category']}")
        print(f"   ✓ Variants: {len(dataset['variants'])}")
        
        # Step 4: Get variant with tile URLs
        print("\n4. User gets tile URLs...")
        variant_response = client.get(f"/api/datasets/{dataset_id}/variants/default")
        
        assert variant_response.status_code == 200
        variant_data = variant_response.json()
        
        variant = variant_data["variant"]
        assert "{z}" in variant["tile_url"]
        assert "{x}" in variant["tile_url"]
        assert "{y}" in variant["tile_url"]
        assert "tiles.example.com/mars" in variant["tile_url"]
        print(f"   ✓ Tile URL: {variant['tile_url'][:60]}...")
        
        # Step 5: Create a saved view
        print("\n5. User creates a saved view...")
        view_response = client.post("/api/views", json={
            "name": "My Mars Tile View",
            "description": "View of custom Mars tiles",
            "dataset_id": dataset_id,
            "variant_id": "default",
            "center_lat": 0.0,
            "center_lng": 0.0,
            "zoom_level": 5
        })
        
        assert view_response.status_code == 200
        view = view_response.json()
        print(f"   ✓ View created: {view['name']}")
        
        # Step 6: Verify dataset can be filtered
        print("\n6. User filters datasets by category...")
        filter_response = client.get("/api/datasets?category=planets")
        filter_data = filter_response.json()
        
        filtered_ids = [d["id"] for d in filter_data["datasets"]]
        assert dataset_id in filtered_ids
        print(f"   ✓ Dataset appears in filtered results")
        
        # Step 7: Check status (should be ready)
        print("\n7. User checks dataset status...")
        status_response = client.get(f"/api/datasets/{dataset_id}/status")
        
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert status_data["status"] == "ready"
        print(f"   ✓ Status: {status_data['status']}")
        
        print("\n" + "=" * 60)
        print("✓ TILE SERVICE DATASET WORKFLOW SUCCESSFUL")
        print("=" * 60)


class TestLinkAnnotationWorkflow:
    """E2E: Test complete link annotation workflow"""
    
    def test_create_link_between_views(self, client: TestClient):
        """
        E2E: Create link annotations to connect related views
        
        Steps:
        1. User creates first view (Earth hurricane)
        2. User creates second view (Mars dust storm)
        3. User adds link annotation on first view pointing to second
        4. User navigates using the link
        5. User adds bidirectional link back
        6. User creates collection with both views
        """
        print("\n" + "=" * 60)
        print("E2E: LINK ANNOTATION WORKFLOW")
        print("=" * 60)
        
        # Step 1: Create first view (Earth hurricane)
        print("\n1. User creates view of Earth hurricane...")
        view1_data = {
            "name": "Hurricane Milton - Oct 5",
            "description": "Category 4 hurricane",
            "dataset_id": "viirs_snpp",
            "variant_id": "true_color",
            "selected_date": "2025-10-05",
            "center_lat": 25.0,
            "center_lng": -80.0,
            "zoom_level": 6
        }
        
        view1_response = client.post("/api/views", json=view1_data)
        assert view1_response.status_code == 200
        view1 = view1_response.json()
        view1_id = view1["id"]
        print(f"   ✓ View 1 created: {view1['name']}")
        
        # Step 2: Create second view (Mars dust storm)
        print("\n2. User creates view of Mars dust storm...")
        view2_data = {
            "name": "Mars Dust Storm - Olympus Mons",
            "description": "Similar atmospheric phenomenon on Mars",
            "dataset_id": "mars_viking",
            "variant_id": "colorized",
            "center_lat": -14.5,
            "center_lng": 175.4,
            "zoom_level": 6
        }
        
        view2_response = client.post("/api/views", json=view2_data)
        assert view2_response.status_code == 200
        view2 = view2_response.json()
        view2_id = view2["id"]
        print(f"   ✓ View 2 created: {view2['name']}")
        
        # Step 3: Add link annotation on first view pointing to second
        print("\n3. User adds link annotation on Earth view...")
        link_annotation_data = {
            "map_view_id": view1_id,
            "type": "link",
            "coordinates": [{"lat": 25.5, "lng": -80.3}],
            "text": "Compare with Mars dust storm",
            "color": "#0066CC",
            "link_target": {
                "dataset_id": "mars_viking",
                "variant_id": "colorized",
                "center_lat": -14.5,
                "center_lng": 175.4,
                "zoom_level": 6,
                "preserve_zoom": True
            }
        }
        
        link_response = client.post("/api/annotations", json=link_annotation_data)
        assert link_response.status_code == 200
        link_annotation = link_response.json()
        print(f"   ✓ Link annotation created: {link_annotation['text']}")
        print(f"   ✓ Links to: {link_annotation['link_target']['dataset_id']}")
        
        # Step 4: User retrieves annotations for view 1
        print("\n4. User retrieves annotations for Earth view...")
        annotations_response = client.get(f"/api/annotations?map_view_id={view1_id}")
        assert annotations_response.status_code == 200
        annotations_data = annotations_response.json()
        
        assert len(annotations_data["annotations"]) == 1
        assert annotations_data["annotations"][0]["type"] == "link"
        print(f"   ✓ Found {len(annotations_data['annotations'])} link annotation(s)")
        
        # Step 5: Add bidirectional link back from view 2 to view 1
        print("\n5. User adds link back from Mars view...")
        back_link_data = {
            "map_view_id": view2_id,
            "type": "link",
            "coordinates": [{"lat": -14.0, "lng": 175.0}],
            "text": "Compare with Earth hurricane",
            "color": "#0066CC",
            "link_target": {
                "dataset_id": "viirs_snpp",
                "variant_id": "true_color",
                "center_lat": 25.0,
                "center_lng": -80.0,
                "zoom_level": 6,
                "preserve_zoom": True
            }
        }
        
        back_link_response = client.post("/api/annotations", json=back_link_data)
        assert back_link_response.status_code == 200
        print(f"   ✓ Bidirectional link created")
        
        # Step 6: Create collection with both views
        print("\n6. User creates collection with both views...")
        collection_data = {
            "name": "Weather Phenomena Comparison",
            "description": "Comparing atmospheric storms on Earth and Mars",
            "view_ids": [view1_id, view2_id]
        }
        
        collection_response = client.post("/api/collections", json=collection_data)
        assert collection_response.status_code == 200
        collection = collection_response.json()
        print(f"   ✓ Collection created: {collection['name']}")
        print(f"   ✓ Contains {len(collection['view_ids'])} views with interconnected links")
        
        print("\n" + "=" * 60)
        print("✓ LINK ANNOTATION WORKFLOW SUCCESSFUL")
        print("=" * 60)
    
    def test_link_annotation_validation(self, client: TestClient):
        """
        E2E: Test link annotation validation
        
        Steps:
        1. User tries to create link with invalid dataset (fails)
        2. User tries to create link with invalid variant (fails)
        3. User creates valid link (succeeds)
        4. User verifies link target is accessible
        """
        print("\n" + "=" * 60)
        print("E2E: LINK ANNOTATION VALIDATION")
        print("=" * 60)
        
        # Step 1: Try to create link with invalid dataset
        print("\n1. User tries to create link with invalid dataset...")
        invalid_dataset_link = {
            "type": "link",
            "coordinates": [{"lat": 25.0, "lng": -80.0}],
            "text": "Invalid link",
            "link_target": {
                "dataset_id": "nonexistent_dataset",
                "variant_id": "some_variant"
            }
        }
        
        response = client.post("/api/annotations", json=invalid_dataset_link)
        assert response.status_code == 400
        print(f"   ✓ Correctly rejected: {response.json()['detail']}")
        
        # Step 2: Try to create link with invalid variant
        print("\n2. User tries to create link with invalid variant...")
        invalid_variant_link = {
            "type": "link",
            "coordinates": [{"lat": 25.0, "lng": -80.0}],
            "text": "Invalid variant",
            "link_target": {
                "dataset_id": "viirs_snpp",
                "variant_id": "nonexistent_variant"
            }
        }
        
        response = client.post("/api/annotations", json=invalid_variant_link)
        assert response.status_code == 400
        print(f"   ✓ Correctly rejected: {response.json()['detail']}")
        
        # Step 3: Create valid link
        print("\n3. User creates valid link...")
        valid_link = {
            "type": "link",
            "coordinates": [{"lat": 25.0, "lng": -80.0}],
            "text": "Valid link to Mars",
            "link_target": {
                "dataset_id": "mars_viking",
                "variant_id": "colorized"
            }
        }
        
        response = client.post("/api/annotations", json=valid_link)
        assert response.status_code == 200
        link = response.json()
        print(f"   ✓ Link created successfully")
        
        # Step 4: Verify link target is accessible
        print("\n4. User verifies link target is accessible...")
        target_dataset_id = link["link_target"]["dataset_id"]
        target_variant_id = link["link_target"]["variant_id"]
        
        dataset_response = client.get(f"/api/datasets/{target_dataset_id}")
        assert dataset_response.status_code == 200
        print(f"   ✓ Target dataset accessible: {target_dataset_id}")
        
        variant_response = client.get(f"/api/datasets/{target_dataset_id}/variants/{target_variant_id}")
        assert variant_response.status_code == 200
        print(f"   ✓ Target variant accessible: {target_variant_id}")
        
        print("\n" + "=" * 60)
        print("✓ LINK ANNOTATION VALIDATION SUCCESSFUL")
        print("=" * 60)
