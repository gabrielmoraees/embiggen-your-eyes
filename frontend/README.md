# Embiggen Your Eyes - Frontend

Frontend application for NASA Space Apps Challenge 2025 - Embiggen Your Eyes project.

## Overview

This frontend provides an interactive web-based viewer for extremely large NASA satellite images using tiled web maps. It leverages NASA's Global Imagery Browse Services (GIBS) to efficiently load and display high-resolution Earth imagery.

## Technology Stack

- **Leaflet.js**: Lightweight, mobile-friendly mapping library
- **NASA GIBS**: Global Imagery Browse Services for satellite imagery
- **Vanilla JavaScript**: No framework dependencies for simplicity
- **HTML5/CSS3**: Modern, responsive design

## Why Leaflet?

After evaluating Leaflet, OpenLayers, and OpenSeadragon:

- **Leaflet** was chosen because:
  - Excellent integration with NASA GIBS (NASA provides official Leaflet examples)
  - Lightweight (~42KB) and simple to use
  - Perfect for tiled web maps with WMS/WMTS support
  - Outstanding mobile gesture support out of the box
  - Easy marker management and smooth animations
  - Large community and ecosystem
  - Built-in support for overlays and custom drawing (via plugins)

## Features

- ✅ Load extremely large NASA satellite images as tiled web maps
- ✅ Smooth zoom and pan navigation
- ✅ Add and manage markers with smooth fly-to transitions
- ✅ Multiple NASA GIBS layers (MODIS, VIIRS, Blue Marble, etc.)
- ✅ Date selection for temporal imagery
- ✅ Desktop and mobile support with gesture controls
- ✅ Responsive UI with collapsible control panel
- ✅ Real-time coordinate and zoom level display
- ✅ Keyboard shortcuts for productivity
- 🚧 Ready for overlay support (future)
- 🚧 Ready for custom path drawing (future - via Leaflet.draw plugin)

## NASA GIBS Integration

### What is GIBS?

NASA's Global Imagery Browse Services (GIBS) provides quick access to over 1,000 satellite imagery products, covering every part of the world. Images are provided as tiled web maps compatible with standards like WMTS and WMS.

### Available Layers

The application currently supports these GIBS layers:

1. **MODIS Terra True Color** - Daily global imagery from Terra satellite
2. **VIIRS SNPP True Color** - Daily high-resolution visible imagery
3. **MODIS Aqua True Color** - Daily global imagery from Aqua satellite
4. **Blue Marble Next Generation** - Static Earth composite
5. **Land Surface Temperature** - Thermal imaging

### API Request Examples

#### WMTS Tile Request Format
```
https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/{Layer}/default/{Date}/{Resolution}/{Z}/{Y}/{X}.{Format}
```

#### Example Request - MODIS True Color Tile
```
https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/2025-10-04/250m/2/1/1.jpg
```

**Parameters:**
- `epsg3857`: Web Mercator projection (standard for web maps)
- `best`: Quality tier
- `Layer`: `MODIS_Terra_CorrectedReflectance_TrueColor`
- `Date`: `2025-10-04` (YYYY-MM-DD format)
- `Resolution`: `250m`
- `Z/Y/X`: Tile coordinates (zoom/row/column)
- `Format`: `jpg` (or `png` for layers with transparency)

#### Example Request - VIIRS True Color
```
https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/VIIRS_SNPP_CorrectedReflectance_TrueColor/default/2025-10-04/250m/3/2/3.jpg
```

#### GetCapabilities Request (to discover available layers)
```
https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/wmts.cgi?SERVICE=WMTS&REQUEST=GetCapabilities
```

### Working with Different Projections

GIBS supports multiple projections:

- **EPSG:3857** (Web Mercator): Best for web maps - `https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/`
- **EPSG:4326** (Geographic): Best for scientific applications - `https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/`
- **EPSG:3413** (Polar Stereographic North): Arctic imagery
- **EPSG:3031** (Polar Stereographic South): Antarctic imagery

### Additional NASA Data Sources

Beyond GIBS, you can also access:

1. **NASA Worldview**: Interactive imagery explorer
   - URL: https://worldview.earthdata.nasa.gov/
   
2. **NASA Earth Observatory**: Curated imagery
   - API: https://api.nasa.gov/
   
3. **LANCE (Land, Atmosphere Near real-time Capability for EOS)**
   - Near real-time data: https://lance.nasa.gov/

