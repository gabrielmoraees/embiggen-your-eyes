// ============================================================================
// Embiggen Your Eyes - iOS 26 Design Frontend
// Comprehensive backend integration with adaptive UI
// ============================================================================

const BACKEND_URL = 'http://localhost:8000';

// ============================================================================
// Application State
// ============================================================================
const AppState = {
    // New backend structure
    currentCategory: 'planets',
    currentSubject: 'earth',
    currentDataset: null,
    currentVariant: null,
    currentDate: getDefaultDate(),
    currentView: null,
    
    // Map layers
    baseLayer: null,
    baseTileLayer: null,
    overlayLayers: [], // Array of {id, dataset, variant, tileLayer, opacity, zIndex}
    
    // Catalog data
    categories: [],
    datasets: [],  // Currently filtered datasets for explore panel
    allDatasets: [],  // Complete catalog of all datasets (never filtered)
    sources: [],
    
    // User data
    views: [],
    annotations: [],
    collections: [],
    
    // UI state
    compareMode: 'overlay',
    compareViews: [],
    
    // Drawing state
    drawingMode: null, // 'marker', 'path', 'rectangle', 'circle'
    drawingPath: [],
    drawingStart: null,
    tempDrawing: null
};

// ============================================================================
// Utility Functions
// ============================================================================
function getDefaultDate() {
    const date = new Date();
    date.setDate(date.getDate() - 2);  // Match backend: 2 days ago
    return date.toISOString().split('T')[0];
}

