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


@pytest.mark.e2e
class TestMapDiscoveryWorkflow:
    """E2E: Test complete map discovery workflow"""
    
    def test_discover_categories(self, client: TestClient):
        """E2E: User discovers available celestial bodies"""
        response = client.get("/api/categories")
        assert response.status_code == 200
        
        data = response.json()
        assert "categories" in data
        
        categories = data["categories"]
        assert len(categories) == 2  # Planets, Moons
        
        # Verify each category has required info
        for category in categories:
            assert "id" in category
            assert "name" in category
            assert "dataset_count" in category
            assert "sources" in category
            assert "subjects" in category
            assert category["dataset_count"] > 0
        
        # Verify we have planets and moons
        category_ids = [c["id"] for c in categories]
        assert "planets" in category_ids
        assert "moons" in category_ids
        
        print(f"\n✓ Found {len(categories)} categories with subjects")
    
    def test_browse_datasets_for_category(self, client: TestClient):
        """E2E: User selects Moon and browses available datasets"""
        # Step 1: Get Moon datasets
        response = client.get("/api/datasets?subject=moon")
        assert response.status_code == 200
        
        data = response.json()
        datasets = data["datasets"]
        assert len(datasets) == 2  # OPM Basemap + USGS Geologic
        
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
        assert len(variants) == 2  # True color and false color
        
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
        
        # Verify counts match
        assert len(bodies) == 2  # Planets, Moons
        assert len(sources) >= 4  # At least NASA GIBS, Trek, OPM, USGS
        assert len(datasets) == 7  # Our current catalog
        assert total_variants == 9  # All variants
        
        # Verify each category has subjects
        for category in bodies:
            assert "subjects" in category
            assert len(category["subjects"]) > 0
        
        print(f"\n✓ Catalog is complete and consistent")