## Running the Application

### Option 1: Python HTTP Server (Recommended)

```bash
cd frontend
python -m http.server 8000
```

Then open your browser to: http://localhost:8000

### Option 2: Python 3 HTTP Server

```bash
cd frontend
python3 -m http.server 8000
```

### Option 3: Node.js HTTP Server

```bash
cd frontend
npx http-server -p 8000
```

### Option 4: PHP Built-in Server

```bash
cd frontend
php -S localhost:8000
```

### Option 5: Live Server (VS Code Extension)

1. Install "Live Server" extension in VS Code
2. Right-click `index.html`
3. Select "Open with Live Server"

## Usage Guide

### Basic Navigation

- **Zoom**: Mouse wheel, pinch gesture (mobile), or +/- buttons
- **Pan**: Click and drag, or swipe (mobile)
- **Reset**: Double-click to zoom in

### Adding Markers

1. Click "Add Marker" button (or press 'M')
2. Click on the map to place a marker
3. Markers appear in the list with coordinates

### Navigating to Markers

- Click "Go" button next to any marker in the list
- The map will smoothly fly to that location
- Marker popup opens automatically

### Changing Imagery

1. Select a layer from the dropdown
2. Choose a date (for temporal layers)
3. Click "Update" to refresh the imagery

### Keyboard Shortcuts

- **M**: Toggle add marker mode
- **P**: Toggle control panel

## Mobile Support

The application is fully responsive and supports:
- Touch gestures (pinch to zoom, swipe to pan)
- Optimized UI for small screens
- Collapsible control panel for more viewing space

## Project Structure

```
frontend/
├── index.html      # Main HTML structure
├── styles.css      # Styling and responsive design
├── app.js          # Application logic and NASA GIBS integration
└── README.md       # This file
```

## Future Enhancements

### Ready to Implement

1. **Overlays**: Add multiple layers simultaneously
   ```javascript
   const overlay = L.tileLayer(overlayUrl).addTo(map);
   ```

2. **Custom Path Drawing**: Using Leaflet.draw plugin
   ```html
   <script src="https://unpkg.com/leaflet-draw@latest/dist/leaflet.draw.js"></script>
   ```

3. **Image Export**: Capture current view
   ```javascript
   // Using leaflet-image plugin
   ```

4. **Measurement Tools**: Distance and area calculation
   ```javascript
   // Using Leaflet.measure plugin
   ```

5. **Time Series Animation**: Animate through dates
6. **Layer Comparison**: Split screen or opacity slider
7. **Marker Clustering**: For large numbers of markers
8. **Search Functionality**: Geocoding for place names
9. **Data Visualization**: Add charts and statistics

## NASA GIBS Resources

- **Documentation**: https://nasa-gibs.github.io/gibs-api-docs/
- **Available Products**: https://nasa-gibs.github.io/gibs-api-docs/available-visualizations/
- **Worldview**: https://worldview.earthdata.nasa.gov/ (inspiration and testing)
- **GitHub Examples**: https://github.com/nasa-gibs/gibs-web-examples

## Browser Compatibility

- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- Mobile browsers: ✅ Full support

## Performance Notes

- Tiles are cached by the browser for faster subsequent loads
- Only visible tiles at current zoom level are loaded
- Images are progressive JPEG for faster rendering
- Maximum zoom level is limited to balance quality and performance

## Troubleshooting

### Images not loading?

1. Check your internet connection
2. Verify the date is valid (GIBS has data from ~2000 onwards)
3. Some layers may not have data for recent dates (24-48 hour delay)
4. Open browser console (F12) to check for errors

### Tiles appear gray or missing?

- The selected date may not have coverage for that layer
- Try a different date or layer
- Check the NASA GIBS status page

### Performance issues?

- Close other browser tabs
- Clear browser cache
- Try a lower zoom level
- Some layers are more demanding than others

## Development

To add new features:

1. **Add a new GIBS layer**: Update the `layer-select` options in `index.html`
2. **Add overlays**: Create additional tile layers in `app.js`
3. **Custom markers**: Modify the `addMarker()` function
4. **Drawing tools**: Install Leaflet.draw plugin

## License

See the main project LICENSE file.

## Credits

- NASA GIBS for providing satellite imagery
- Leaflet.js for the mapping library
- NASA Space Apps Challenge 2025

---

Built for NASA Space Apps Challenge 2025 🚀🌍