function showStatus(message, type = 'info') {
    const statusPill = document.getElementById('status-pill');
    const statusText = document.getElementById('status-text');
    const statusDot = statusPill.querySelector('.status-dot');
    
    // Update both desktop and mobile status
    statusText.textContent = message;
    const statusTextMobile = document.getElementById('status-text-mobile');
    if (statusTextMobile) {
        statusTextMobile.textContent = message;
    }
    
    // Update dot color based on type
    const colors = {
        info: '#5AC8FA',
        success: '#34C759',
        error: '#FF3B30',
        warning: '#FF9500'
    };
    
    statusDot.style.background = colors[type] || colors.info;
    
    // Update mobile status dot color
    const statusPillMobile = document.getElementById('status-pill-mobile');
    if (statusPillMobile) {
        const statusDotMobile = statusPillMobile.querySelector('.status-dot');
        if (statusDotMobile) {
            statusDotMobile.style.background = colors[type] || colors.info;
        }
    }
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
        
        // Map click handler for drawing
        map.on('click', handleMapClick);
        map.on('mousemove', handleMapMouseMove);
        
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

async function loadCategories() {
    try {
        const data = await apiRequest('/api/categories');
        AppState.categories = data.categories || [];
        console.log(`Loaded ${AppState.categories.length} categories`);
        return AppState.categories;
    } catch (error) {
        console.error('Failed to load categories:', error);
        return [];
    }
}

async function loadDatasets(category = null, subject = null, sourceId = null) {
    try {
        let endpoint = '/api/datasets?';
        const params = [];
        if (category) params.push(`category=${category}`);
        if (subject) params.push(`subject=${subject}`);
        if (sourceId) params.push(`source_id=${sourceId}`);
        
        endpoint += params.join('&');
        
        const data = await apiRequest(endpoint);
        AppState.datasets = data.datasets || [];
        console.log(`Loaded ${AppState.datasets.length} datasets`);
        return AppState.datasets;
    } catch (error) {
        console.error('Failed to load datasets:', error);
        return [];
    }
}

async function loadDataset(datasetId) {
    try {
        const dataset = await apiRequest(`/api/datasets/${datasetId}`);
        console.log(`Loaded dataset: ${dataset.name}`);
        return dataset;
    } catch (error) {
        console.error('Failed to load dataset:', error);
        return null;
    }
}

async function loadDatasetVariants(datasetId) {
    try {
        const data = await apiRequest(`/api/datasets/${datasetId}/variants`);
        console.log(`Loaded ${data.variants?.length || 0} variants for dataset ${datasetId}`);
        return data.variants || [];
    } catch (error) {
        console.error('Failed to load variants:', error);
        return [];
    }
}

async function loadVariantWithUrls(datasetId, variantId, date = null) {
    try {
        let endpoint = `/api/datasets/${datasetId}/variants/${variantId}`;
        if (date) {
            endpoint += `?date_param=${date}`;
        }
        const variant = await apiRequest(endpoint);
        console.log(`Loaded variant: ${variant.name}`);
        return variant;
    } catch (error) {
        console.error('Failed to load variant:', error);
        return null;
    }
}

async function loadSources(category = null, subject = null) {
    try {
        let endpoint = '/api/sources?';
        const params = [];
        if (category) params.push(`category=${category}`);
        if (subject) params.push(`subject=${subject}`);
        
        endpoint += params.join('&');
        
        const data = await apiRequest(endpoint);
        AppState.sources = data.sources || [];
        console.log(`Loaded ${AppState.sources.length} sources`);
        return AppState.sources;
    } catch (error) {
        console.error('Failed to load sources:', error);
        return [];
    }
}

async function loadAnnotations(viewId = null) {
    try {
        const endpoint = viewId 
            ? `/api/annotations?map_view_id=${viewId}`
            : '/api/annotations';
        const response = await apiRequest(endpoint);
        
        // Backend returns {annotations: [...]} not just [...]
        const annotations = response.annotations || response;
        
        // Ensure annotations is always an array
        if (!Array.isArray(annotations)) {
            console.warn('API returned non-array for annotations:', annotations);
            AppState.annotations = [];
            return [];
        }
        
        AppState.annotations = annotations;
        console.log(`✅ Loaded ${annotations.length} annotations from backend`);
        
        // Display all annotations on map
        annotations.forEach(ann => displayAnnotationOnMap(ann));
        
        renderAnnotationsList(annotations);
        return annotations;
    } catch (error) {
        console.error('Failed to load annotations:', error);
        // Ensure annotations remains an array even on error
        AppState.annotations = [];
        return [];
    }
}

async function createAnnotation(type, coordinates, text, color = '#007AFF', properties = {}) {
    try {
        const annotation = await apiRequest('/api/annotations', {
            method: 'POST',
            body: JSON.stringify({
                map_view_id: AppState.currentView?.id || null,
                type: type,
                coordinates: coordinates,
                text: text,
                color: color,
                properties: properties
            })
        });
        
        // Ensure annotations is an array before pushing
        if (!Array.isArray(AppState.annotations)) {
            console.warn('AppState.annotations is not an array, reinitializing...');
            AppState.annotations = [];
        }
        
        AppState.annotations.push(annotation);
        console.log(`✅ Annotation created and added to state. Total: ${AppState.annotations.length}`);
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
        
        // Find and remove from map
        const annotation = AppState.annotations.find(a => a.id === annotationId);
        if (annotation && annotation._leafletLayer) {
            map.removeLayer(annotation._leafletLayer);
        }
        
        AppState.annotations = AppState.annotations.filter(a => a.id !== annotationId);
        renderAnnotationsList(AppState.annotations);
        return true;
    } catch (error) {
        console.error('Failed to delete annotation:', error);
        return false;
    }
}

async function loadViews() {
    try {
        const views = await apiRequest('/api/views');
        AppState.views = views;
        console.log(`Loaded ${views.length} saved views`);
        return views;
    } catch (error) {
        console.error('Failed to load views:', error);
        return [];
    }
}

async function createView(name, description = null) {
    try {
        if (!AppState.currentDataset || !AppState.currentVariant) {
            console.warn('No dataset/variant selected');
            return null;
        }
        
        const center = map.getCenter();
        const view = await apiRequest('/api/views', {
            method: 'POST',
            body: JSON.stringify({
                name: name,
                description: description,
                dataset_id: AppState.currentDataset.id,
                variant_id: AppState.currentVariant.id,
                selected_date: AppState.currentDate || null,
                center_lat: center.lat,
                center_lng: center.lng,
                zoom_level: map.getZoom(),
                active_layers: AppState.overlayLayers.map(l => l.id),
                annotation_ids: AppState.annotations.map(a => a.id)
            })
        });
        
        AppState.views.push(view);
        AppState.currentView = view;
        console.log(`Created view: ${view.name}`);
        return view;
    } catch (error) {
        console.error('Failed to create view:', error);
        return null;
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

async function createCollection(name, description, viewIds = []) {
    try {
        const collection = await apiRequest('/api/collections', {
            method: 'POST',
            body: JSON.stringify({
                name: name,
                description: description,
                view_ids: viewIds
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

// ============================================================================
// Layer Management
// ============================================================================

function createTileLayer(tileUrl, maxZoom = 18, attribution = '© NASA') {
    const tileLayer = L.tileLayer(tileUrl, {
        attribution: attribution,
        tileSize: 256,
        noWrap: AppState.currentSubject === 'earth',
        minZoom: 0,
        maxZoom: maxZoom,
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
    if (!AppState.currentDataset || !AppState.currentVariant) {
        console.warn('No dataset or variant selected');
        return;
    }
    
    try {
        // Load the variant with resolved tile URLs
        const response = await loadVariantWithUrls(
            AppState.currentDataset.id,
            AppState.currentVariant.id,
            AppState.currentDate
        );
        
        // Backend returns {dataset_id, variant: {...}}
        const variant = response?.variant;
        
        if (!variant || !variant.tile_url) {
            showStatus('No tile URL found', 'warning');
            console.error('Variant response:', response);
            return;
        }
        
        // Remove old base layer
        if (gibsLayer) {
    map.removeLayer(gibsLayer);
        }
        
        // Get attribution from source
        const source = AppState.sources.find(s => s.id === AppState.currentDataset.source_id);
        const attribution = source ? source.attribution : '© NASA';
        
        // Create new base layer with z-index 0
        gibsLayer = createTileLayer(variant.tile_url, variant.max_zoom || 18, attribution);
        gibsLayer.setZIndex(0);
    gibsLayer.addTo(map);
    
        // Store reference
        AppState.baseTileLayer = gibsLayer;
        
        // Update UI
        const baseLayerName = document.getElementById('base-layer-name');
        if (baseLayerName) {
            baseLayerName.textContent = `${AppState.currentDataset.name} - ${variant.name}`;
        }
        
        // Update map attribution
        map.attributionControl.setPrefix('');
        
        // Re-apply overlay layer z-indices to ensure correct stacking
        updateLayerStacking();
        
        showStatus('Map loaded', 'success');
        console.log(`Loaded: ${AppState.currentDataset.name} - ${variant.name}`);
    } catch (error) {
        console.error('Failed to update base layer:', error);
        showStatus('Failed to load map', 'error');
    }
}

// ============================================================================
// Drawing & Annotation Functions
// ============================================================================

function handleMapClick(e) {
    if (!AppState.drawingMode) return;
    
    const latlng = e.latlng;
    
    switch (AppState.drawingMode) {
        case 'marker':
            createMarkerAnnotation(latlng);
            exitDrawingMode();
            break;
            
        case 'path':
            addPathPoint(latlng);
            break;
            
        case 'rectangle':
            if (!AppState.drawingStart) {
                startRectangle(latlng);
            } else {
                finishRectangle(latlng);
            }
            break;
            
        case 'circle':
            if (!AppState.drawingStart) {
                startCircle(latlng);
            } else {
                finishCircle(latlng);
            }
            break;
    }
}

function handleMapMouseMove(e) {
    if (!AppState.drawingMode || !AppState.drawingStart) return;
    
    const latlng = e.latlng;
    
    switch (AppState.drawingMode) {
        case 'rectangle':
            updateRectanglePreview(latlng);
            break;
            
        case 'circle':
            updateCirclePreview(latlng);
            break;
    }
}

// Marker annotation
async function createMarkerAnnotation(latlng) {
    // Use default name, user can edit later
    const name = `Marker ${AppState.annotations.length + 1}`;
    
    console.log('📍 Creating marker at:', latlng);
    const annotation = await createAnnotation(
        'point',
        [{lat: latlng.lat, lng: latlng.lng}],
        name,
        '#007AFF'
    );
    
    console.log('📍 Annotation created:', annotation);
    if (annotation) {
        console.log('📍 Displaying annotation on map...');
        displayAnnotationOnMap(annotation, true); // Auto-open popup for new marker
        console.log('📍 Annotation displayed!');
        showStatus('Marker added', 'success');
    } else {
        console.error('❌ Failed to create annotation');
        showStatus('Failed to add marker', 'error');
    }
}

// Path builder (replaces polygon)
function addPathPoint(latlng) {
    AppState.drawingPath.push(latlng);
    
    // Visual feedback - show path so far
    if (AppState.tempDrawing) {
        map.removeLayer(AppState.tempDrawing);
    }
    
    if (AppState.drawingPath.length > 1) {
        AppState.tempDrawing = L.polyline(
            AppState.drawingPath.map(p => [p.lat, p.lng]),
            {
                color: '#007AFF',
                weight: 3,
                opacity: 0.7,
                dashArray: '5, 10'
            }
        ).addTo(map);
    }
    
    // Add temporary marker for this point
    L.circleMarker([latlng.lat, latlng.lng], {
        radius: 5,
        fillColor: '#007AFF',
        fillOpacity: 1,
        color: 'white',
        weight: 2
    }).addTo(map);
    
    // Show instruction
    showStatus(`Path: ${AppState.drawingPath.length} points (double-click to finish)`, 'info');
}

async function finishPath() {
    if (AppState.drawingPath.length < 2) {
        showStatus('Path needs at least 2 points', 'warning');
        exitDrawingMode();
        return;
    }
    
    // Use default name, user can edit later
    const name = `Path ${AppState.annotations.length + 1}`;
    
    const coordinates = AppState.drawingPath.map(p => ({lat: p.lat, lng: p.lng}));
    
    const annotation = await createAnnotation(
        'polygon',
        coordinates,
        name,
        '#007AFF'
    );
    
    if (annotation) {
        displayAnnotationOnMap(annotation, true); // Auto-open popup for new path
        showStatus('Path created', 'success');
    }
    
    exitDrawingMode();
}

// Rectangle
function startRectangle(latlng) {
    AppState.drawingStart = latlng;
    showStatus('Click to set opposite corner', 'info');
}

function updateRectanglePreview(latlng) {
    if (AppState.tempDrawing) {
        map.removeLayer(AppState.tempDrawing);
    }
    
    const bounds = [
        [AppState.drawingStart.lat, AppState.drawingStart.lng],
        [latlng.lat, latlng.lng]
    ];
    
    AppState.tempDrawing = L.rectangle(bounds, {
        color: '#007AFF',
        weight: 2,
        opacity: 0.7,
        fillOpacity: 0.2,
        dashArray: '5, 10'
    }).addTo(map);
}

async function finishRectangle(latlng) {
    // Use default name, user can edit later
    const name = `Rectangle ${AppState.annotations.length + 1}`;
    
    const coordinates = [
        {lat: AppState.drawingStart.lat, lng: AppState.drawingStart.lng},
        {lat: latlng.lat, lng: latlng.lng}
    ];
    
    const annotation = await createAnnotation(
        'rectangle',
        coordinates,
        name,
        '#007AFF'
    );
    
    if (annotation) {
        displayAnnotationOnMap(annotation, true); // Auto-open popup for new rectangle
        showStatus('Rectangle created', 'success');
    }
    
    exitDrawingMode();
}

// Circle
function startCircle(latlng) {
    AppState.drawingStart = latlng;
    showStatus('Click to set radius', 'info');
}

function updateCirclePreview(latlng) {
    if (AppState.tempDrawing) {
        map.removeLayer(AppState.tempDrawing);
    }
    
    const radius = AppState.drawingStart.distanceTo(latlng);
    
    AppState.tempDrawing = L.circle(
        [AppState.drawingStart.lat, AppState.drawingStart.lng],
        {
            radius: radius,
            color: '#007AFF',
            weight: 2,
            opacity: 0.7,
            fillOpacity: 0.2,
            dashArray: '5, 10'
        }
    ).addTo(map);
}

async function finishCircle(latlng) {
    const radius = AppState.drawingStart.distanceTo(latlng);
    // Use default name, user can edit later
    const name = `Circle ${AppState.annotations.length + 1}`;
    
    const coordinates = [
        {lat: AppState.drawingStart.lat, lng: AppState.drawingStart.lng}
    ];
    
    const annotation = await createAnnotation(
        'circle',
        coordinates,
        name,
        '#007AFF',
        {radius: radius}
    );
    
    if (annotation) {
        displayAnnotationOnMap(annotation, true); // Auto-open popup for new circle
        showStatus('Circle created', 'success');
    }
    
    exitDrawingMode();
}

function displayAnnotationOnMap(annotation, autoOpenPopup = false) {
    console.log('🗺️ displayAnnotationOnMap called for:', annotation.type, annotation.text);
    let layer;
    
    if (annotation.type === 'point') {
        console.log('🗺️ Creating circleMarker at:', annotation.coordinates[0]);
        layer = L.circleMarker(
            [annotation.coordinates[0].lat, annotation.coordinates[0].lng],
            {
                radius: 8,
                fillColor: annotation.color,
                fillOpacity: 0.8,
                color: 'white',
                weight: 2
            }
        );
        console.log('🗺️ CircleMarker created:', layer);
    } else if (annotation.type === 'polygon') {
        const coords = annotation.coordinates.map(c => [c.lat, c.lng]);
        layer = L.polyline(coords, {
            color: annotation.color,
            weight: 3,
            opacity: 0.8
        });
    } else if (annotation.type === 'rectangle') {
        const bounds = [
            [annotation.coordinates[0].lat, annotation.coordinates[0].lng],
            [annotation.coordinates[1].lat, annotation.coordinates[1].lng]
        ];
        layer = L.rectangle(bounds, {
            color: annotation.color,
            weight: 2,
            opacity: 0.8,
            fillOpacity: 0.2
        });
    } else if (annotation.type === 'circle') {
        layer = L.circle(
            [annotation.coordinates[0].lat, annotation.coordinates[0].lng],
            {
                radius: annotation.properties.radius || 10000,
                color: annotation.color,
                weight: 2,
                opacity: 0.8,
                fillOpacity: 0.2
            }
        );
    }
    
    if (layer) {
        console.log('🗺️ Layer created, adding to map...');
        // Create popup with editable content
        const popupContent = createEditablePopup(annotation);
        layer.bindPopup(popupContent);
        
        // Add event listener for when popup opens
        layer.on('popupopen', () => {
            setupPopupEditing(annotation);
        });
        
        console.log('🗺️ Adding layer to map. Map object:', map);
        layer.addTo(map);
        console.log('🗺️ Layer added to map successfully!');
        
        // Store reference for cleanup
        if (!annotation._leafletLayer) {
            annotation._leafletLayer = layer;
        }
        
        // Auto-open popup for newly created annotations
        if (autoOpenPopup) {
            console.log('🗺️ Auto-opening popup in 100ms...');
                setTimeout(() => {
                layer.openPopup();
                console.log('🗺️ Popup opened!');
            }, 100);
        }
    } else {
        console.error('❌ Layer is null/undefined! annotation.type:', annotation.type);
    }
}

function createEditablePopup(annotation) {
    return `
        <div style="font-family: -apple-system, sans-serif; min-width: 150px;">
            <div class="popup-title-editable" 
                 data-annotation-id="${annotation.id}" 
                 contenteditable="false" 
                 spellcheck="false"
                 style="font-weight: 600; 
                        font-size: 15px; 
                        padding: 4px 6px; 
                        border-radius: 4px; 
                        cursor: text; 
                        transition: all 0.2s;
                        outline: none;
                        margin-bottom: 8px;"
                 onmouseover="this.style.background='rgba(0,0,0,0.05)'"
                 onmouseout="if(!this.isContentEditable) this.style.background='transparent'"
            >${annotation.text || 'Annotation'}</div>
            <small style="color: #666;">Type: ${annotation.type}</small>
        </div>
    `;
}

function setupPopupEditing(annotation) {
    const titleEl = document.querySelector(`.popup-title-editable[data-annotation-id="${annotation.id}"]`);
    if (!titleEl) return;
    
    // Click to edit
    titleEl.addEventListener('click', (e) => {
        e.stopPropagation();
        enablePopupEdit(titleEl, annotation);
    });
    
    // Save on blur
    titleEl.addEventListener('blur', () => {
        savePopupEdit(titleEl, annotation);
    });
    
    // Keyboard shortcuts
    titleEl.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            titleEl.blur();
        } else if (e.key === 'Escape') {
            e.preventDefault();
            cancelPopupEdit(titleEl, annotation);
        }
    });
}

function enablePopupEdit(element, annotation) {
    // Store original value
    element.dataset.originalValue = element.textContent;
    
    // Enable editing
    element.contentEditable = true;
    element.style.background = 'rgba(12, 140, 233, 0.15)';
    element.style.border = '1px solid #0C8CE9';
    element.style.boxShadow = '0 0 0 3px rgba(12, 140, 233, 0.2)';
    
    // Focus and select
    element.focus();
    const range = document.createRange();
    range.selectNodeContents(element);
    const selection = window.getSelection();
    selection.removeAllRanges();
    selection.addRange(range);
}

function savePopupEdit(element, annotation) {
    if (!element.isContentEditable) return;
    
    const newName = element.textContent.trim();
    const originalName = element.dataset.originalValue;
    
    // Reset styles
    element.contentEditable = false;
    element.style.background = 'transparent';
    element.style.border = 'none';
    element.style.boxShadow = 'none';
    
    // Update if changed
    if (newName && newName !== originalName) {
        updateAnnotationName(annotation.id, newName);
    } else {
        element.textContent = originalName;
    }
    
    delete element.dataset.originalValue;
}

function cancelPopupEdit(element, annotation) {
    if (!element.isContentEditable) return;
    
    // Restore original
    element.textContent = element.dataset.originalValue;
    
    // Reset styles
    element.contentEditable = false;
    element.style.background = 'transparent';
    element.style.border = 'none';
    element.style.boxShadow = 'none';
    
    delete element.dataset.originalValue;
    element.blur();
}

function enterDrawingMode(mode) {
    // Exit any previous mode
    exitDrawingMode();
    
    AppState.drawingMode = mode;
    map.getContainer().style.cursor = 'crosshair';
    
    const messages = {
        marker: 'Click on map to place marker',
        path: 'Click points to build path (double-click to finish)',
        rectangle: 'Click to set first corner',
        circle: 'Click to set center'
    };
    
    showStatus(messages[mode] || 'Drawing mode active', 'info');
    
    // Update tool button states
    updateToolButtonStates();
    
    // Close the bottom sheet to focus on map
    closeBottomSheet();
}

function exitDrawingMode() {
    // Clean up temp drawing
    if (AppState.tempDrawing) {
        map.removeLayer(AppState.tempDrawing);
        AppState.tempDrawing = null;
    }
    
    AppState.drawingMode = null;
    AppState.drawingPath = [];
    AppState.drawingStart = null;
    map.getContainer().style.cursor = '';
    
    // Update tool button states
    updateToolButtonStates();
}

function updateToolButtonStates() {
    const toolButtons = document.querySelectorAll('.tool-btn');
    toolButtons.forEach(btn => {
        btn.classList.remove('active');
    });
    
    if (AppState.drawingMode) {
        const activeBtn = document.getElementById(`tool-${AppState.drawingMode}`);
        if (activeBtn) {
            activeBtn.classList.add('active');
        }
    }
}

// ============================================================================
// Overlay Layer Management
// ============================================================================

async function addOverlayLayer(datasetId, variantId = null, date = null) {
    try {
        showStatus('Loading overlay...', 'info');
        
        // Load the dataset
        const dataset = await loadDataset(datasetId);
        if (!dataset) {
            showStatus('Failed to load dataset', 'error');
            return;
        }
        
        // Load variants
        const variants = await loadDatasetVariants(datasetId);
        if (variants.length === 0) {
            showStatus('No variants available', 'error');
            return;
        }
        
        // Select variant (use provided, default, or first)
        const selectedVariant = variantId 
            ? variants.find(v => v.id === variantId) 
            : (variants.find(v => v.is_default) || variants[0]);
        
        // Load variant with tile URLs
        const useDate = date || (dataset.supports_time_series ? AppState.currentDate : null);
        const response = await loadVariantWithUrls(datasetId, selectedVariant.id, useDate);
        const variant = response?.variant;
        
        if (!variant || !variant.tile_url) {
            showStatus('No tile URL found', 'error');
            return;
        }
        
        // Get attribution
        const source = AppState.sources.find(s => s.id === dataset.source_id);
        const attribution = source ? source.attribution : '© NASA';
        
        // Create tile layer
        const tileLayer = createTileLayer(variant.tile_url, variant.max_zoom || 18, attribution);
        tileLayer.setOpacity(0.7); // Default opacity for overlays
        
        // Generate unique ID for this layer
        const layerId = `overlay-${Date.now()}`;
        
        // Calculate z-index (base layer is 0, overlays start at 1)
        const zIndex = AppState.overlayLayers.length + 1;
        tileLayer.setZIndex(zIndex);
        tileLayer.addTo(map);
        
        // Add to overlay layers array
        AppState.overlayLayers.push({
            id: layerId,
            dataset: dataset,
            variant: variant,
            tileLayer: tileLayer,
            opacity: 0.7,
            zIndex: zIndex,
            date: useDate
        });
        
        // Update UI
        renderOverlayLayers();
        showStatus('Overlay added', 'success');
        console.log(`Added overlay: ${dataset.name} - ${variant.name}`);
        
    } catch (error) {
        console.error('Failed to add overlay layer:', error);
        showStatus('Failed to add overlay', 'error');
    }
}

function removeOverlayLayer(layerId) {
    const index = AppState.overlayLayers.findIndex(l => l.id === layerId);
    if (index === -1) return;
    
    const overlay = AppState.overlayLayers[index];
    
    // Remove from map
    if (overlay.tileLayer) {
        map.removeLayer(overlay.tileLayer);
    }
    
    // Remove from array
    AppState.overlayLayers.splice(index, 1);
    
    // Update z-indices for remaining layers
    updateLayerStacking();
    
    // Update UI
    renderOverlayLayers();
    showStatus('Overlay removed', 'success');
}

function updateLayerOpacity(layerId, opacity) {
    const overlay = AppState.overlayLayers.find(l => l.id === layerId);
    if (!overlay) return;
    
    overlay.opacity = opacity;
    overlay.tileLayer.setOpacity(opacity);
}

function updateLayerStacking() {
    // Ensure base layer stays at z-index 0
    if (AppState.baseTileLayer) {
        AppState.baseTileLayer.setZIndex(0);
    }
    
    // Update z-indices for overlay layers based on their order in the array
    AppState.overlayLayers.forEach((overlay, index) => {
        const zIndex = index + 1;
        overlay.zIndex = zIndex;
        if (overlay.tileLayer) {
            overlay.tileLayer.setZIndex(zIndex);
        }
    });
}

function reorderOverlayLayers(fromIndex, toIndex) {
    if (fromIndex === toIndex) return;
    if (fromIndex < 0 || fromIndex >= AppState.overlayLayers.length) return;
    if (toIndex < 0 || toIndex >= AppState.overlayLayers.length) return;
    
    // Remove item from old position
    const [movedItem] = AppState.overlayLayers.splice(fromIndex, 1);
    
    // Insert at new position
    AppState.overlayLayers.splice(toIndex, 0, movedItem);
    
    // Update z-indices
    updateLayerStacking();
    
    // Update UI
    renderOverlayLayers();
    showStatus('Layer order updated', 'success');
}

// ============================================================================
// UI Rendering Functions
// ============================================================================

// Subject icon mapping - Using SVG icons from Flaticon-style assets
const SUBJECT_ICONS = {
    // Planets - SVG icons
    earth: 'assets/icons/earth.svg',
    mars: 'assets/icons/mars.svg',
    mercury: 'assets/icons/mercury.svg',
    venus: 'assets/icons/earth.svg',    // Reuse Earth, replace with venus.svg later
    jupiter: 'assets/icons/saturn.svg',  // Reuse Saturn, replace with jupiter.svg later
    saturn: 'assets/icons/saturn.svg',
    uranus: 'assets/icons/earth.svg',    // Reuse Earth, replace with uranus.svg later
    neptune: 'assets/icons/earth.svg',   // Reuse Earth, replace with neptune.svg later
    
    // Moons
    moon: 'assets/icons/moon.svg',
    europa: 'assets/icons/moon.svg',     // Reuse Moon, replace with europa.svg later
    titan: 'assets/icons/moon.svg',      // Reuse Moon, replace with titan.svg later
    enceladus: 'assets/icons/moon.svg',  // Reuse Moon, replace with enceladus.svg later
    
    // Deep space
    milky_way: 'assets/icons/galaxy.svg',
    andromeda: 'assets/icons/galaxy.svg',
    
    // Custom
    custom: 'assets/icons/custom.svg'
};

// Category icon mapping - Using SVG icons
const CATEGORY_ICONS = {
    planets: 'assets/icons/earth.svg',
    moons: 'assets/icons/moon.svg',
    satellites: 'assets/icons/moon.svg',  // Use moon icon for satellites
    dwarf_planets: 'assets/icons/mercury.svg',
    galaxies: 'assets/icons/galaxy.svg',
    nebulae: 'assets/icons/galaxy.svg',    // Reuse galaxy, replace with nebula.svg later
    star_clusters: 'assets/icons/galaxy.svg', // Reuse galaxy, replace with cluster.svg later
    phenomena: 'assets/icons/galaxy.svg',  // Reuse galaxy, replace with phenomena.svg later
    regions: 'assets/icons/custom.svg',
    custom: 'assets/icons/custom.svg'
};

function renderCategoriesWithSubjects() {
    const categoriesList = document.getElementById('categories-list');
    if (!categoriesList) {
        console.error('categories-list element not found');
        return;
    }
    
    categoriesList.innerHTML = '';
    
    if (!AppState.categories || AppState.categories.length === 0) {
        categoriesList.innerHTML = '<div class="panel-desc">Loading categories...</div>';
        console.log('No categories available yet');
        return;
    }
    
    console.log(`Rendering ${AppState.categories.length} categories`);
    
    AppState.categories.forEach(category => {
        const group = document.createElement('div');
        group.className = 'category-group';
        
        const subjectsHTML = category.subjects.map(subject => {
            const iconPath = SUBJECT_ICONS[subject] || SUBJECT_ICONS.custom;
            // Get dataset count for this subject
            const datasetCount = AppState.datasets ? AppState.datasets.filter(d => 
                d.subject === subject && d.category === category.id
            ).length : 0;
            
            const isActive = AppState.currentSubject === subject ? 'active' : '';
            
            return `
                <div class="subject-card ${isActive}" data-category="${category.id}" data-subject="${subject}">
                    <img src="${iconPath}" alt="${subject}" class="subject-icon" />
                    <div class="subject-name">${subject.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</div>
                    ${datasetCount > 0 ? `<div class="subject-count">${datasetCount} dataset${datasetCount > 1 ? 's' : ''}</div>` : ''}
                </div>
            `;
        }).join('');
        
        const categoryIconPath = CATEGORY_ICONS[category.id] || CATEGORY_ICONS.custom;
        
        group.innerHTML = `
            <div class="category-header">
                <img src="${categoryIconPath}" alt="${category.id}" class="category-icon" />
                <div class="category-info">
                    <div class="category-name">${category.name}</div>
                    <div class="category-meta">${category.dataset_count} datasets • ${category.subjects.length} subjects</div>
                </div>
            </div>
            <div class="subjects-grid">
                ${subjectsHTML}
            </div>
        `;
        
        categoriesList.appendChild(group);
    });
    
    console.log('Categories rendered, adding event listeners');
    
    // Add event listeners to subject cards
    document.querySelectorAll('.subject-card').forEach(card => {
        card.addEventListener('click', async () => {
            const category = card.dataset.category;
            const subject = card.dataset.subject;
            
            console.log(`Subject clicked: ${category} > ${subject}`);
            
            // Check if this subject is already selected
            if (AppState.currentCategory === category && AppState.currentSubject === subject) {
                console.log('Subject already selected, skipping reload');
                
                // Just close the bottom sheet
                closeBottomSheet();
                return;
            }
            
            AppState.currentCategory = category;
            AppState.currentSubject = subject;
            
            // Close bottom sheet to focus on map
            closeBottomSheet();
            
            // Load datasets for this subject
            const datasets = await loadDatasets(category, subject);
            
            // Auto-select first dataset if available
            if (datasets.length > 0) {
                AppState.currentDataset = datasets[0];
                
                // Load variants for the first dataset
                const variants = await loadDatasetVariants(datasets[0].id);
                if (variants.length > 0) {
                    AppState.currentVariant = variants.find(v => v.is_default) || variants[0];
                    
                    // Show variant selector
                    renderVariantSelector(variants);
                    
                    // Update date picker visibility
                    updateDatePickerVisibility(datasets[0]);
                    
                    // Update map with selected dataset
                    await updateBaseLayer();
                }
            }
            
            // Render datasets list AFTER setting current dataset (so active state shows)
            renderDatasetsList(datasets);
            
            // Update breadcrumb
            updateBreadcrumb();
            
            // Dataset is now in dropdown, no need to switch panels
        });
    });
}

function updateBreadcrumb() {
    const breadcrumb = document.getElementById('dataset-breadcrumb');
    const breadcrumbDropdown = document.getElementById('dataset-breadcrumb-dropdown');
    
    const parts = [];
    if (AppState.currentCategory) {
        parts.push(AppState.currentCategory.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()));
    }
    if (AppState.currentSubject) {
        parts.push(AppState.currentSubject.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()));
    }
    if (AppState.currentDataset) {
        parts.push(AppState.currentDataset.name);
    }
    
    const breadcrumbText = parts.join(' › ');
    if (breadcrumb) breadcrumb.textContent = breadcrumbText;
    if (breadcrumbDropdown) breadcrumbDropdown.textContent = breadcrumbText;
    
    // Update dataset button label
    updateDatasetButtonLabel();
}

function updateDatasetButtonLabel() {
    const btnLabel = document.getElementById('dataset-btn-label');
    if (!btnLabel) return;
    
    // Always show "Dataset" label
    btnLabel.textContent = 'Dataset';
}

function renderDatasetsList(datasets) {
    const layersList = document.getElementById('layers-list');
    const layersListDropdown = document.getElementById('layers-list-dropdown');
    
    console.log(`Rendering ${datasets.length} datasets`);
    
    if (datasets.length === 0) {
        const emptyMsg = '<div class="panel-desc">No datasets available for this selection</div>';
        if (layersList) layersList.innerHTML = emptyMsg;
        if (layersListDropdown) layersListDropdown.innerHTML = emptyMsg;
        return;
    }
    
    if (layersList) {
        layersList.innerHTML = '';
        renderDatasetsInContainer(datasets, layersList);
    }
    
    if (layersListDropdown) {
        layersListDropdown.innerHTML = '';
        renderDatasetsInContainer(datasets, layersListDropdown);
    }
}

function renderDatasetsInContainer(datasets, container) {
    
    datasets.forEach(dataset => {
        const card = document.createElement('div');
        card.className = 'layer-card';
        const isActive = AppState.currentDataset && dataset.id === AppState.currentDataset.id;
        if (isActive) {
            card.classList.add('active');
            console.log(`✓ Dataset "${dataset.name}" marked as active`);
        }
        
        // Build badges
        const badges = [];
        if (dataset.supports_time_series) {
            badges.push(`<span class="layer-badge"><span class="material-icons-round">schedule</span>Time-series</span>`);
        }
        if (dataset.variants && dataset.variants.length > 1) {
            badges.push(`<span class="layer-badge">${dataset.variants.length} variants</span>`);
        }
        
        card.innerHTML = `
            <div class="layer-icon">
                <span class="material-icons-round">terrain</span>
            </div>
            <div class="layer-info">
                <div class="layer-name">
                    ${dataset.name}
                    ${badges.join('')}
                </div>
                <div class="layer-desc">${dataset.description}</div>
            </div>
        `;
        
        card.addEventListener('click', async () => {
            AppState.currentDataset = dataset;
            
            // Load variants for this dataset
            const variants = await loadDatasetVariants(dataset.id);
            if (variants.length > 0) {
                // Find default variant or use first one
                const defaultVariant = variants.find(v => v.is_default) || variants[0];
                AppState.currentVariant = defaultVariant;
                
                // Show variant selector if multiple variants
                renderVariantSelector(variants);
                
                // Show/hide date picker based on time-series support
                updateDatePickerVisibility(dataset);
                
                // Update map
                await updateBaseLayer();
            }
            
            // Update breadcrumb
            updateBreadcrumb();
            
            renderDatasetsList(datasets);
        });
        
        container.appendChild(card);
    });
}

function renderVariantSelector(variants) {
    const variantSection = document.getElementById('variant-section');
    const variantSelector = document.getElementById('variant-selector');
    const variantSectionDropdown = document.getElementById('variant-section-dropdown');
    const variantSelectorDropdown = document.getElementById('variant-selector-dropdown');
    
    if (!variants || variants.length === 0) {
        if (variantSection) variantSection.classList.add('hidden');
        if (variantSectionDropdown) variantSectionDropdown.classList.add('hidden');
        return;
    }
    
    console.log(`Rendering ${variants.length} variant(s), current: ${AppState.currentVariant?.id}`);
    
    // Render in panel
    if (variantSection && variantSelector) {
        variantSection.classList.remove('hidden');
        variantSelector.innerHTML = '';
        renderVariantsInContainer(variants, variantSelector);
    }
    
    // Render in dropdown
    if (variantSectionDropdown && variantSelectorDropdown) {
        variantSectionDropdown.classList.remove('hidden');
        variantSelectorDropdown.innerHTML = '';
        renderVariantsInContainer(variants, variantSelectorDropdown);
    }
}

function renderVariantsInContainer(variants, container) {
    variants.forEach(variant => {
        const card = document.createElement('div');
        card.className = 'variant-card';
        if (AppState.currentVariant && variant.id === AppState.currentVariant.id) {
            card.classList.add('active');
        }
        
        card.innerHTML = `
            <div class="variant-name">${variant.name}</div>
            <div class="variant-desc">${variant.description}</div>
        `;
        
        card.addEventListener('click', async () => {
            AppState.currentVariant = variant;
            await updateBaseLayer();
            renderVariantSelector([...variants]); // Re-render both
        });
        
        container.appendChild(card);
    });
}

function updateDatePickerVisibility(dataset) {
    const dateSection = document.getElementById('date-section');
    const datePicker = document.getElementById('date-picker');
    const dateRangeInfo = document.getElementById('date-range-info');
    const dateSectionDropdown = document.getElementById('date-section-dropdown');
    const datePickerDropdown = document.getElementById('date-picker-dropdown');
    const dateRangeInfoDropdown = document.getElementById('date-range-info-dropdown');
    
    if (!dataset.supports_time_series) {
        if (dateSection) dateSection.classList.add('hidden');
        if (dateSectionDropdown) dateSectionDropdown.classList.add('hidden');
        return;
    }
    
    if (dateSection) dateSection.classList.remove('hidden');
    if (dateSectionDropdown) dateSectionDropdown.classList.remove('hidden');
    
    // Set date range
    if (dataset.date_range_start && dataset.date_range_end) {
        const start = new Date(dataset.date_range_start).toLocaleDateString('en-US', { year: 'numeric', month: 'short' });
        const end = new Date(dataset.date_range_end).toLocaleDateString('en-US', { year: 'numeric', month: 'short' });
        const rangeText = `(${start} - ${end})`;
        
        if (dateRangeInfo) dateRangeInfo.textContent = rangeText;
        if (dateRangeInfoDropdown) dateRangeInfoDropdown.textContent = rangeText;
        
        // Set min/max on both date pickers
        if (datePicker) {
            datePicker.min = dataset.date_range_start;
            datePicker.max = dataset.date_range_end;
        }
        if (datePickerDropdown) {
            datePickerDropdown.min = dataset.date_range_start;
            datePickerDropdown.max = dataset.date_range_end;
        }
    } else {
        if (dateRangeInfo) dateRangeInfo.textContent = '';
        if (dateRangeInfoDropdown) dateRangeInfoDropdown.textContent = '';
    }
    
    // Set default value
    if (dataset.default_date) {
        const dateValue = dataset.default_date;
        if (datePicker) datePicker.value = dateValue;
        if (datePickerDropdown) datePickerDropdown.value = dateValue;
        AppState.currentDate = dateValue;
    }
}

function renderOverlayLayers() {
    const overlayLayersEl = document.getElementById('overlay-layers');
    
    // Keep base layer, clear overlay layers
    const baseLayerEl = overlayLayersEl.querySelector('.base-layer');
    overlayLayersEl.innerHTML = '';
    if (baseLayerEl) {
        overlayLayersEl.appendChild(baseLayerEl);
    }
    
    // Render overlay layers (in order from bottom to top)
    AppState.overlayLayers.forEach((overlay, index) => {
        const item = document.createElement('div');
        item.className = 'overlay-item';
        item.dataset.layerId = overlay.id;
        item.dataset.index = index;
        item.draggable = true;
        
        const opacityPercent = Math.round(overlay.opacity * 100);
        
        item.innerHTML = `
            <span class="material-icons-round drag-handle">drag_indicator</span>
            <span class="material-icons-round">layers</span>
            <div class="overlay-info">
                <div class="overlay-name">Layer ${index + 1}</div>
                <div class="overlay-desc">${overlay.dataset.name} - ${overlay.variant.name}</div>
            </div>
            <div class="overlay-controls">
                <div class="opacity-control">
                    <input type="range" min="0" max="100" value="${opacityPercent}" 
                           class="opacity-slider" data-layer-id="${overlay.id}">
                    <span class="opacity-value">${opacityPercent}%</span>
                </div>
                <button class="icon-btn" data-layer-id="${overlay.id}" title="Remove">
                    <span class="material-icons-round">close</span>
                </button>
        </div>
    `;
        
        // Add drag event listeners
        const dragHandle = item.querySelector('.drag-handle');
        dragHandle.addEventListener('mousedown', (e) => {
            item.draggable = true;
        });
        
        item.addEventListener('dragstart', handleDragStart);
        item.addEventListener('dragover', handleDragOver);
        item.addEventListener('drop', handleDrop);
        item.addEventListener('dragend', handleDragEnd);
        
        // Add opacity slider listener
        const opacitySlider = item.querySelector('.opacity-slider');
        opacitySlider.addEventListener('input', (e) => {
            const opacity = parseFloat(e.target.value) / 100;
            updateLayerOpacity(overlay.id, opacity);
            
            // Update displayed value
            const valueSpan = item.querySelector('.opacity-value');
            valueSpan.textContent = `${e.target.value}%`;
        });
        
        // Add remove button listener
        const removeBtn = item.querySelector('.icon-btn[data-layer-id]');
        removeBtn.addEventListener('click', () => {
            removeOverlayLayer(overlay.id);
        });
        
        overlayLayersEl.appendChild(item);
    });
}

// Drag and drop handlers
let draggedItem = null;

function handleDragStart(e) {
    draggedItem = e.currentTarget;
    draggedItem.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
}

function handleDragOver(e) {
    if (e.preventDefault) {
        e.preventDefault();
    }
    e.dataTransfer.dropEffect = 'move';
    
    const target = e.currentTarget;
    if (target !== draggedItem && target.classList.contains('overlay-item') && !target.classList.contains('base-layer')) {
        target.classList.add('drag-over');
    }
    
    return false;
}

function handleDrop(e) {
    if (e.stopPropagation) {
        e.stopPropagation();
    }
    
    const target = e.currentTarget;
    target.classList.remove('drag-over');
    
    if (draggedItem !== target && !target.classList.contains('base-layer')) {
        const fromIndex = parseInt(draggedItem.dataset.index);
        const toIndex = parseInt(target.dataset.index);
        
        reorderOverlayLayers(fromIndex, toIndex);
    }
    
    return false;
}

function handleDragEnd(e) {
    e.currentTarget.classList.remove('dragging');
    
    // Remove drag-over class from all items
    document.querySelectorAll('.overlay-item').forEach(item => {
        item.classList.remove('drag-over');
    });
    
    draggedItem = null;
}

function renderAnnotationsList(annotations) {
    const annotationsList = document.getElementById('annotations-list');
    annotationsList.innerHTML = '';
    
    if (annotations.length === 0) {
        annotationsList.innerHTML = '<div class="panel-desc">No annotations yet. Use tools above to add annotations.</div>';
        return;
    }
    
    annotations.forEach(ann => {
        const icons = {
            point: 'place',
            polygon: 'timeline',
            rectangle: 'crop_square',
            circle: 'circle'
        };
        
        const item = document.createElement('div');
        item.className = 'list-item';
        item.style.cursor = 'pointer';
        item.innerHTML = `
            <div class="list-item-icon">
                <span class="material-icons-round">${icons[ann.type] || 'place'}</span>
        </div>
            <div class="list-item-info">
                <div class="list-item-title editable" data-annotation-id="${ann.id}" contenteditable="false" spellcheck="false">${ann.text || 'Annotation'}</div>
                <div class="list-item-desc">${ann.type}</div>
            </div>
            <button class="icon-btn delete-btn" onclick="deleteAnnotation('${ann.id}')" title="Delete">
                <span class="material-icons-round">delete</span>
            </button>
        `;
        
        // Click to focus on annotation and center map
        item.addEventListener('click', (e) => {
            const titleEl = item.querySelector('.editable');
            if (!e.target.closest('.icon-btn') && !titleEl.isContentEditable && ann._leafletLayer) {
                // Close the sheet to focus on map
                closeBottomSheet();
                
                // Center map on annotation
                if (ann.type === 'point') {
                    map.setView([ann.coordinates[0].lat, ann.coordinates[0].lng], Math.max(map.getZoom(), 6));
                } else {
                    map.fitBounds(ann._leafletLayer.getBounds(), {padding: [50, 50]});
                }
                ann._leafletLayer.openPopup();
            }
        });
        
        // Make title editable with inline editing
        const titleEl = item.querySelector('.editable');
        
        // Click on title to edit
        titleEl.addEventListener('click', (e) => {
            e.stopPropagation();
            enableInlineEdit(titleEl, ann);
        });
        
        // Save on blur (clicking outside)
        titleEl.addEventListener('blur', () => {
            saveInlineEdit(titleEl, ann);
        });
        
        // Save on Enter, Cancel on Escape
        titleEl.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                titleEl.blur(); // Trigger save
            } else if (e.key === 'Escape') {
                e.preventDefault();
                cancelInlineEdit(titleEl, ann);
            }
        });
        
        annotationsList.appendChild(item);
    });
}

// Inline editing functions for annotations
function enableInlineEdit(element, annotation) {
    // Store original value for potential cancel
    element.dataset.originalValue = element.textContent;
    
    // Enable editing
    element.contentEditable = true;
    element.classList.add('editing');
    
    // Focus and select all text
    element.focus();
    
    // Select all text for easy replacement
    const range = document.createRange();
    range.selectNodeContents(element);
    const selection = window.getSelection();
    selection.removeAllRanges();
    selection.addRange(range);
}

function saveInlineEdit(element, annotation) {
    if (!element.isContentEditable) return;
    
    const newName = element.textContent.trim();
    const originalName = element.dataset.originalValue;
    
    // Disable editing
    element.contentEditable = false;
    element.classList.remove('editing');
    
    // If name changed, update
    if (newName && newName !== originalName) {
        updateAnnotationName(annotation.id, newName);
    } else {
        // Restore original if empty or unchanged
        element.textContent = originalName;
    }
    
    delete element.dataset.originalValue;
}

function cancelInlineEdit(element, annotation) {
    if (!element.isContentEditable) return;
    
    // Restore original value
    element.textContent = element.dataset.originalValue;
    
    // Disable editing
    element.contentEditable = false;
    element.classList.remove('editing');
    
    delete element.dataset.originalValue;
    element.blur();
}

async function updateAnnotationName(annotationId, newName) {
    try {
        const annotation = AppState.annotations.find(a => a.id === annotationId);
        if (!annotation) {
            console.error('Annotation not found:', annotationId);
            return;
        }
        
        // Store old name for logging
        const oldName = annotation.text;
        
        // Update in-memory object
        annotation.text = newName;
        console.log(`📝 Updated annotation: "${oldName}" → "${newName}"`);
        
        // Update the popup on the map marker with editable version
        if (annotation._leafletLayer) {
            const popupContent = createEditablePopup(annotation);
            annotation._leafletLayer.setPopupContent(popupContent);
            
            // If popup is open, re-setup editing
            if (annotation._leafletLayer.isPopupOpen()) {
                setTimeout(() => setupPopupEditing(annotation), 10);
            }
        }
        
        // Update the Tools panel list immediately (before API call for instant feedback)
        renderAnnotationsList(AppState.annotations);
        
        // Prepare update payload with only the fields the backend expects
        const updatePayload = {
            map_view_id: annotation.map_view_id || null,
            type: annotation.type,
            coordinates: annotation.coordinates,
            text: newName,
            color: annotation.color,
            properties: annotation.properties || {},
            link_target: annotation.link_target || null
        };
        
        console.log('📤 Sending update to backend:', updatePayload);
        
        // Save to backend
        await apiRequest(`/api/annotations/${annotationId}`, {
            method: 'PUT',
            body: JSON.stringify(updatePayload)
        });
        
        console.log('✅ Backend update successful');
        showStatus('Name updated', 'success');
    } catch (error) {
        console.error('Failed to update annotation name:', error);
        showStatus('Failed to update name', 'error');
        
        // Re-render list in case of error to show correct state
        renderAnnotationsList(AppState.annotations);
    }
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
// Overlay Dataset Modal
// ============================================================================

// State for dataset configuration
let selectedOverlayDataset = null;
let selectedOverlayVariant = null;
let selectedOverlayDate = null;

function openOverlayDatasetModal() {
    const modal = document.getElementById('overlay-dataset-modal');
    const backdrop = document.getElementById('modal-backdrop');
    
    // Reset selection state
    selectedOverlayDataset = null;
    selectedOverlayVariant = null;
    selectedOverlayDate = null;
    
    // Show dataset list, hide config
    showDatasetList();
    
    // Populate filters
    populateOverlayFilters();
    
    // Show all datasets initially (use allDatasets to show complete catalog)
    renderOverlayDatasetsList(AppState.allDatasets);
    
    // Show modal and backdrop
    backdrop.classList.remove('hidden');
    modal.classList.remove('hidden');
}

function closeOverlayDatasetModal() {
    const modal = document.getElementById('overlay-dataset-modal');
    const backdrop = document.getElementById('modal-backdrop');
    
    modal.classList.add('hidden');
    backdrop.classList.add('hidden');
}

function showDatasetList() {
    document.getElementById('overlay-datasets-list').classList.remove('hidden');
    document.querySelector('.modal-filters').classList.remove('hidden');
    document.querySelector('.modal-subtitle').classList.remove('hidden');
    document.getElementById('overlay-dataset-config').classList.add('hidden');
}

function showDatasetConfig() {
    document.getElementById('overlay-datasets-list').classList.add('hidden');
    document.querySelector('.modal-filters').classList.add('hidden');
    document.querySelector('.modal-subtitle').classList.add('hidden');
    document.getElementById('overlay-dataset-config').classList.remove('hidden');
}

function populateOverlayFilters() {
    const categoryFilter = document.getElementById('overlay-category-filter');
    const subjectFilter = document.getElementById('overlay-subject-filter');
    
    // Clear existing options (keep "All" option)
    categoryFilter.innerHTML = '<option value="">All Categories</option>';
    
    // Populate categories from complete catalog
    const categories = [...new Set(AppState.allDatasets.map(d => d.category))].sort();
    categories.forEach(category => {
        const option = document.createElement('option');
        option.value = category;
        option.textContent = category.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
        categoryFilter.appendChild(option);
    });
    
    // Populate subjects based on current category selection
    updateSubjectFilter();
}

function updateSubjectFilter() {
    const categoryFilter = document.getElementById('overlay-category-filter');
    const subjectFilter = document.getElementById('overlay-subject-filter');
    const selectedCategory = categoryFilter.value;
    
    // Clear existing subjects
    subjectFilter.innerHTML = '<option value="">All Subjects</option>';
    
    // Get subjects based on selected category
    const datasetsToFilter = selectedCategory 
        ? AppState.allDatasets.filter(d => d.category === selectedCategory)
        : AppState.allDatasets;
    
    const subjects = [...new Set(datasetsToFilter.map(d => d.subject))].sort();
    subjects.forEach(subject => {
        const option = document.createElement('option');
        option.value = subject;
        option.textContent = subject.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
        subjectFilter.appendChild(option);
    });
}

function filterOverlayDatasets() {
    const categoryFilter = document.getElementById('overlay-category-filter').value;
    const subjectFilter = document.getElementById('overlay-subject-filter').value;
    
    // Always filter from complete catalog
    let filtered = AppState.allDatasets;
    
    if (categoryFilter) {
        filtered = filtered.filter(d => d.category === categoryFilter);
    }
    
    if (subjectFilter) {
        filtered = filtered.filter(d => d.subject === subjectFilter);
    }
    
    renderOverlayDatasetsList(filtered);
}

function renderOverlayDatasetsList(datasets) {
    const listEl = document.getElementById('overlay-datasets-list');
    listEl.innerHTML = '';
    
    if (datasets.length === 0) {
        listEl.innerHTML = '<div class="panel-desc">No datasets found</div>';
        return;
    }
    
    datasets.forEach(dataset => {
        const card = document.createElement('div');
        card.className = 'overlay-dataset-card';
        
        const badges = [];
        if (dataset.supports_time_series) {
            badges.push('<span class="layer-badge"><span class="material-icons-round" style="font-size: 14px;">schedule</span>Time</span>');
        }
        if (dataset.variants && dataset.variants.length > 1) {
            badges.push(`<span class="layer-badge">${dataset.variants.length} variants</span>`);
        }
        
        card.innerHTML = `
            <span class="material-icons-round">terrain</span>
            <div class="overlay-dataset-info">
                <div class="overlay-dataset-name">
                    ${dataset.name}
                    ${badges.join(' ')}
                </div>
                <div class="overlay-dataset-meta">
                    ${dataset.category.replace('_', ' ')} › ${dataset.subject.replace('_', ' ')}
                </div>
            </div>
        `;
        
        card.addEventListener('click', async () => {
            // Show configuration screen for this dataset
            await showDatasetConfiguration(dataset);
        });
        
        listEl.appendChild(card);
    });
}

async function showDatasetConfiguration(dataset) {
    selectedOverlayDataset = dataset;
    
    // Update title
    document.getElementById('config-dataset-name').textContent = dataset.name;
    
    // Load and show variants
    const variants = await loadDatasetVariants(dataset.id);
    renderConfigVariants(variants);
    
    // Show/hide date picker based on time-series support
    if (dataset.supports_time_series) {
        const dateSection = document.getElementById('config-date-section');
        const datePicker = document.getElementById('config-date-picker');
        const dateRangeInfo = document.getElementById('config-date-range-info');
        
        dateSection.classList.remove('hidden');
        
        // Set date range
        if (dataset.date_range_start && dataset.date_range_end) {
            const start = new Date(dataset.date_range_start).toLocaleDateString('en-US', { year: 'numeric', month: 'short' });
            const end = new Date(dataset.date_range_end).toLocaleDateString('en-US', { year: 'numeric', month: 'short' });
            dateRangeInfo.textContent = `(${start} - ${end})`;
            datePicker.min = dataset.date_range_start;
            datePicker.max = dataset.date_range_end;
        }
        
        // Set default date
        const defaultDate = dataset.default_date || AppState.currentDate;
        datePicker.value = defaultDate;
        selectedOverlayDate = defaultDate;
    } else {
        document.getElementById('config-date-section').classList.add('hidden');
        selectedOverlayDate = null;
    }
    
    // Switch to config view
    showDatasetConfig();
}

function renderConfigVariants(variants) {
    const container = document.getElementById('config-variant-selector');
    container.innerHTML = '';
    
    if (!variants || variants.length === 0) return;
    
    // Auto-select default or first variant
    selectedOverlayVariant = variants.find(v => v.is_default) || variants[0];
    
    variants.forEach(variant => {
        const card = document.createElement('div');
        card.className = 'variant-card';
        if (variant.id === selectedOverlayVariant.id) {
            card.classList.add('active');
        }
        
        card.innerHTML = `
            <div class="variant-name">${variant.name}</div>
            <div class="variant-desc">${variant.description}</div>
        `;
        
        card.addEventListener('click', () => {
            selectedOverlayVariant = variant;
            // Update active state
            container.querySelectorAll('.variant-card').forEach(c => c.classList.remove('active'));
            card.classList.add('active');
        });
        
        container.appendChild(card);
    });
}

// ============================================================================
// UI Event Handlers
// ============================================================================

function initializeEventListeners() {
    // Bottom sheet drag/tap to expand/collapse
    const sheetHandle = document.getElementById('sheet-handle');
    const controlSheet = document.getElementById('control-sheet');
    const floatingButtons = document.getElementById('floating-buttons');
    
    sheetHandle.addEventListener('click', () => {
        closeBottomSheet();
    });
    
    // Floating action buttons
    const floatingBtns = document.querySelectorAll('.floating-btn');
    floatingBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const panelId = btn.id.replace('floating-btn-', 'panel-');
            openBottomSheet(panelId);
        });
    });
    
    // Sheet tabs (inside bottom sheet)
    const sheetTabs = document.querySelectorAll('.sheet-tab');
    const sheetTabsContainer = document.querySelector('.sheet-tabs');
    
    function updateTabIndicator(activeTab) {
        if (!activeTab || !sheetTabsContainer) return;
        
        const containerRect = sheetTabsContainer.getBoundingClientRect();
        const tabRect = activeTab.getBoundingClientRect();
        
        const left = tabRect.left - containerRect.left;
        const width = tabRect.width;
        
        sheetTabsContainer.style.setProperty('--tab-left', `${left}px`);
        sheetTabsContainer.style.setProperty('--tab-width', `${width}px`);
    }
    
    sheetTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const panelId = tab.id.replace('tab-', 'panel-');
            switchPanel(panelId);
            
            // Update active state
            sheetTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            // Update sliding indicator position
            updateTabIndicator(tab);
        });
    });
    
    // Initialize tab indicator on load
    const initializeTabIndicator = () => {
        const activeTab = document.querySelector('.sheet-tab.active');
        if (activeTab && sheetTabsContainer) {
            updateTabIndicator(activeTab);
        }
    };
    
    // Try multiple times to ensure tabs are rendered
    setTimeout(initializeTabIndicator, 100);
    setTimeout(initializeTabIndicator, 300);
    
    // Also update on window resize
    window.addEventListener('resize', () => {
        const activeTab = document.querySelector('.sheet-tab.active');
        if (activeTab) {
            updateTabIndicator(activeTab);
        }
    });
    
    // Note: Subject cards are now rendered dynamically in renderCategoriesWithSubjects()
    // Event listeners are added there
    
    // Date pickers (both panel and dropdown)
    const datePicker = document.getElementById('date-picker');
    const datePickerDropdown = document.getElementById('date-picker-dropdown');
    
    datePicker.value = AppState.currentDate;
    datePickerDropdown.value = AppState.currentDate;
    
    datePicker.addEventListener('change', (e) => {
        AppState.currentDate = e.target.value;
        datePickerDropdown.value = e.target.value;
        updateBaseLayer();
    });
    
    datePickerDropdown.addEventListener('change', (e) => {
        AppState.currentDate = e.target.value;
        datePicker.value = e.target.value;
        updateBaseLayer();
    });
    
    // Quick date buttons
    document.querySelectorAll('.date-quick-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const offset = parseInt(btn.dataset.offset);
            const newDate = new Date();
            newDate.setDate(newDate.getDate() + offset);
            
            // Format date as YYYY-MM-DD
            const dateStr = newDate.toISOString().split('T')[0];
            
            // Check if date is within dataset range
            const dateInput = document.getElementById('date-picker');
            const min = dateInput.min;
            const max = dateInput.max;
            
            if ((min && dateStr < min) || (max && dateStr > max)) {
                showStatus(`Date out of range. Available: ${min} to ${max}`, 'warning');
                return;
            }
            
            AppState.currentDate = dateStr;
            datePicker.value = dateStr;
            updateBaseLayer();
        });
    });
    
    // Map controls
    document.getElementById('btn-zoom-in').addEventListener('click', () => map.zoomIn());
    document.getElementById('btn-zoom-out').addEventListener('click', () => map.zoomOut());
    document.getElementById('btn-fullscreen').addEventListener('click', () => {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen();
        } else {
            document.exitFullscreen();
        }
    });
    
    // Add overlay layer button
    document.getElementById('btn-add-overlay').addEventListener('click', () => {
        openOverlayDatasetModal();
    });
    
    // Close overlay modal button
    document.getElementById('btn-close-overlay-modal').addEventListener('click', () => {
        closeOverlayDatasetModal();
    });
    
    // Modal backdrop click - only close if clicking the backdrop, not the modal
    const modalBackdrop = document.getElementById('modal-backdrop');
    const overlayModal = document.getElementById('overlay-dataset-modal');
    
    modalBackdrop.addEventListener('click', (e) => {
        closeOverlayDatasetModal();
    });
    
    // Prevent clicks inside modal from closing it
    overlayModal.addEventListener('click', (e) => {
        e.stopPropagation();
    });
    
    // Overlay filters
    document.getElementById('overlay-category-filter').addEventListener('change', (e) => {
        updateSubjectFilter();  // Update subjects when category changes
        filterOverlayDatasets();
    });
    
    document.getElementById('overlay-subject-filter').addEventListener('change', (e) => {
        filterOverlayDatasets();
    });
    
    // Back to list button
    document.getElementById('btn-back-to-list').addEventListener('click', () => {
        showDatasetList();
    });
    
    // Add configured overlay button
    document.getElementById('btn-add-configured-overlay').addEventListener('click', async () => {
        if (!selectedOverlayDataset || !selectedOverlayVariant) {
            showStatus('Please select a variant', 'warning');
            return;
        }
        
        // Get date if applicable
        const datePicker = document.getElementById('config-date-picker');
        const date = selectedOverlayDataset.supports_time_series ? datePicker.value : null;
        
        // Close modal
        closeOverlayDatasetModal();
        
        // Add the overlay layer
        await addOverlayLayer(selectedOverlayDataset.id, selectedOverlayVariant.id, date);
    });
    
    // Import Gigapixel Image button
    document.getElementById('btn-import-gigapixel').addEventListener('click', () => {
        openImportGigapixelModal();
    });
    
    // Close import modal button
    document.getElementById('btn-close-import-modal').addEventListener('click', () => {
        closeImportGigapixelModal();
    });
    
    // Import modal backdrop (prevent closing when clicking inside modal)
    const importModal = document.getElementById('import-gigapixel-modal');
    importModal.addEventListener('click', (e) => {
        e.stopPropagation();
    });
    
    // Import method selector buttons
    document.querySelectorAll('.method-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            switchImportMethod(btn.dataset.method);
        });
    });
    
    // File upload area
    const fileUploadArea = document.getElementById('file-upload-area');
    const fileInput = document.getElementById('file-upload-input');
    
    fileUploadArea.addEventListener('click', () => {
        fileInput.click();
    });
    
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            selectedFile = e.target.files[0];
            document.getElementById('selected-file-name').textContent = selectedFile.name;
            validateImportForm();
        }
    });
    
    // Drag and drop for file upload
    fileUploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        fileUploadArea.style.borderColor = 'var(--ios-blue)';
    });
    
    fileUploadArea.addEventListener('dragleave', () => {
        fileUploadArea.style.borderColor = '';
    });
    
    fileUploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        fileUploadArea.style.borderColor = '';
        
        if (e.dataTransfer.files.length > 0) {
            selectedFile = e.dataTransfer.files[0];
            document.getElementById('selected-file-name').textContent = selectedFile.name;
            validateImportForm();
        }
    });
    
    // Import form inputs validation
    document.getElementById('import-url-input').addEventListener('input', validateImportForm);
    document.getElementById('import-name-input').addEventListener('input', validateImportForm);
    document.getElementById('import-category-select').addEventListener('change', () => {
        updateImportSubjects();
        validateImportForm();
    });
    document.getElementById('import-subject-select').addEventListener('change', validateImportForm);
    
    // Import submit button
    document.getElementById('btn-import-submit').addEventListener('click', () => {
        submitImportGigapixel();
    });
    
    // Date picker change handler
    document.getElementById('config-date-picker').addEventListener('change', (e) => {
        selectedOverlayDate = e.target.value;
    });
    
    // New collection button
    document.getElementById('btn-new-collection').addEventListener('click', () => {
        const name = prompt('Collection name:');
        if (name) {
            createCollection(name, '');
        }
    });
    
    // Suggestions button (desktop)
    document.getElementById('btn-suggestions').addEventListener('click', () => {
        const popover = document.getElementById('suggestions-popover');
        popover.classList.toggle('hidden');
    });
    
    // Suggestions button (mobile)
    document.getElementById('btn-suggestions-mobile').addEventListener('click', () => {
        const popover = document.getElementById('suggestions-popover');
        const mobileMenu = document.getElementById('mobile-menu-dropdown');
        popover.classList.toggle('hidden');
        mobileMenu.classList.add('hidden');
    });
    
    // Search button (mobile)
    document.getElementById('btn-search-mobile').addEventListener('click', () => {
        const searchInput = document.getElementById('search-input');
        const mobileMenu = document.getElementById('mobile-menu-dropdown');
        searchInput.focus();
        mobileMenu.classList.add('hidden');
    });
    
    // Mobile menu toggle
    document.getElementById('btn-mobile-menu').addEventListener('click', () => {
        const mobileMenu = document.getElementById('mobile-menu-dropdown');
        const datasetDropdown = document.getElementById('dataset-dropdown');
        mobileMenu.classList.toggle('hidden');
        // Close dataset dropdown if open
        if (!datasetDropdown.classList.contains('hidden')) {
            datasetDropdown.classList.add('hidden');
        }
    });
    
    // Dataset dropdown button
    document.getElementById('btn-dataset-dropdown').addEventListener('click', () => {
        const dropdown = document.getElementById('dataset-dropdown');
        const btn = document.getElementById('btn-dataset-dropdown');
        
        dropdown.classList.toggle('hidden');
        btn.classList.toggle('active');
        
        // Close other popovers
        document.getElementById('suggestions-popover').classList.add('hidden');
    });
    
    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
        const dropdown = document.getElementById('dataset-dropdown');
        const btn = document.getElementById('btn-dataset-dropdown');
        
        if (!dropdown.contains(e.target) && !btn.contains(e.target)) {
            dropdown.classList.add('hidden');
            btn.classList.remove('active');
        }
    });
    
    // Tool buttons - work with any loaded dataset
    document.getElementById('tool-marker').addEventListener('click', () => {
        if (AppState.currentDataset) {
            if (AppState.drawingMode === 'marker') {
                exitDrawingMode();
            } else {
                enterDrawingMode('marker');
            }
        } else {
            showStatus('Please select a dataset first', 'warning');
        }
    });
    
    document.getElementById('tool-path').addEventListener('click', () => {
        if (AppState.currentDataset) {
            if (AppState.drawingMode === 'path') {
                exitDrawingMode();
            } else {
                enterDrawingMode('path');
            }
        } else {
            showStatus('Please select a dataset first', 'warning');
        }
    });
    
    document.getElementById('tool-rectangle').addEventListener('click', () => {
        if (AppState.currentDataset) {
            if (AppState.drawingMode === 'rectangle') {
                exitDrawingMode();
            } else {
                enterDrawingMode('rectangle');
            }
        } else {
            showStatus('Please select a dataset first', 'warning');
        }
    });
    
    document.getElementById('tool-circle').addEventListener('click', () => {
        if (AppState.currentDataset) {
            if (AppState.drawingMode === 'circle') {
                exitDrawingMode();
            } else {
                enterDrawingMode('circle');
            }
        } else {
            showStatus('Please select a dataset first', 'warning');
        }
    });
    
    // Double-click to finish path
    map.on('dblclick', (e) => {
        L.DomEvent.stop(e);
        if (AppState.drawingMode === 'path' && AppState.drawingPath.length >= 2) {
            finishPath();
        }
    });
}

