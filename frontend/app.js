// ============================================================================
// Embiggen Your Eyes - iOS 26 Design Frontend
// Comprehensive backend integration with adaptive UI
// ============================================================================

const BACKEND_URL = 'http://localhost:8000';

// ============================================================================
// Application State
// ============================================================================
const AppState = {
    currentCelestialBody: 'earth',
    currentLayer: null,
    currentDate: getDefaultDate(),
    currentImage: null,
    baseLay: null,
    overlayLayers: [],
    markers: [],
    annotations: [],
    collections: [],
    links: [],
    images: [],
    availableLayers: [],
    compareMode: 'overlay',
    compareImages: [],
    searchHistory: [],
    suggestions: []
};

// ============================================================================
// Utility Functions
// ============================================================================
function getDefaultDate() {
    const date = new Date();
    date.setDate(date.getDate() - 3);
    return date.toISOString().split('T')[0];
}

function showStatus(message, type = 'info') {
    const statusPill = document.getElementById('status-pill');
    const statusText = document.getElementById('status-text');
    const statusDot = statusPill.querySelector('.status-dot');
    
    statusText.textContent = message;
    
    // Update dot color based on type
    const colors = {
        info: '#5AC8FA',
        success: '#34C759',
        error: '#FF3B30',
        warning: '#FF9500'
    };
    
    statusDot.style.background = colors[type] || colors.info;
}

