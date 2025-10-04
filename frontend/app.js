// Backend API Configuration
const BACKEND_URL = 'http://localhost:8000';

// Get a date from 3 days ago (GIBS has 24-48 hour delay)
function getDefaultDate() {
    const date = new Date();
    date.setDate(date.getDate() - 3);
    return date.toISOString().split('T')[0];
}

// Application State
const AppState = {
    currentLayer: 'VIIRS_SNPP_CorrectedReflectance_TrueColor',
    currentDate: getDefaultDate(),
    currentImage: null,
    markers: [],
    annotations: [],
    markerCounter: 0,
    addMarkerMode: false,
    images: [],
    collections: [],
    links: []
};

// API Helper Functions
async function apiRequest(endpoint, options = {}) {
    try {
        const response = await fetch(`${BACKEND_URL}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status} ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Request failed:', error);
        showError(`API Error: ${error.message}`);
        throw error;
    }
}

function showError(message) {
    const loadingStatus = document.getElementById('loading-status');
    if (loadingStatus) {
        loadingStatus.textContent = `❌ ${message}`;
        loadingStatus.style.color = '#FC3D21';
        loadingStatus.style.display = 'inline';
    }
}

function showSuccess(message) {
    const loadingStatus = document.getElementById('loading-status');
    if (loadingStatus) {
        loadingStatus.textContent = `✓ ${message}`;
        loadingStatus.style.color = '#0B3D91';
        loadingStatus.style.display = 'inline';
        setTimeout(() => {
            loadingStatus.style.display = 'none';
        }, 3000);
    }
}

// Initialize the map
const map = L.map('map', {
    center: [0, 0],
    zoom: 2,
    minZoom: 1,
    maxZoom: 9,
    zoomControl: true,
    attributionControl: true
});

// Create the NASA GIBS tile layer
let gibsLayer = null;

// Add attribution
map.attributionControl.addAttribution('Imagery provided by NASA GIBS');

// API Functions for Backend Integration

async function searchImages(layer, dateStart, dateEnd, limit = 1) {
    const loadingStatus = document.getElementById('loading-status');
    if (loadingStatus) {
        loadingStatus.textContent = '⏳ Searching images...';
        loadingStatus.style.color = '#FC3D21';
        loadingStatus.style.display = 'inline';
    }
    
    try {
        const images = await apiRequest('/api/search/images', {
            method: 'POST',
            body: JSON.stringify({
                layer: layer,
                date_start: dateStart,
                date_end: dateEnd,
                projection: 'epsg3857',
                limit: limit
            })
        });
        
        console.log(`Found ${images.length} images from backend`);
        AppState.images = images;
        
        if (images.length > 0) {
            showSuccess(`Found ${images.length} images`);
            return images;
        } else {
            showError('No images found');
            return [];
        }
    } catch (error) {
        console.error('Failed to search images:', error);
        return [];
    }
}

async function loadAnnotations(imageId) {
    try {
        const annotations = await apiRequest(`/api/annotations/image/${imageId}`);
        AppState.annotations = annotations;
        console.log(`Loaded ${annotations.length} annotations for image ${imageId}`);
        displayAnnotations(annotations);
        return annotations;
    } catch (error) {
        console.error('Failed to load annotations:', error);
        return [];
    }
}

async function createAnnotation(imageId, type, coordinates, text, color = '#FF0000', properties = {}) {
    try {
        const annotation = await apiRequest('/api/annotations', {
            method: 'POST',
            body: JSON.stringify({
                image_id: imageId,
                type: type,
                coordinates: coordinates,
                text: text,
                color: color,
                properties: properties
            })
        });
        
        AppState.annotations.push(annotation);
        showSuccess('Annotation created');
        console.log('Created annotation:', annotation);
        return annotation;
    } catch (error) {
        console.error('Failed to create annotation:', error);
        return null;
    }
}

async function deleteAnnotation(annotationId) {
    try {
        await apiRequest(`/api/annotations/${annotationId}`, {
            method: 'DELETE'
        });
        
        AppState.annotations = AppState.annotations.filter(a => a.id !== annotationId);
        showSuccess('Annotation deleted');
        return true;
    } catch (error) {
        console.error('Failed to delete annotation:', error);
        return false;
    }
}

function displayAnnotations(annotations) {
    // Clear existing annotation layers (keep markers separate)
    map.eachLayer(layer => {
        if (layer.options && layer.options.isAnnotation) {
            map.removeLayer(layer);
        }
    });
    
    annotations.forEach(ann => {
        let layer;
        
        if (ann.type === 'point') {
            layer = L.circleMarker([ann.coordinates[0].lat, ann.coordinates[0].lng], {
                color: ann.color,
                fillColor: ann.color,
                fillOpacity: 0.5,
                radius: 8,
                isAnnotation: true
            });
        } else if (ann.type === 'polygon') {
            const coords = ann.coordinates.map(c => [c.lat, c.lng]);
            layer = L.polygon(coords, {
                color: ann.color,
                fillOpacity: 0.3,
                isAnnotation: true
            });
        } else if (ann.type === 'rectangle') {
            const bounds = [[ann.coordinates[0].lat, ann.coordinates[0].lng],
                          [ann.coordinates[1].lat, ann.coordinates[1].lng]];
            layer = L.rectangle(bounds, {
                color: ann.color,
                fillOpacity: 0.3,
                isAnnotation: true
            });
        } else if (ann.type === 'circle') {
            layer = L.circle([ann.coordinates[0].lat, ann.coordinates[0].lng], {
                color: ann.color,
                fillOpacity: 0.3,
                radius: ann.properties.radius || 10000,
                isAnnotation: true
            });
        }
        
        if (layer) {
            layer.bindPopup(`
                <div>
                    <strong>${ann.text || 'Annotation'}</strong><br>
                    Type: ${ann.type}<br>
                    ${ann.properties ? `<small>${JSON.stringify(ann.properties)}</small>` : ''}
                </div>
            `);
            layer.addTo(map);
        }
    });
}

// Function to create GIBS tile layer from backend image metadata
function createGIBSLayerFromImage(imageMetadata) {
    const tileLayer = L.tileLayer(imageMetadata.tile_url, {
        attribution: '&copy; NASA GIBS',
        tileSize: 256,
        noWrap: false,
        minZoom: 0,
        maxZoom: imageMetadata.max_zoom || 9,
        bounds: [[-85.0511, -180], [85.0511, 180]]
    });
    
    // Add error handling
    let tilesLoaded = 0;
    let tilesErrored = 0;
    
    tileLayer.on('tileerror', function(error) {
        tilesErrored++;
        console.error('Tile loading error:', error);
        
        if (tilesErrored === 1) {
            showError('Some tiles failed to load');
        }
        
        if (tilesErrored > 5) {
            console.log('Multiple tile errors detected. Check backend logs.');
        }
    });
    
    tileLayer.on('tileload', function() {
        tilesLoaded++;
        if (tilesLoaded === 1) {
            console.log('✓ Tiles loading successfully from NASA GIBS via backend');
            showSuccess('Tiles loaded');
        }
    });
    
    return tileLayer;
}

// Function to update the layer (using backend API)
async function updateLayer() {
    const loadingStatus = document.getElementById('loading-status');
    if (loadingStatus) {
        loadingStatus.textContent = '⏳ Loading from backend...';
        loadingStatus.style.color = '#FC3D91';
        loadingStatus.style.display = 'inline';
    }
    
    // Search for image using backend API
    const images = await searchImages(
        AppState.currentLayer,
        AppState.currentDate,
        AppState.currentDate,
        1
    );
    
    if (images.length === 0) {
        showError('No images found for this date/layer');
        return;
    }
    
    const imageMetadata = images[0];
    AppState.currentImage = imageMetadata;
    
    console.log('Image metadata from backend:', imageMetadata);
    console.log(`Tile URL: ${imageMetadata.tile_url}`);
    
    // Remove old layer
    if (gibsLayer) {
        map.removeLayer(gibsLayer);
    }
    
    // Create new layer from backend metadata
    gibsLayer = createGIBSLayerFromImage(imageMetadata);
    gibsLayer.addTo(map);
    
    // Load annotations for this image
    await loadAnnotations(imageMetadata.id);
    
    console.log(`Loaded image: ${imageMetadata.id}`);
}

// Event Listeners for Controls
document.getElementById('layer-select').addEventListener('change', function(e) {
    AppState.currentLayer = e.target.value;
    updateLayer();
});

document.getElementById('date-picker').value = AppState.currentDate;
document.getElementById('date-picker').addEventListener('change', function(e) {
    AppState.currentDate = e.target.value;
});

document.getElementById('update-date').addEventListener('click', function() {
    updateLayer();
});

// Toggle Control Panel
document.getElementById('toggle-panel').addEventListener('click', function() {
    document.getElementById('control-panel').classList.toggle('hidden');
});

// Add Marker Mode
document.getElementById('add-marker').addEventListener('click', function() {
    AppState.addMarkerMode = !AppState.addMarkerMode;
    this.textContent = AppState.addMarkerMode ? 'Cancel Adding Marker' : 'Add Marker';
    this.style.background = AppState.addMarkerMode ? '#FC3D21' : '#0B3D91';
    map.getContainer().style.cursor = AppState.addMarkerMode ? 'crosshair' : '';
});

// Clear All Markers
document.getElementById('clear-markers').addEventListener('click', function() {
    if (confirm('Clear all markers?')) {
        AppState.markers.forEach(marker => map.removeLayer(marker.leafletMarker));
        AppState.markers = [];
        updateMarkerList();
    }
});

// Map Click Event - Add Marker
map.on('click', async function(e) {
    if (AppState.addMarkerMode) {
        await addMarker(e.latlng);
        AppState.addMarkerMode = false;
        document.getElementById('add-marker').textContent = 'Add Marker';
        document.getElementById('add-marker').style.background = '#0B3D91';
        map.getContainer().style.cursor = '';
    }
});

// Function to add a marker (now saves to backend as annotation)
async function addMarker(latlng, name = null) {
    const markerName = name || `Marker ${++AppState.markerCounter}`;
    
    // Create custom icon
    const customIcon = L.divIcon({
        className: 'marker-icon',
        iconSize: [20, 20],
        iconAnchor: [10, 10],
        popupAnchor: [0, -10],
        html: `<div style="width: 20px; height: 20px; background: #FC3D21; border: 3px solid white; border-radius: 50%; box-shadow: 0 2px 8px rgba(0,0,0,0.3);"></div>`
    });
    
    const marker = L.marker(latlng, { icon: customIcon }).addTo(map);
    
    // Create popup content
    const popupContent = `
        <div style="text-align: center;">
            <strong>${markerName}</strong><br>
            Lat: ${latlng.lat.toFixed(4)}°<br>
            Lon: ${latlng.lng.toFixed(4)}°
        </div>
    `;
    marker.bindPopup(popupContent);
    
    // Store marker data
    const markerData = {
        id: Date.now(),
        name: markerName,
        latlng: latlng,
        leafletMarker: marker,
        annotationId: null
    };
    
    // Save to backend if we have a current image
    if (AppState.currentImage) {
        const annotation = await createAnnotation(
            AppState.currentImage.id,
            'point',
            [{ lat: latlng.lat, lng: latlng.lng }],
            markerName,
            '#FC3D21',
            { markerType: 'user_marker' }
        );
        
        if (annotation) {
            markerData.annotationId = annotation.id;
            console.log(`Marker saved to backend with annotation ID: ${annotation.id}`);
        }
    }
    
    AppState.markers.push(markerData);
    updateMarkerList();
    
    return marker;
}

// Function to update marker list in UI
function updateMarkerList() {
    const markerList = document.getElementById('marker-list');
    markerList.innerHTML = '';
    
    if (AppState.markers.length === 0) {
        markerList.innerHTML = '<div style="color: #999; font-size: 0.85rem; padding: 8px;">No markers added</div>';
        return;
    }
    
    AppState.markers.forEach(marker => {
        const markerItem = document.createElement('div');
        markerItem.className = 'marker-item';
        markerItem.innerHTML = `
            <span>${marker.name}</span>
            <button onclick="flyToMarker(${marker.id})">Go</button>
            <button onclick="removeMarker(${marker.id})">×</button>
        `;
        markerList.appendChild(markerItem);
    });
}

// Function to fly to a marker with smooth animation
window.flyToMarker = function(markerId) {
    const marker = AppState.markers.find(m => m.id === markerId);
    if (marker) {
        map.flyTo(marker.latlng, 6, {
            duration: 1.5,
            easeLinearity: 0.25
        });
        setTimeout(() => marker.leafletMarker.openPopup(), 1500);
    }
};

// Function to remove a marker (and delete from backend)
window.removeMarker = async function(markerId) {
    const markerIndex = AppState.markers.findIndex(m => m.id === markerId);
    if (markerIndex > -1) {
        const markerData = AppState.markers[markerIndex];
        
        // Delete from backend if it has an annotation ID
        if (markerData.annotationId) {
            await deleteAnnotation(markerData.annotationId);
        }
        
        map.removeLayer(markerData.leafletMarker);
        AppState.markers.splice(markerIndex, 1);
        updateMarkerList();
    }
};

// Update coordinates and zoom level display
map.on('mousemove', function(e) {
    document.getElementById('coordinates').textContent = 
        `Lat: ${e.latlng.lat.toFixed(4)}°, Lon: ${e.latlng.lng.toFixed(4)}°`;
});

map.on('zoomend', function() {
    document.getElementById('zoom-level').textContent = `Zoom: ${map.getZoom()}`;
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Press 'M' to toggle add marker mode
    if (e.key === 'm' || e.key === 'M') {
        document.getElementById('add-marker').click();
    }
    // Press 'P' to toggle panel
    if (e.key === 'p' || e.key === 'P') {
        document.getElementById('toggle-panel').click();
    }
});

// Initialize marker list
updateMarkerList();

// Initialize the application
async function initializeApp() {
    console.log('Embiggen Your Eyes - NASA Space Apps Challenge 2025');
    console.log('Initializing app with backend integration...');
    
    // Test backend connection
    try {
        const response = await fetch(`${BACKEND_URL}/`);
        const data = await response.json();
        console.log('✓ Backend connected:', data);
        showSuccess('Connected to backend');
    } catch (error) {
        console.error('❌ Backend not available:', error);
        showError('Backend not connected - Start backend server!');
        return;
    }
    
    // Load initial image
    await updateLayer();
    
    console.log('Map initialized successfully!');
    console.log('Keyboard shortcuts: M - Add marker, P - Toggle panel');
    console.log('Using backend API at:', BACKEND_URL);
}

// Start the app
initializeApp();