function openBottomSheet(panelId) {
    const controlSheet = document.getElementById('control-sheet');
    const floatingButtons = document.getElementById('floating-buttons');
    
    // Hide floating buttons with animation
    floatingButtons.classList.add('hidden');
    
    // Show bottom sheet after a short delay
setTimeout(() => {
        controlSheet.classList.remove('hidden');
        controlSheet.classList.remove('collapsed');
        
        // Update tab indicator after sheet is visible
        setTimeout(() => {
            const activeTab = document.querySelector('.sheet-tab.active');
            const sheetTabsContainer = document.querySelector('.sheet-tabs');
            if (activeTab && sheetTabsContainer) {
                const containerRect = sheetTabsContainer.getBoundingClientRect();
                const tabRect = activeTab.getBoundingClientRect();
                const left = tabRect.left - containerRect.left;
                const width = tabRect.width;
                sheetTabsContainer.style.setProperty('--tab-left', `${left}px`);
                sheetTabsContainer.style.setProperty('--tab-width', `${width}px`);
            }
        }, 50);
    }, 100);
    
    // Switch to the selected panel
    switchPanel(panelId);
}

function closeBottomSheet() {
    const controlSheet = document.getElementById('control-sheet');
    const floatingButtons = document.getElementById('floating-buttons');
    
    // Hide bottom sheet with animation
    controlSheet.classList.add('hidden');
    
    // Show floating buttons after a short delay
    setTimeout(() => {
        floatingButtons.classList.remove('hidden');
    }, 300);
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
    
    // Update tab active states
    const sheetTabs = document.querySelectorAll('.sheet-tab');
    sheetTabs.forEach(tab => {
        const tabPanelId = tab.id.replace('tab-', 'panel-');
        if (tabPanelId === panelId) {
            tab.classList.add('active');
        } else {
            tab.classList.remove('active');
        }
    });
    
    // Re-render Explore panel to restore selected subject state
    if (panelId === 'panel-bodies') {
        renderCategoriesWithSubjects();
    }
}

