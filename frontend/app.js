// NASA GIBS Configuration  
// Using REST tile URL format
const GIBS_URL_TEMPLATE = 'https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/{layer}/default/{time}/GoogleMapsCompatible_Level9/{z}/{y}/{x}.jpg';

// Get a date from 3 days ago (GIBS has 24-48 hour delay)
function getDefaultDate() {
    const date = new Date();
    date.setDate(date.getDate() - 3);
    return date.toISOString().split('T')[0];
}

// Application State
const AppState = {
    currentLayer: 'MODIS_Terra_CorrectedReflectance_TrueColor',
    currentDate: getDefaultDate(),
    markers: [],
    markerCounter: 0,
    addMarkerMode: false
};

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
let gibsLayer = createGIBSLayer(AppState.currentLayer, AppState.currentDate);
gibsLayer.addTo(map);

// Add attribution
map.attributionControl.addAttribution('Imagery provided by NASA GIBS');

// Function to create GIBS tile layer
function createGIBSLayer(layer, date) {
    // Special handling for static layers
    let actualDate = date;
    if (layer === 'BlueMarble_NextGeneration') {
        actualDate = '2004-08-01'; // Blue Marble uses fixed date
    }
    
    // Build tile URL from template
    const url = GIBS_URL_TEMPLATE
        .replace('{layer}', layer)
        .replace('{time}', actualDate);
    
    const tileLayer = L.tileLayer(url, {
        attribution: '&copy; NASA GIBS',
        tileSize: 256,
        noWrap: false,
        minZoom: 0,
        maxZoom: 9,
        bounds: [[-85.0511, -180], [85.0511, 180]]
    });
    
    // Add error handling
    let tilesLoaded = 0;
    let tilesErrored = 0;
    
    tileLayer.on('tileerror', function(error) {
        tilesErrored++;
        console.error('Tile loading error:', error);
        
        const loadingStatus = document.getElementById('loading-status');
        if (loadingStatus) {
            loadingStatus.textContent = '⚠️ Some tiles failed to load';
            loadingStatus.style.color = '#FC3D21';
        }
        
        if (tilesErrored > 5) {
            console.log('Multiple tile errors detected. Troubleshooting tips:');
            console.log('1. Try "Blue Marble" layer (always available)');
            console.log('2. Choose a date from 3-4 days ago');
            console.log('3. Check your internet connection');
            console.log('4. Some layers may not have recent data');
        }
    });
    
    tileLayer.on('tileload', function() {
        tilesLoaded++;
        if (tilesLoaded === 1) {
            console.log('✓ Tiles loading successfully from NASA GIBS');
            const loadingStatus = document.getElementById('loading-status');
            if (loadingStatus) {
                loadingStatus.textContent = '✓ Tiles loaded';
                loadingStatus.style.color = '#0B3D91';
                setTimeout(() => {
                    loadingStatus.style.display = 'none';
                }, 3000);
            }
        }
    });
    
    return tileLayer;
}

// Function to update the layer
function updateLayer() {
    // Reset loading status
    const loadingStatus = document.getElementById('loading-status');
    if (loadingStatus) {
        loadingStatus.textContent = '⏳ Loading tiles...';
        loadingStatus.style.color = '#FC3D21';
        loadingStatus.style.display = 'inline';
    }
    
    map.removeLayer(gibsLayer);
    gibsLayer = createGIBSLayer(AppState.currentLayer, AppState.currentDate);
    gibsLayer.addTo(map);
    
    console.log(`Loading layer: ${AppState.currentLayer}, Date: ${AppState.currentDate}`);
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
map.on('click', function(e) {
    if (AppState.addMarkerMode) {
        addMarker(e.latlng);
        AppState.addMarkerMode = false;
        document.getElementById('add-marker').textContent = 'Add Marker';
        document.getElementById('add-marker').style.background = '#0B3D91';
        map.getContainer().style.cursor = '';
    }
});

// Function to add a marker
function addMarker(latlng, name = null) {
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
        leafletMarker: marker
    };
    
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

// Function to remove a marker
window.removeMarker = function(markerId) {
    const markerIndex = AppState.markers.findIndex(m => m.id === markerId);
    if (markerIndex > -1) {
        map.removeLayer(AppState.markers[markerIndex].leafletMarker);
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

// Add some example markers for demonstration (optional - comment out if not needed)
setTimeout(() => {
    addMarker(L.latLng(40.7128, -74.0060), 'New York');
    addMarker(L.latLng(51.5074, -0.1278), 'London');
    addMarker(L.latLng(35.6762, 139.6503), 'Tokyo');
}, 1000);

console.log('Embiggen Your Eyes - NASA Space Apps Challenge 2025');
console.log('Map initialized successfully!');
console.log('Keyboard shortcuts: M - Add marker, P - Toggle panel');

