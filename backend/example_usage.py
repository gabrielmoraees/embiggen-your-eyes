"""
Example usage of the Embiggen Your Eyes API
Run this after starting the backend server
"""
import requests
from datetime import date, timedelta
import json

BASE_URL = "http://localhost:8000"

def pretty_print(data):
    """Pretty print JSON data"""
    print(json.dumps(data, indent=2, default=str))

def example_search_images():
    """Example: Search for images"""
    print("\n=== SEARCHING FOR IMAGES ===")
    
    response = requests.post(f"{BASE_URL}/api/search/images", json={
        "layer": "MODIS_Terra_CorrectedReflectance_TrueColor",
        "date_start": str(date.today() - timedelta(days=30)),
        "date_end": str(date.today()),
        "limit": 5
    })
    
    images = response.json()
    print(f"Found {len(images)} images")
    pretty_print(images[:2])  # Show first 2
    
    return images

def example_create_annotations(image_id):
    """Example: Create annotations"""
    print("\n=== CREATING ANNOTATIONS ===")
    
    # Point annotation
    response = requests.post(f"{BASE_URL}/api/annotations", json={
        "image_id": image_id,
        "type": "point",
        "coordinates": [{"lat": 40.7128, "lng": -74.0060}],
        "text": "New York City",
        "color": "#FF0000",
        "properties": {"category": "urban", "population": "8M+"}
    })
    annotation1 = response.json()
    
    # Polygon annotation
    response = requests.post(f"{BASE_URL}/api/annotations", json={
        "image_id": image_id,
        "type": "polygon",
        "coordinates": [
            {"lat": 40.7128, "lng": -74.0060},
            {"lat": 40.7580, "lng": -73.9855},
            {"lat": 40.7489, "lng": -73.9680}
        ],
        "text": "Urban area expansion",
        "color": "#00FF00",
        "properties": {"change_type": "urbanization"}
    })
    annotation2 = response.json()
    
    print(f"Created annotations: {annotation1['id']}, {annotation2['id']}")
    pretty_print(annotation1)
    
    return [annotation1, annotation2]

def example_create_links(image_ids):
    """Example: Create links between images"""
    print("\n=== CREATING IMAGE LINKS ===")
    
    if len(image_ids) < 2:
        print("Need at least 2 images to create links")
        return None
    
    response = requests.post(f"{BASE_URL}/api/links", json={
        "source_image_id": image_ids[0],
        "target_image_id": image_ids[1],
        "relationship_type": "temporal_sequence",
        "description": "Weekly progression showing environmental change"
    })
    
    link = response.json()
    print(f"Created link: {link['id']}")
    pretty_print(link)
    
    return link

def example_get_link_graph(image_id):
    """Example: Get network graph of linked images"""
    print("\n=== GETTING LINK GRAPH ===")
    
    response = requests.get(f"{BASE_URL}/api/links/graph/{image_id}")
    graph = response.json()
    
    print(f"Graph for {image_id}:")
    pretty_print(graph)
    
    return graph

def example_create_collection(image_ids):
    """Example: Create a collection"""
    print("\n=== CREATING COLLECTION ===")
    
    response = requests.post(f"{BASE_URL}/api/collections", json={
        "name": "Hurricane Season 2024",
        "description": "Tracking major hurricanes throughout the season",
        "image_ids": image_ids[:3]
    })
    
    collection = response.json()
    print(f"Created collection: {collection['id']}")
    pretty_print(collection)
    
    # Add more images to collection
    response = requests.put(
        f"{BASE_URL}/api/collections/{collection['id']}/images",
        json=image_ids[3:5]
    )
    
    updated_collection = response.json()
    print(f"Updated collection now has {len(updated_collection['image_ids'])} images")
    
    return collection

def example_compare_images(image_ids):
    """Example: Prepare images for comparison"""
    print("\n=== COMPARING IMAGES ===")
    
    if len(image_ids) < 2:
        print("Need at least 2 images to compare")
        return None
    
    response = requests.post(f"{BASE_URL}/api/images/compare", json=image_ids[:3])
    comparison = response.json()
    
    print(f"Comparison ID: {comparison['comparison_id']}")
    print(f"Recommended mode: {comparison['recommended_mode']}")
    pretty_print(comparison)
    
    return comparison

def example_get_suggestions(image_id):
    """Example: Get similar image suggestions"""
    print("\n=== GETTING SUGGESTIONS ===")
    
    response = requests.get(f"{BASE_URL}/api/suggestions/similar/{image_id}")
    suggestions = response.json()
    
    print(f"Found {len(suggestions)} suggestions for {image_id}:")
    pretty_print(suggestions)
    
    return suggestions

def example_get_analytics():
    """Example: Get user activity analytics"""
    print("\n=== GETTING ANALYTICS ===")
    
    response = requests.get(f"{BASE_URL}/api/analytics/user-activity")
    analytics = response.json()
    
    pretty_print(analytics)
    
    return analytics

def run_all_examples():
    """Run all examples in sequence"""
    print("=" * 60)
    print("Embiggen Your Eyes - API Examples")
    print("=" * 60)
    
    try:
        # 1. Search for images
        images = example_search_images()
        
        if not images:
            print("No images found. Cannot continue with examples.")
            return
        
        image_ids = [img["id"] for img in images]
        
        # 2. Create annotations
        annotations = example_create_annotations(image_ids[0])
        
        # 3. Create links between images
        link = example_create_links(image_ids)
        
        # 4. Get link graph
        if link:
            graph = example_get_link_graph(image_ids[0])
        
        # 5. Create collection
        collection = example_create_collection(image_ids)
        
        # 6. Compare images
        comparison = example_compare_images(image_ids)
        
        # 7. Get suggestions
        suggestions = example_get_suggestions(image_ids[0])
        
        # 8. Get analytics
        analytics = example_get_analytics()
        
        print("\n" + "=" * 60)
        print("✅ All examples completed successfully!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to backend server")
        print("Make sure the server is running: python main.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    run_all_examples()