// Make functions globally accessible
window.removeOverlayLayer = removeOverlayLayer;
window.deleteAnnotation = deleteAnnotation;

// ============================================================================
// Import Gigapixel Image
// ============================================================================

let importMethod = 'url'; // 'url' or 'file'
let selectedFile = null;

async function openImportGigapixelModal() {
    const modal = document.getElementById('import-gigapixel-modal');
    const backdrop = document.getElementById('modal-backdrop');
    
    // Reset form
    document.getElementById('import-url-input').value = '';
    document.getElementById('import-name-input').value = '';
    document.getElementById('import-description-input').value = '';
    document.getElementById('import-category-select').value = '';
    document.getElementById('import-subject-select').value = '';
    document.getElementById('selected-file-name').textContent = '';
    selectedFile = null;
    
    // Load ALL categories from backend (not just ones with datasets)
    try {
        const categoriesResponse = await fetch(`${BACKEND_URL}/api/categories/all`);
        const categoriesData = await categoriesResponse.json();
        
        // Populate category dropdown with ALL categories
        const categorySelect = document.getElementById('import-category-select');
        categorySelect.innerHTML = '<option value="">Select Category</option>';
        categoriesData.categories.forEach(cat => {
            const option = document.createElement('option');
            option.value = cat.id;
            option.textContent = cat.name;
            categorySelect.appendChild(option);
        });
        
        console.log(`✅ Loaded ${categoriesData.categories.length} categories for import`);
    } catch (error) {
        console.error('Failed to load categories:', error);
        // Fallback to current categories if API fails
        const categorySelect = document.getElementById('import-category-select');
        categorySelect.innerHTML = '<option value="">Select Category</option>';
        AppState.categories.forEach(cat => {
            const option = document.createElement('option');
            option.value = cat.id;
            option.textContent = cat.name;
            categorySelect.appendChild(option);
        });
    }
    
    // Show modal
    modal.classList.remove('hidden');
    backdrop.classList.remove('hidden');
    
    validateImportForm();
}

