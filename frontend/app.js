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
    overlayLayers: [],
    
    // Catalog data
    categories: [],
    datasets: [],
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
        const annotations = await apiRequest(endpoint);
        AppState.annotations = annotations;
        
        // Display all annotations on map
        annotations.forEach(ann => displayAnnotationOnMap(ann));
        
        renderAnnotationsList(annotations);
        return annotations;
    } catch (error) {
        console.error('Failed to load annotations:', error);
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
        
        // Create new base layer
        gibsLayer = createTileLayer(variant.tile_url, variant.max_zoom || 18, attribution);
    gibsLayer.addTo(map);
    
        // Update UI
        const baseLayerName = document.getElementById('base-layer-name');
        if (baseLayerName) {
            baseLayerName.textContent = `${AppState.currentDataset.name} - ${variant.name}`;
        }
        
        // Update map attribution
        map.attributionControl.setPrefix('');
        
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
    
    const annotation = await createAnnotation(
        'point',
        [{lat: latlng.lat, lng: latlng.lng}],
        name,
        '#007AFF'
    );
    
    if (annotation) {
        displayAnnotationOnMap(annotation);
        showStatus('Marker added', 'success');
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
        displayAnnotationOnMap(annotation);
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
        displayAnnotationOnMap(annotation);
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
        displayAnnotationOnMap(annotation);
        showStatus('Circle created', 'success');
    }
    
    exitDrawingMode();
}

function displayAnnotationOnMap(annotation) {
    let layer;
    
    if (annotation.type === 'point') {
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
        layer.bindPopup(`
            <div style="font-family: -apple-system, sans-serif;">
                <strong>${annotation.text || 'Annotation'}</strong><br>
                <small style="color: #666;">Type: ${annotation.type}</small>
            </div>
        `);
        layer.addTo(map);
        
        // Store reference for cleanup
        if (!annotation._leafletLayer) {
            annotation._leafletLayer = layer;
        }
    }
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
    
    // Collapse the bottom sheet to focus on map
    const controlSheet = document.getElementById('control-sheet');
    if (controlSheet && !controlSheet.classList.contains('collapsed')) {
        controlSheet.classList.add('collapsed');
    }
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
            
            AppState.currentCategory = category;
            AppState.currentSubject = subject;
            
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
            
            // Switch to datasets panel
            switchPanel('panel-layers');
            document.getElementById('btn-layers').classList.add('active');
            document.getElementById('btn-bodies').classList.remove('active');
        });
    });
}

function updateBreadcrumb() {
    const breadcrumb = document.getElementById('dataset-breadcrumb');
    if (!breadcrumb) return;
    
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
    
    breadcrumb.textContent = parts.join(' › ');
}

function renderDatasetsList(datasets) {
    const layersList = document.getElementById('layers-list');
    if (!layersList) {
        console.error('layers-list element not found');
        return;
    }
    
    layersList.innerHTML = '';
    
    console.log(`Rendering ${datasets.length} datasets`);
    
    if (datasets.length === 0) {
        layersList.innerHTML = '<div class="panel-desc">No datasets available for this selection</div>';
        return;
    }
    
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
        
        layersList.appendChild(card);
    });
}

function renderVariantSelector(variants) {
    const variantSection = document.getElementById('variant-section');
    const variantSelector = document.getElementById('variant-selector');
    
    if (!variantSection || !variantSelector) {
        console.error('Variant selector elements not found');
        return;
    }
    
    if (!variants || variants.length === 0) {
        variantSection.classList.add('hidden');
        return;
    }
    
    // Show variant section (even for single variant to show what's selected)
    variantSection.classList.remove('hidden');
    variantSelector.innerHTML = '';
    
    console.log(`Rendering ${variants.length} variant(s), current: ${AppState.currentVariant?.id}`);
    
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
            renderVariantSelector(variants);
        });
        
        variantSelector.appendChild(card);
    });
}

function updateDatePickerVisibility(dataset) {
    const dateSection = document.getElementById('date-section');
    const datePicker = document.getElementById('date-picker');
    const dateRangeInfo = document.getElementById('date-range-info');
    
    if (!dataset.supports_time_series) {
        dateSection.classList.add('hidden');
        return;
    }
    
    dateSection.classList.remove('hidden');
    
    // Set date range
    if (dataset.date_range_start && dataset.date_range_end) {
        const start = new Date(dataset.date_range_start).toLocaleDateString('en-US', { year: 'numeric', month: 'short' });
        const end = new Date(dataset.date_range_end).toLocaleDateString('en-US', { year: 'numeric', month: 'short' });
        dateRangeInfo.textContent = `(${start} - ${end})`;
        
        // Set min/max on date picker
        datePicker.min = dataset.date_range_start;
        datePicker.max = dataset.date_range_end;
    } else {
        dateRangeInfo.textContent = '';
    }
    
    // Set default value
    if (dataset.default_date) {
        datePicker.value = dataset.default_date;
        AppState.currentDate = dataset.default_date;
    }
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
                <div class="list-item-title editable" data-annotation-id="${ann.id}">${ann.text || 'Annotation'}</div>
                <div class="list-item-desc">${ann.type}</div>
            </div>
            <button class="icon-btn delete-btn" onclick="deleteAnnotation('${ann.id}')" title="Delete">
                <span class="material-icons-round">delete</span>
            </button>
        `;
        
        // Click to focus on annotation and center map
        item.addEventListener('click', (e) => {
            if (!e.target.closest('.icon-btn') && !e.target.classList.contains('editable') && ann._leafletLayer) {
                // Collapse the sheet to focus on map
                const controlSheet = document.getElementById('control-sheet');
                if (controlSheet) {
                    controlSheet.classList.add('collapsed');
                }
                
                // Center map on annotation
                if (ann.type === 'point') {
                    map.setView([ann.coordinates[0].lat, ann.coordinates[0].lng], Math.max(map.getZoom(), 6));
                } else {
                    map.fitBounds(ann._leafletLayer.getBounds(), {padding: [50, 50]});
                }
                ann._leafletLayer.openPopup();
            }
        });
        
        // Make title editable on double-click
        const titleEl = item.querySelector('.editable');
        titleEl.addEventListener('dblclick', (e) => {
            e.stopPropagation();
            const newName = prompt('Edit name:', ann.text);
            if (newName && newName !== ann.text) {
                updateAnnotationName(ann.id, newName);
            }
        });
        
        annotationsList.appendChild(item);
    });
}

async function updateAnnotationName(annotationId, newName) {
    try {
        const annotation = AppState.annotations.find(a => a.id === annotationId);
        if (!annotation) return;
        
        annotation.text = newName;
        
        await apiRequest(`/api/annotations/${annotationId}`, {
            method: 'PUT',
            body: JSON.stringify(annotation)
        });
        
        renderAnnotationsList(AppState.annotations);
        showStatus('Name updated', 'success');
    } catch (error) {
        console.error('Failed to update annotation name:', error);
        showStatus('Failed to update name', 'error');
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
    
    // Note: Subject cards are now rendered dynamically in renderCategoriesWithSubjects()
    // Event listeners are added there
    
    // Date picker
    const datePicker = document.getElementById('date-picker');
    datePicker.value = AppState.currentDate;
    datePicker.addEventListener('change', (e) => {
        AppState.currentDate = e.target.value;
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
    
    // Re-render Explore panel to restore selected subject state
    if (panelId === 'panel-bodies') {
        renderCategoriesWithSubjects();
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
    
    console.log('✅ App initialization complete!');
    console.log('🎨 Enjoy the iOS 26-inspired interface!');
}

// Start the app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}