async function apiRequest(endpoint, options = {}) {
    try {
        showStatus('Loading...', 'info');
        const response = await fetch(`${BACKEND_URL}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }
        
        const data = await response.json();
        showStatus('Ready', 'success');
        return data;
    } catch (error) {
        console.error('API Request failed:', error);
        showStatus('Error', 'error');
        throw error;
    }
}

// ============================================================================
// Map Initialization
// ============================================================================
let map = null;
let gibsLayer = null;

function initializeMap() {
    console.log('🗺️ Initializing map with iOS design...');
    
    const mapContainer = document.getElementById('map');
    if (!mapContainer) {
        console.error('❌ Map container not found!');
        return false;
    }
    
    try {
        map = L.map('map', {
            center: [0, 0],
            zoom: 2,
            minZoom: 1,
            maxZoom: 12,
            zoomControl: false,
            attributionControl: true
        });

        map.attributionControl.setPosition('bottomright');
        map.attributionControl.setPrefix('');
    
        // Map event listeners
        map.on('mousemove', (e) => {
            const coordsEl = document.getElementById('coordinates');
            if (coordsEl) {
                coordsEl.textContent = `${e.latlng.lat.toFixed(4)}°, ${e.latlng.lng.toFixed(4)}°`;
            }
        });

        map.on('zoomend', () => {
            const zoomEl = document.getElementById('zoom-level');
            if (zoomEl) {
                zoomEl.textContent = `Zoom: ${map.getZoom()}`;
            }
        });
        
        console.log('✅ Map initialized');
        return true;
    } catch (error) {
        console.error('❌ Error initializing map:', error);
        return false;
    }
}

// ============================================================================
// Backend API Functions
// ============================================================================

async function loadAvailableLayers(celestialBody = null) {
    try {
        const endpoint = celestialBody 
            ? `/api/layers?celestial_body=${celestialBody}`
            : '/api/layers';
        const data = await apiRequest(endpoint);
        AppState.availableLayers = data.layers;
        
        renderLayersList(data.layers);
        
        // Auto-select first layer
        if (data.layers.length > 0 && !AppState.currentLayer) {
            AppState.currentLayer = data.layers[0].value;
        }
        
        console.log(`Loaded ${data.layers.length} layers for ${celestialBody || 'all bodies'}`);
        return data.layers;
    } catch (error) {
        console.error('Failed to load layers:', error);
        return [];
    }
}

async function searchImages(layer, dateStart, dateEnd, celestialBody = 'earth', limit = 1) {
    try {
        const images = await apiRequest('/api/search/images', {
            method: 'POST',
            body: JSON.stringify({
                celestial_body: celestialBody,
                layer: layer,
                date_start: dateStart,
                date_end: dateEnd,
                projection: 'epsg3857',
                limit: limit
            })
        });
        
        AppState.images = images;
        console.log(`Found ${images.length} images`);
        return images;
    } catch (error) {
        console.error('Failed to search images:', error);
        return [];
    }
}

async function loadAnnotations(imageId) {
    try {
        const annotations = await apiRequest(`/api/annotations/image/${imageId}`);
        AppState.annotations = annotations;
        renderAnnotationsList(annotations);
        return annotations;
    } catch (error) {
        console.error('Failed to load annotations:', error);
        return [];
    }
}

async function createAnnotation(imageId, type, coordinates, text, color = '#007AFF') {
    try {
        const annotation = await apiRequest('/api/annotations', {
            method: 'POST',
            body: JSON.stringify({
                image_id: imageId,
                type: type,
                coordinates: coordinates,
                text: text,
                color: color
            })
        });
        
        AppState.annotations.push(annotation);
        renderAnnotationsList(AppState.annotations);
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
        renderAnnotationsList(AppState.annotations);
        return true;
    } catch (error) {
        console.error('Failed to delete annotation:', error);
        return false;
    }
}

async function loadCollections() {
    try {
        const collections = await apiRequest('/api/collections');
        AppState.collections = collections;
        renderCollectionsList(collections);
        return collections;
    } catch (error) {
        console.error('Failed to load collections:', error);
        return [];
    }
}

async function createCollection(name, description) {
    try {
        const collection = await apiRequest('/api/collections', {
            method: 'POST',
            body: JSON.stringify({
                name: name,
                description: description,
                image_ids: []
            })
        });
        
        AppState.collections.push(collection);
        renderCollectionsList(AppState.collections);
        return collection;
    } catch (error) {
        console.error('Failed to create collection:', error);
        return null;
    }
}

async function loadSuggestions(imageId) {
    try {
        const suggestions = await apiRequest(`/api/suggestions/similar/${imageId}`);
        AppState.suggestions = suggestions;
        renderSuggestionsList(suggestions);
        return suggestions;
    } catch (error) {
        console.error('Failed to load suggestions:', error);
        return [];
    }
}

// ============================================================================
// Layer Management
// ============================================================================

function createTileLayer(imageMetadata) {
    const tileLayer = L.tileLayer(imageMetadata.tile_url, {
        attribution: '© NASA',
        tileSize: 256,
        noWrap: AppState.currentCelestialBody === 'earth',
        minZoom: 0,
        maxZoom: imageMetadata.max_zoom || 9,
        bounds: [[-85.0511, -180], [85.0511, 180]]
    });
    
    tileLayer.on('tileload', () => {
        showStatus('Tiles loaded', 'success');
    });
    
    tileLayer.on('tileerror', () => {
        showStatus('Tile load error', 'error');
    });
    
    return tileLayer;
}

async function updateBaseLayer() {
    if (!AppState.currentLayer) return;
    
    const images = await searchImages(
        AppState.currentLayer,
        AppState.currentDate,
        AppState.currentDate,
        AppState.currentCelestialBody,
        1
    );
    
    if (images.length === 0) {
        showStatus('No images found', 'warning');
        return;
    }
    
    const imageMetadata = images[0];
    AppState.currentImage = imageMetadata;
    
    // Remove old base layer
    if (gibsLayer) {
        map.removeLayer(gibsLayer);
    }
    
    // Create new base layer
    gibsLayer = createTileLayer(imageMetadata);
    gibsLayer.addTo(map);
    
    // Update UI
    const baseLayerName = document.getElementById('base-layer-name');
    if (baseLayerName) {
        const layer = AppState.availableLayers.find(l => l.value === AppState.currentLayer);
        baseLayerName.textContent = layer ? layer.display_name : 'Unknown Layer';
    }
    
    // Load annotations
    await loadAnnotations(imageMetadata.id);
    
    // Load suggestions
    if (imageMetadata.id) {
        await loadSuggestions(imageMetadata.id);
    }
    
    console.log(`Loaded image: ${imageMetadata.id}`);
}

async function addOverlayLayer(layer) {
    if (!layer) return;
    
    const images = await searchImages(
        layer,
        AppState.currentDate,
        AppState.currentDate,
        AppState.currentCelestialBody,
        1
    );
    
    if (images.length === 0) {
        showStatus('No overlay images found', 'warning');
        return;
    }
    
    const imageMetadata = images[0];
    const tileLayer = createTileLayer(imageMetadata);
    tileLayer.setOpacity(0.6);
    tileLayer.addTo(map);
    
    AppState.overlayLayers.push({
        layer: layer,
        tileLayer: tileLayer,
        metadata: imageMetadata
    });
    
    renderOverlayLayers();
}

function removeOverlayLayer(index) {
    const overlay = AppState.overlayLayers[index];
    if (overlay) {
        map.removeLayer(overlay.tileLayer);
        AppState.overlayLayers.splice(index, 1);
        renderOverlayLayers();
    }
}

// ============================================================================
// UI Rendering Functions
// ============================================================================

function renderLayersList(layers) {
    const layersList = document.getElementById('layers-list');
    layersList.innerHTML = '';
    
    layers.forEach(layer => {
        const card = document.createElement('div');
        card.className = 'layer-card';
        if (layer.value === AppState.currentLayer) {
            card.classList.add('active');
        }
        
        card.innerHTML = `
            <div class="layer-icon">
                <span class="material-icons-round">terrain</span>
            </div>
            <div class="layer-info">
                <div class="layer-name">${layer.display_name}</div>
                <div class="layer-desc">${layer.type}</div>
            </div>
        `;
        
        card.addEventListener('click', () => {
            AppState.currentLayer = layer.value;
            updateBaseLayer();
            renderLayersList(layers);
        });
        
        layersList.appendChild(card);
    });
}

function renderOverlayLayers() {
    const overlayLayersEl = document.getElementById('overlay-layers');
    
    // Keep base layer, remove old overlays
    const baseLayer = overlayLayersEl.querySelector('.base-layer');
    overlayLayersEl.innerHTML = '';
    overlayLayersEl.appendChild(baseLayer);
    
    AppState.overlayLayers.forEach((overlay, index) => {
        const layer = AppState.availableLayers.find(l => l.value === overlay.layer);
        const item = document.createElement('div');
        item.className = 'overlay-item';
        item.innerHTML = `
            <span class="material-icons-round">layers</span>
            <div class="overlay-info">
                <div class="overlay-name">Overlay ${index + 1}</div>
                <div class="overlay-desc">${layer ? layer.display_name : 'Unknown'}</div>
            </div>
            <button class="icon-btn" onclick="removeOverlayLayer(${index})">
                <span class="material-icons-round">close</span>
            </button>
        `;
        overlayLayersEl.appendChild(item);
    });
}

function renderAnnotationsList(annotations) {
    const annotationsList = document.getElementById('annotations-list');
    annotationsList.innerHTML = '';
    
    if (annotations.length === 0) {
        annotationsList.innerHTML = '<div class="panel-desc">No annotations yet</div>';
        return;
    }
    
    annotations.forEach(ann => {
        const item = document.createElement('div');
        item.className = 'list-item';
        item.innerHTML = `
            <div class="list-item-icon">
                <span class="material-icons-round">place</span>
            </div>
            <div class="list-item-info">
                <div class="list-item-title">${ann.text || 'Annotation'}</div>
                <div class="list-item-desc">${ann.type}</div>
            </div>
            <button class="icon-btn" onclick="deleteAnnotation('${ann.id}')">
                <span class="material-icons-round">delete</span>
            </button>
        `;
        annotationsList.appendChild(item);
    });
}

function renderCollectionsList(collections) {
    const collectionsList = document.getElementById('collections-list');
    collectionsList.innerHTML = '';
    
    if (collections.length === 0) {
        collectionsList.innerHTML = '<div class="panel-desc">No collections yet</div>';
        return;
    }
    
    collections.forEach(col => {
        const item = document.createElement('div');
        item.className = 'list-item';
        item.innerHTML = `
            <div class="list-item-icon">
                <span class="material-icons-round">collections</span>
            </div>
            <div class="list-item-info">
                <div class="list-item-title">${col.name}</div>
                <div class="list-item-desc">${col.image_ids.length} images</div>
            </div>
        `;
        collectionsList.appendChild(item);
    });
}

function renderSuggestionsList(suggestions) {
    const suggestionsList = document.getElementById('suggestions-list');
    suggestionsList.innerHTML = '';
    
    if (suggestions.length === 0) {
        suggestionsList.innerHTML = '<div class="panel-desc">No suggestions available</div>';
        return;
    }
    
    suggestions.forEach(sug => {
        const item = document.createElement('div');
        item.className = 'list-item';
        item.innerHTML = `
            <div class="list-item-icon">
                <span class="material-icons-round">auto_awesome</span>
            </div>
            <div class="list-item-info">
                <div class="list-item-title">${sug.reason}</div>
                <div class="list-item-desc">Confidence: ${Math.round(sug.confidence * 100)}%</div>
            </div>
        `;
        suggestionsList.appendChild(item);
    });
}

// ============================================================================
// UI Event Handlers
// ============================================================================

function initializeEventListeners() {
    // Bottom sheet drag/tap to expand/collapse
    const sheetHandle = document.getElementById('sheet-handle');
    const controlSheet = document.getElementById('control-sheet');
    
    sheetHandle.addEventListener('click', () => {
        controlSheet.classList.toggle('collapsed');
    });
    
    // Quick action buttons
    const actionButtons = document.querySelectorAll('.action-btn');
    actionButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const panelId = btn.id.replace('btn-', 'panel-');
            switchPanel(panelId);
            
            // Update active state
            actionButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        });
    });
    
    // Celestial body cards
    const bodyCards = document.querySelectorAll('.body-card');
    bodyCards.forEach(card => {
        card.addEventListener('click', async () => {
            const body = card.dataset.body;
            AppState.currentCelestialBody = body;
            
            // Update active state
            bodyCards.forEach(c => c.classList.remove('active'));
            card.classList.add('active');
            
            // Show/hide date section
            const dateSection = document.getElementById('date-section');
            dateSection.style.display = body === 'earth' ? 'block' : 'none';
            
            // Load layers for this body
            await loadAvailableLayers(body);
            
            // Switch to layers panel
            switchPanel('panel-layers');
            document.getElementById('btn-layers').classList.add('active');
            document.getElementById('btn-bodies').classList.remove('active');
        });
    });
    
    // Date picker
    document.getElementById('date-picker').value = AppState.currentDate;
    document.getElementById('date-picker').addEventListener('change', (e) => {
        AppState.currentDate = e.target.value;
        updateBaseLayer();
    });
    
    // Map controls
    document.getElementById('btn-zoom-in').addEventListener('click', () => map.zoomIn());
    document.getElementById('btn-zoom-out').addEventListener('click', () => map.zoomOut());
    document.getElementById('btn-locate').addEventListener('click', () => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition((position) => {
                map.setView([position.coords.latitude, position.coords.longitude], 8);
            });
        }
    });
    document.getElementById('btn-fullscreen').addEventListener('click', () => {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen();
        } else {
            document.exitFullscreen();
        }
    });
    
    // Add overlay layer button
    document.getElementById('btn-add-overlay').addEventListener('click', () => {
        // Show layer selector
        const layerValue = prompt('Enter layer ID to overlay:');
        if (layerValue) {
            addOverlayLayer(layerValue);
        }
    });
    
    // New collection button
    document.getElementById('btn-new-collection').addEventListener('click', () => {
        const name = prompt('Collection name:');
        if (name) {
            createCollection(name, '');
        }
    });
    
    // Suggestions button
    document.getElementById('btn-suggestions').addEventListener('click', () => {
        const popover = document.getElementById('suggestions-popover');
        popover.classList.toggle('hidden');
    });
    
    // Tool buttons
    document.getElementById('tool-marker').addEventListener('click', () => {
        if (AppState.currentImage) {
            const coords = prompt('Enter coordinates (lat,lng):');
            if (coords) {
                const [lat, lng] = coords.split(',').map(s => parseFloat(s.trim()));
                createAnnotation(AppState.currentImage.id, 'point', [{lat, lng}], 'Marker');
            }
        }
    });
}

function switchPanel(panelId) {
    // Hide all panels
    document.querySelectorAll('.content-panel').forEach(panel => {
        panel.classList.remove('active');
    });
    
    // Show selected panel
    const selectedPanel = document.getElementById(panelId);
    if (selectedPanel) {
        selectedPanel.classList.add('active');
    }
    
    // Expand sheet if collapsed
    const controlSheet = document.getElementById('control-sheet');
    controlSheet.classList.remove('collapsed');
}

// Make functions globally accessible
window.removeOverlayLayer = removeOverlayLayer;
window.deleteAnnotation = deleteAnnotation;

// ============================================================================
// Application Initialization
// ============================================================================

async function initializeApp() {
    console.log('🚀 Embiggen Your Eyes - iOS 26 Design');
    console.log('Initializing adaptive UI with backend integration...');
    
    // Initialize map
    const mapInitialized = initializeMap();
    if (!mapInitialized) {
        showStatus('Map initialization failed', 'error');
        return;
    }
    
    // Initialize event listeners
    initializeEventListeners();
    console.log('✓ Event listeners initialized');
    
    // Test backend connection
    try {
        const response = await fetch(`${BACKEND_URL}/`);
        const data = await response.json();
        console.log('✓ Backend connected:', data);
        showStatus('Connected', 'success');
    } catch (error) {
        console.error('❌ Backend not available:', error);
        showStatus('Backend offline', 'error');
        return;
    }
    
    // Load initial data
    await loadAvailableLayers(AppState.currentCelestialBody);
    await loadCollections();
    
    // Load initial image
    if (AppState.currentLayer) {
        await updateBaseLayer();
    }
    
    console.log('✅ App initialization complete!');
    console.log('🎨 Enjoy the iOS 26-inspired interface!');
}

// Start the app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}