function closeImportGigapixelModal() {
    const modal = document.getElementById('import-gigapixel-modal');
    const backdrop = document.getElementById('modal-backdrop');
    
    modal.classList.add('hidden');
    backdrop.classList.add('hidden');
    
    // Hide status section
    document.getElementById('import-status').classList.add('hidden');
}

function switchImportMethod(method) {
    importMethod = method;
    
    // Update button states
    document.querySelectorAll('.method-btn').forEach(btn => {
        if (btn.dataset.method === method) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    
    // Toggle input sections
    if (method === 'url') {
        document.getElementById('import-url-section').classList.remove('hidden');
        document.getElementById('import-file-section').classList.add('hidden');
    } else {
        document.getElementById('import-url-section').classList.add('hidden');
        document.getElementById('import-file-section').classList.remove('hidden');
    }
    
    validateImportForm();
}

async function updateImportSubjects() {
    const categoryId = document.getElementById('import-category-select').value;
    const subjectSelect = document.getElementById('import-subject-select');
    
    subjectSelect.innerHTML = '<option value="">Select Subject</option>';
    
    if (!categoryId) {
        subjectSelect.disabled = true;
        validateImportForm();
        return;
    }
    
    subjectSelect.disabled = false;
    
    // Define category-to-subject mapping (matches backend)
    const categorySubjectMap = {
        'planets': ['earth', 'mars', 'mercury', 'venus', 'jupiter', 'saturn', 'uranus', 'neptune'],
        'satellites': ['moon', 'europa', 'titan', 'enceladus'],
        'galaxies': ['milky_way', 'andromeda'],
        'dwarf_planets': [],
        'nebulae': [],
        'star_clusters': [],
        'phenomena': [],
        'regions': []
    };
    
    // Load ALL subjects from backend
    try {
        const subjectsResponse = await fetch(`${BACKEND_URL}/api/subjects/all`);
        const subjectsData = await subjectsResponse.json();
        
        // Filter subjects based on selected category
        const allowedSubjects = categorySubjectMap[categoryId] || [];
        
        let filteredCount = 0;
        subjectsData.subjects.forEach(subject => {
            // Only show subjects that belong to this category
            if (allowedSubjects.length === 0 || allowedSubjects.includes(subject.id)) {
                const option = document.createElement('option');
                option.value = subject.id;
                option.textContent = subject.name;
                subjectSelect.appendChild(option);
                filteredCount++;
            }
        });
        
        console.log(`✅ Loaded ${filteredCount} subjects for category "${categoryId}"`);
    } catch (error) {
        console.error('Failed to load subjects:', error);
        // Fallback to existing logic
        const subjects = new Set();
        AppState.allDatasets
            .filter(ds => ds.category === categoryId)
            .forEach(ds => subjects.add(ds.subject));
        
        Array.from(subjects).sort().forEach(subject => {
            const option = document.createElement('option');
            option.value = subject;
            option.textContent = subject.charAt(0).toUpperCase() + subject.slice(1).replace('_', ' ');
            subjectSelect.appendChild(option);
        });
    }
    
    validateImportForm();
}

function validateImportForm() {
    const name = document.getElementById('import-name-input').value.trim();
    const category = document.getElementById('import-category-select').value;
    const subject = document.getElementById('import-subject-select').value;
    const submitBtn = document.getElementById('btn-import-submit');
    
    let hasSource = false;
    if (importMethod === 'url') {
        const url = document.getElementById('import-url-input').value.trim();
        hasSource = url.length > 0;
    } else {
        hasSource = selectedFile !== null;
    }
    
    const isValid = name && category && subject && hasSource;
    submitBtn.disabled = !isValid;
}

async function submitImportGigapixel() {
    const name = document.getElementById('import-name-input').value.trim();
    const description = document.getElementById('import-description-input').value.trim();
    const category = document.getElementById('import-category-select').value;
    const subject = document.getElementById('import-subject-select').value;
    
    // Show status
    const statusDiv = document.getElementById('import-status');
    const statusText = document.getElementById('import-status-text');
    statusDiv.classList.remove('hidden');
    statusText.textContent = 'Creating dataset...';
    
    // Disable submit button and form inputs
    document.getElementById('btn-import-submit').disabled = true;
    document.querySelectorAll('.import-input-section input, .import-input-section select').forEach(el => {
        el.disabled = true;
    });
    
    try {
        let imageUrl;
        
        if (importMethod === 'url') {
            imageUrl = document.getElementById('import-url-input').value.trim();
        } else {
            // Upload file first
            statusText.textContent = 'Uploading file...';
            imageUrl = await uploadImageFile(selectedFile);
        }
        
        statusText.textContent = 'Creating dataset...';
        
        // Create dataset via API (returns immediately)
        const response = await apiRequest('/api/datasets', {
            method: 'POST',
            body: JSON.stringify({
                name: name,
                description: description || undefined,
                category: category,
                subject: subject,
                url: imageUrl
            })
        });
        
        if (response.success) {
            const datasetId = response.dataset_id;
            const status = response.status || 'ready';
            
            console.log(`✅ Dataset created: ${datasetId}, status: ${status}`);
            
            if (status === 'processing') {
                statusText.textContent = 'Processing image...';
                showStatus('Processing image tiles...', 'info');
                
                // Wait for processing to complete (keep modal open)
                try {
                    await pollDatasetStatus(datasetId, category, subject);
                    // If we get here, processing completed successfully
                    // selectImportedDataset was called from within pollDatasetStatus
                    // Now close the modal
                    setTimeout(() => {
                        closeImportGigapixelModal();
                    }, 1500);
                } catch (pollError) {
                    // Polling failed or timed out
                    throw pollError;
                }
            } else {
                // Dataset ready immediately (pre-tiled service)
                statusText.textContent = 'Dataset ready!';
                showStatus('Dataset imported successfully!', 'success');
                
                // Select and load the new dataset (will close modal automatically)
                await selectImportedDataset(datasetId, category, subject, true);
            }
        } else {
            throw new Error(response.error || 'Failed to create dataset');
        }
    } catch (error) {
        console.error('Failed to import gigapixel image:', error);
        statusText.textContent = '❌ Import failed: ' + error.message;
        showStatus('Import failed', 'error');
        
        // Re-enable form after delay
        setTimeout(() => {
            document.getElementById('btn-import-submit').disabled = false;
            document.querySelectorAll('.import-input-section input, .import-input-section select').forEach(el => {
                el.disabled = false;
            });
        }, 3000);
    }
}

async function uploadImageFile(file) {
    // For now, return a placeholder URL
    // In production, you'd upload to a cloud storage service
    console.log('File upload not yet implemented. File:', file.name);
    throw new Error('File upload is not yet implemented. Please use URL method.');
}

async function pollDatasetStatus(datasetId, category, subject) {
    const statusText = document.getElementById('import-status-text');
    const statusSubtext = document.getElementById('import-status-subtext');
    let pollCount = 0;
    const maxPolls = 180; // 6 minutes max (180 * 2 seconds)
    
    return new Promise((resolve, reject) => {
        const checkStatus = async () => {
            try {
                pollCount++;
                const elapsedSeconds = pollCount * 2;
                const elapsedMinutes = Math.floor(elapsedSeconds / 60);
                const elapsedSecondsRemainder = elapsedSeconds % 60;
                
                console.log(`📊 Polling status for ${datasetId} (attempt ${pollCount})`);
                
                const response = await fetch(`${BACKEND_URL}/api/datasets/${datasetId}/status`);
                
                if (!response.ok) {
                    throw new Error(`Status check failed: ${response.status}`);
                }
                
                const data = await response.json();
                console.log('Status response:', data);
                
                if (data.status === 'ready') {
                    // Processing complete!
                    statusText.textContent = '✅ Dataset ready!';
                    statusSubtext.textContent = '100% complete • Loading dataset on map...';
                    showStatus('Dataset processed successfully!', 'success');
                    
                    // Set progress bar to 100%
                    const progressFill = document.getElementById('import-progress-fill');
                    if (progressFill) {
                        progressFill.style.width = '100%';
                        progressFill.style.animation = 'none';
                    }
                    
                    console.log(`✅ Dataset ${datasetId} is ready!`);
                    
                    // Select and load the new dataset (don't close modal yet)
                    try {
                        await selectImportedDataset(datasetId, category, subject, false); // Pass false to not close modal
                        resolve(data);
                    } catch (error) {
                        reject(error);
                    }
                    
                } else if (data.status === 'processing') {
                    // Still processing - show detailed progress
                    const progress = data.progress || '';
                    const percentage = data.percentage || 0;
                    const message = data.message || 'Processing...';
                    
                    // Update progress bar
                    const progressFill = document.getElementById('import-progress-fill');
                    if (progressFill) {
                        progressFill.style.width = `${percentage}%`;
                        progressFill.style.animation = 'none'; // Remove indeterminate animation
                    }
                    
                    // Update main text with icon based on progress
                    let icon = '⏳';
                    if (progress === 'downloading') {
                        icon = '⬇️';
                    } else if (progress === 'generating_tiles') {
                        icon = '🔨';
                    } else if (progress === 'queued') {
                        icon = '⏱️';
                    } else if (progress === 'finalizing') {
                        icon = '✨';
                    }
                    
                    statusText.textContent = `${icon} ${message}`;
                    
                    // Update subtext with percentage and elapsed time
                    const timeStr = elapsedMinutes > 0 
                        ? `${elapsedMinutes}m ${elapsedSecondsRemainder}s`
                        : `${elapsedSeconds}s`;
                    statusSubtext.textContent = `${percentage}% complete • ${timeStr} elapsed`;
                    
                    // Check if we've exceeded max polls
                    if (pollCount >= maxPolls) {
                        throw new Error('Processing timeout - taking too long');
                    }
                    
                    // Continue polling
                    setTimeout(checkStatus, 2000); // Check again in 2 seconds
                    
                } else if (data.status === 'failed' || data.status === 'error') {
                    // Processing failed - show detailed error
                    const errorMsg = data.error || data.message || 'Processing failed';
                    statusText.textContent = `❌ Processing failed`;
                    statusSubtext.textContent = errorMsg;
                    showStatus('Failed to process dataset', 'error');
                    
                    // Reset progress bar to 0
                    const progressFill = document.getElementById('import-progress-fill');
                    if (progressFill) {
                        progressFill.style.width = '0%';
                        progressFill.style.animation = 'none';
                    }
                    
                    console.error(`❌ Dataset ${datasetId} processing failed:`, errorMsg);
                    reject(new Error(errorMsg));
                    
                } else {
                    // Unknown status
                    console.warn('Unknown status:', data.status);
                    statusText.textContent = '⏳ Processing...';
                    statusSubtext.textContent = `Status: ${data.status}`;
                    setTimeout(checkStatus, 2000);
                }
                
            } catch (error) {
                console.error('Failed to check dataset status:', error);
                
                // Retry a few times on network errors
                if (pollCount < 5) {
                    statusText.textContent = '⚠️ Connection issue...';
                    statusSubtext.textContent = 'Retrying...';
                    setTimeout(checkStatus, 3000); // Retry in 3 seconds
                } else {
                    statusText.textContent = '❌ Failed to check status';
                    statusSubtext.textContent = error.message || 'Network error';
                    showStatus('Status check failed', 'error');
                    reject(error);
                }
            }
        };
        
        // Start polling
        checkStatus();
    });
}

async function selectImportedDataset(datasetId, category, subject, shouldCloseModal = true) {
    try {
        console.log(`🎯 Selecting imported dataset: ${datasetId}`);
        
        // Fetch the complete dataset details
        const dataset = await apiRequest(`/api/datasets/${datasetId}`);
        console.log('Dataset details:', dataset);
        
        // Check if dataset is still processing
        if (dataset.processing_status === 'processing') {
            console.warn('⚠️ Dataset is still processing, cannot load yet');
            showStatus('Dataset is still processing...', 'warning');
            return; // Don't try to load it yet
        }
        
        // Check if processing failed
        if (dataset.processing_status === 'failed') {
            console.error('❌ Dataset processing failed');
            showStatus('Dataset processing failed', 'error');
            throw new Error('Dataset processing failed');
        }
        
        // Update AppState
        AppState.currentCategory = category;
        AppState.currentSubject = subject;
        AppState.currentDataset = dataset;
        
        // Load variants for this dataset
        const variants = await loadDatasetVariants(datasetId);
        console.log('Dataset variants:', variants);
        
        if (variants && variants.length > 0) {
            // Check if variant has valid tile URL
            const defaultVariant = variants.find(v => v.is_default) || variants[0];
            
            if (!defaultVariant.tile_url_template || defaultVariant.tile_url_template === '') {
                console.warn('⚠️ Variant has no tile URL yet');
                showStatus('Tiles not ready yet...', 'warning');
                return; // Don't try to load without tile URLs
            }
            
            // Select default or first variant
            AppState.currentVariant = defaultVariant;
            
            // Render variant selector
            renderVariantSelector(variants);
            
            // Update date picker visibility
            updateDatePickerVisibility(dataset);
            
            // Update the base layer with the new dataset
            await updateBaseLayer();
            
            console.log(`✅ Dataset ${datasetId} loaded and displayed on map!`);
            showStatus('Dataset loaded successfully!', 'success');
        }
        
        // Reload catalog to show the new dataset in lists
        await loadCategories();  // Reload categories first (includes new category if needed)
        await loadDatasets();    // Then reload datasets
        renderCategoriesWithSubjects();  // Re-render the explore panel
        
        // Update breadcrumb
        updateBreadcrumb();
        
        // Close modal after successful load (if requested)
        if (shouldCloseModal) {
            setTimeout(() => {
                closeImportGigapixelModal();
            }, 1500);
        }
        
    } catch (error) {
        console.error('Failed to select imported dataset:', error);
        showStatus('Failed to load dataset', 'error');
        throw error; // Re-throw to let caller handle it
    }
}

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
        const response = await fetch(`${BACKEND_URL}/api/health`);
        const data = await response.json();
        console.log('✓ Backend connected:', data);
        showStatus('Connected', 'success');
    } catch (error) {
        console.error('❌ Backend not available:', error);
        showStatus('Backend offline', 'error');
        return;
    }
    
    // Load catalog data
    console.log('📦 Loading catalog data...');
    await loadCategories();
    console.log('Categories loaded:', AppState.categories);
    
    await loadSources();
    console.log('Sources loaded:', AppState.sources);
    
    // Load ALL datasets to populate subject counts
    console.log('📊 Loading all datasets...');
    const allDatasets = await loadDatasets();
    AppState.datasets = allDatasets;
    AppState.allDatasets = allDatasets;  // Store complete catalog separately
    console.log(`Datasets loaded: ${allDatasets.length} total`);
    
    // Render categories with subjects
    console.log('🎨 Rendering categories with subjects...');
    renderCategoriesWithSubjects();
    console.log('Categories rendered');
    
    await loadCollections();
    
    // Set initial state
    AppState.currentCategory = 'planets';
    AppState.currentSubject = 'earth';
    
    // Load initial datasets for the default subject (Earth)
    const datasets = await loadDatasets('planets', 'earth');
    if (datasets.length > 0) {
        // Select first dataset
        AppState.currentDataset = datasets[0];
        
        // Load its variants
        const variants = await loadDatasetVariants(datasets[0].id);
        if (variants.length > 0) {
            AppState.currentVariant = variants.find(v => v.is_default) || variants[0];
            
            // Show variant selector
            renderVariantSelector(variants);
            
            // Update date picker
            updateDatePickerVisibility(datasets[0]);
            
            // Update map with default dataset
            await updateBaseLayer();
        }
        
        // Render datasets list
        renderDatasetsList(datasets);
        
        // Update breadcrumb
        updateBreadcrumb();
    }
    
    // Load saved annotations AFTER map is fully initialized
    console.log('📍 Loading annotations...');
    await loadAnnotations();
    console.log(`Annotations loaded: ${AppState.annotations.length} total`);

    
    console.log('✅ App initialization complete!');
    console.log('🎨 Enjoy the iOS 26-inspired interface!');
}

// Start the app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}
