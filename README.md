<<<<<<< Updated upstream
# 🔭 Embiggen Your Eyes

**NASA Space Apps Challenge 2025** - A platform for exploring, analyzing, and annotating large-scale NASA satellite imagery with Google Maps-like functionality.

## 🎯 Project Overview

This platform enables users to:
- 🔍 **Search** NASA satellite imagery by date, location, and layer type
- 🗺️ **Visualize** massive images with smooth pan and zoom (Google Maps style)
- ✏️ **Annotate** images with points, polygons, and notes
- 🔗 **Link** related images to create narrative connections
- 📊 **Compare** images side-by-side, overlay, or swipe modes
- 🤖 **Discover** related content through smart suggestions
- 📚 **Organize** images into collections

## 🏗️ Architecture

```
┌──────────────┐
│   Frontend   │  ← You build: React/Vue + Leaflet
│  (Your UI)   │
└──────┬───────┘
       │ REST API
┌──────▼───────┐
│   Backend    │  ✅ Already built: FastAPI (see /backend)
│  (FastAPI)   │     - Annotations
│              │     - Links & Graph
└──────┬───────┘     - Collections
       │             - Smart suggestions
   ┌───┴────┐
   │        │
┌──▼──┐  ┌─▼────────┐
│NASA │  │  NASA    │
│GIBS │  │CMR (API) │  ← NASA provides: Tiles & Metadata
└─────┘  └──────────┘
```

### Key Design Decision
**We DON'T rebuild what NASA already provides!**

✅ NASA provides:
- Pre-tiled satellite imagery (billions of tiles)
- Global infrastructure (fast CDN)
- 20+ years of data
- Multiple spectral bands

✅ We provide:
- Smart annotation tools
- Image linking & relationships
- Graph-based navigation
- Comparison features
- User experience layer

## 🚀 Quick Start

### Backend (Ready to Use ✅)

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Start server
python main.py

# View API docs
open http://localhost:8000/docs
```

**API Features:**
- Search NASA imagery
- Create/manage annotations
- Link images together
- Build collections
- Get smart suggestions
- Graph navigation

📖 **Full API documentation**: See [backend/README.md](backend/README.md)

### Frontend (Integrated with Backend ✅)

```bash
cd frontend

# Start HTTP server (choose one)
./start.sh
# or
python3 -m http.server 8080
# or
npx http-server -p 8080

# Open browser
open http://localhost:8080
```

**Frontend Features:**
- ✅ Backend API integration
- ✅ Image search via backend
- ✅ Persistent annotations (saved to backend)
- ✅ Interactive map with Leaflet
- ✅ Layer selection (4 NASA GIBS layers)
- ✅ Date picker
- ✅ Marker tools
- 🚧 Collections (backend ready, UI pending)
- 🚧 Image linking (backend ready, UI pending)
- 🚧 Smart suggestions (backend ready, UI pending)

📖 **Integration docs**: See [INTEGRATION_COMPLETE.md](INTEGRATION_COMPLETE.md)

## 💡 Key Features Explained

### 1. 🔍 Smart Search
Search across NASA's vast imagery catalog:
```javascript
POST /api/search/images
{
  "layer": "MODIS_Terra_CorrectedReflectance_TrueColor",
  "date_start": "2024-09-01",
  "date_end": "2024-10-01",
  "bbox": { "north": 45, "south": 35, "east": -100, "west": -110 }
}
```

### 2. ✏️ Rich Annotations
Draw on images and add context:
- Points (markers)
- Polygons (areas)
- Rectangles (bounding boxes)
- Circles (radii)
- Text notes with metadata

### 3. 🔗 Image Linking
Create relationships between images:
- **before_after**: Time series comparison
- **same_location**: Different spectral bands
- **related_event**: Connected phenomena
- **comparison**: Side-by-side analysis

Navigate linked images as a graph!

### 4. 📚 Collections
Organize images into stories:
- "California Wildfires 2024"
- "Hurricane Season Track"
- "Amazon Deforestation Study"
- "Arctic Ice Melt Analysis"

### 5. 🔄 Comparison Tools
Multiple comparison modes:
- **Side-by-side**: View 2-4 images at once
- **Overlay**: Adjust opacity sliders
- **Swipe**: Dramatic before/after reveal
- **Difference**: Highlight changes

### 6. 🤖 Smart Suggestions
AI-powered discovery:
- Same location, different dates
- Linked images in graph
- Similar viewing patterns
- Related events

## 📊 Use Cases

### 🔥 Wildfire Monitoring
1. Search for fire thermal anomaly layers
2. Annotate active fire zones
3. Link daily images to track progression
4. Compare with historical data
5. Create collection: "2024 Wildfire Season"

### 🌊 Hurricane Tracking
1. Search for true color imagery over Atlantic
2. Annotate hurricane eye position daily
3. Link temporal sequence
4. Measure path and intensity
5. Compare with previous hurricanes

### 🌳 Deforestation Analysis
1. Search Amazon region: 2023 vs 2024
2. Link before/after images
3. Annotate deforested areas
4. Calculate area lost
5. Export data for reporting

### ❄️ Climate Change Monitoring
1. Search Arctic ice coverage over decades
2. Create annotations for ice extent
3. Link yearly comparisons
4. Graph shows long-term trends
5. Share findings with collection

## 🛠️ Technology Stack

### Backend (Implemented)
- **FastAPI**: Modern Python web framework
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server
- **In-memory storage**: MVP (replace with DB for production)

### Frontend (Recommended)
- **React**: UI framework
- **Leaflet**: Mapping library
- **Tailwind CSS**: Styling
- **Axios**: HTTP client
- **Redux/Zustand**: State management

### Data Sources
- **NASA GIBS**: Tile serving
- **NASA CMR**: Metadata search
- **NASA Earthdata**: Authentication (optional)

## 📁 Project Structure

```
embiggen-your-eyes/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── requirements.txt        # Python dependencies
│   ├── example_usage.py        # API usage examples
│   ├── run.sh                  # Startup script
│   ├── README.md               # Backend documentation
│   ├── ARCHITECTURE.md         # Architecture deep dive
│   └── API_QUICKSTART.md       # API reference
├── frontend/
│   └── (your implementation)
├── README.md                   # This file
└── LICENSE
```

## 🎨 Available NASA Layers

| Layer | Description | Use Case |
|-------|-------------|----------|
| `TRUE_COLOR` | Natural RGB view | General observation |
| `FALSE_COLOR` | Bands 7-2-1 | Vegetation analysis |
| `FIRES` | Thermal anomalies | Wildfire detection |
| `SNOW_COVER` | Snow and ice | Climate monitoring |
| `CHLOROPHYLL` | Ocean productivity | Marine biology |

More layers: https://worldview.earthdata.nasa.gov/

## 🎯 MVP Features Checklist

### Backend ✅ (Complete)
- [x] Search API with date/location filters
- [x] Annotation CRUD operations
- [x] Image linking system
- [x] Graph navigation
- [x] Collections management
- [x] Smart suggestions engine
- [x] Comparison preparation
- [x] Analytics endpoint

### Frontend 🚧 (To Build)
- [ ] Map viewer with Leaflet
- [ ] Search interface
- [ ] Drawing tools for annotations
- [ ] Link creation UI
- [ ] Collection manager
- [ ] Comparison view (side-by-side, overlay, swipe)
- [ ] Graph visualization
- [ ] Suggestion display

## 📚 Documentation

### Getting Started
- **[Quick Start Guide](QUICKSTART.md)** - Get running in 3 minutes
- **[Integration Complete](INTEGRATION_COMPLETE.md)** - What's new in the integrated system

### Backend Documentation
- **[Backend API Documentation](backend/README.md)** - Full API reference
- **[Architecture Guide](backend/ARCHITECTURE.md)** - System design deep dive
- **[API Quick Start](backend/API_QUICKSTART.md)** - Usage examples and patterns

### Frontend Documentation
- **[Backend Integration Guide](frontend/BACKEND_INTEGRATION.md)** - How frontend uses backend API
- **[Advanced Features TODO](frontend/TODO_ADVANCED_FEATURES.md)** - Implementation guides
- **[Data Flow Documentation](DATA_FLOW.md)** - Visual data flow diagrams

### Other
- **[Integration Summary](INTEGRATION_SUMMARY.md)** - Complete overview of integration

## 🚀 Development Workflow

### For Hackathon (48 hours)

**Hour 0-4: Setup**
- [x] Backend setup (done!)
- [ ] Frontend scaffolding
- [ ] Basic map viewer

**Hour 4-12: Core Features**
- [ ] Search implementation
- [ ] Display NASA tiles
- [ ] Basic annotations

**Hour 12-24: Smart Features**
- [ ] Image linking
- [ ] Comparison modes
- [ ] Collections

**Hour 24-36: Polish**
- [ ] Graph visualization
- [ ] Suggestions UI
- [ ] Smooth UX

**Hour 36-48: Demo Prep**
- [ ] Use case walkthrough
- [ ] Sample data
- [ ] Presentation

## 🌟 Innovation Points

What makes this unique:
1. **Graph-based navigation** - Explore images as interconnected network
2. **Smart suggestions** - AI guides you to related content
3. **Multi-modal comparison** - 4 different comparison modes
4. **Rich annotations** - Not just markers, but contextual metadata
5. **Story building** - Collections create narratives from data

## 🏆 NASA Space Apps Judging Criteria

### Impact
- **Climate monitoring**: Track environmental changes
- **Disaster response**: Real-time event analysis
- **Education**: Make satellite data accessible
- **Research**: Enable scientific discovery

### Creativity
- **Graph navigation**: Novel way to explore image relationships
- **Smart suggestions**: AI-assisted discovery
- **Comparison modes**: Multiple ways to analyze change

### Functionality
- **Works with NASA's infrastructure**: No reinventing the wheel
- **Fast & responsive**: MVP-focused backend
- **Scalable architecture**: Can grow to production

### Presentation
- **Clear use cases**: Wildfire, hurricane, deforestation tracking
- **Visual impact**: Before/after comparisons
- **Demo-ready**: Backend complete, focus on frontend polish

## 🤝 Contributing

For the NASA Space Apps Challenge:
1. Fork this repository
2. Build your frontend
3. Enhance backend features
4. Submit your solution

Post-challenge:
- Add more NASA data sources
- Implement ML-based features
- Add user authentication
- Deploy to production

## 📄 License

See LICENSE file.

## 🙏 Acknowledgments

- **NASA** for GIBS tile service and data
- **NASA Space Apps Challenge** for the opportunity
- **OpenStreetMap** for mapping inspiration
- **FastAPI** for the amazing framework

## 📞 Support

- **API Issues**: See [backend/README.md](backend/README.md)
- **API Docs**: http://localhost:8000/docs
- **Example Code**: [backend/example_usage.py](backend/example_usage.py)

---

**Built for NASA Space Apps Challenge 2025** 🚀🛰️

*"Making NASA's eyes (satellite imagery) embiggen (bigger, more accessible) for everyone!"*
=======
# Embiggen Your Eyes

**NASA Space Apps Challenge 2025**

A web-based application for exploring extremely large NASA satellite images using interactive tiled web maps.

🔗 **Challenge Details**: [Embiggen Your Eyes - NASA Space Apps Challenge](https://www.spaceappschallenge.org/2025/challenges/embiggen-your-eyes)

## Project Overview

This hackathon project provides an efficient way to view, navigate, and interact with high-resolution satellite imagery from NASA. Users can zoom, pan, add markers, and explore Earth imagery from multiple NASA data sources including GIBS (Global Imagery Browse Services).

## Features

✨ **Interactive Map Viewer**
- Load extremely large NASA satellite images as tiled web maps
- Smooth zoom and pan navigation (desktop and mobile)
- Touch gesture support for mobile devices
- Real-time coordinate and zoom level display

🗺️ **Multiple NASA Imagery Layers**
- MODIS Terra True Color (daily)
- VIIRS SNPP True Color (daily)
- MODIS Aqua True Color (daily)
- Blue Marble Next Generation (static)
- Land Surface Temperature visualization

📍 **Marker Management**
- Add custom markers to points of interest
- Quick navigation between markers with smooth fly-to transitions
- Marker list with coordinates
- Easy marker removal

🎨 **Modern UI/UX**
- Responsive design for desktop and mobile
- Collapsible control panel
- Keyboard shortcuts for productivity
- NASA-themed color scheme

🚧 **Extensible Architecture**
- Ready for overlay support
- Prepared for custom path drawing
- Built for future enhancements

## Quick Start

### Prerequisites

You need one of the following installed on your system:
- **Python 3** (recommended) - usually pre-installed on macOS/Linux
- Node.js (optional)
- PHP (optional)

### Running the Application

#### Option 1: Using the Quick Start Script (macOS/Linux)

```bash
cd frontend
./start.sh
```

#### Option 2: Using Python (macOS/Linux/Windows)

```bash
cd frontend
python3 -m http.server 8000
```

Then open your browser to: **http://localhost:8000**

#### Option 3: Using Node.js

```bash
cd frontend
npx http-server -p 8000
```

### That's it! 🎉

The application will open in your browser showing NASA's satellite imagery. You can:
- Zoom in/out with mouse wheel or pinch gestures
- Pan by clicking and dragging
- Add markers by clicking "Add Marker" button (or press 'M')
- Switch between different NASA imagery layers
- Change the date to view temporal data

## Project Structure

```
embiggen-your-eyes/
├── frontend/               # Frontend application
│   ├── index.html         # Main HTML structure
│   ├── styles.css         # Styling and responsive design
│   ├── app.js             # Application logic and NASA GIBS integration
│   ├── README.md          # Detailed frontend documentation
│   ├── package.json       # Package configuration
│   ├── start.sh           # Quick start script
│   └── .gitignore         # Git ignore patterns
├── README.md              # This file
└── LICENSE                # Project license
```

## Technology Stack

### Frontend
- **Leaflet.js** - Lightweight mapping library (chosen for NASA GIBS compatibility)
- **NASA GIBS** - Global Imagery Browse Services for satellite imagery
- **Vanilla JavaScript** - No framework dependencies
- **HTML5/CSS3** - Modern, responsive design

### Why Leaflet?

After evaluating Leaflet, OpenLayers, and OpenSeadragon, **Leaflet** was chosen because:
- ✅ Excellent NASA GIBS integration (NASA provides official examples)
- ✅ Lightweight (~42KB) and simple to use
- ✅ Perfect for tiled web maps with WMS/WMTS support
- ✅ Outstanding mobile gesture support
- ✅ Easy marker management and smooth animations
- ✅ Large community and ecosystem
- ✅ Built-in support for overlays and custom drawing (via plugins)

## NASA GIBS Integration

### What is GIBS?

NASA's Global Imagery Browse Services (GIBS) provides quick access to over 1,000 satellite imagery products, covering every part of the world. Images are provided as tiled web maps compatible with web standards.

### Example API Requests

#### MODIS Terra True Color Tile
```
https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/2025-10-04/250m/2/1/1.jpg
```

#### VIIRS True Color Tile
```
https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/VIIRS_SNPP_CorrectedReflectance_TrueColor/default/2025-10-04/250m/3/2/3.jpg
```

#### GetCapabilities (discover available layers)
```
https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/wmts.cgi?SERVICE=WMTS&REQUEST=GetCapabilities
```

### URL Format
```
https://gibs.earthdata.nasa.gov/wmts/{projection}/{quality}/{layer}/default/{date}/{resolution}/{z}/{y}/{x}.{format}
```

**Parameters:**
- `projection`: `epsg3857` (Web Mercator), `epsg4326` (Geographic), etc.
- `quality`: `best` or `std`
- `layer`: Layer identifier (e.g., `MODIS_Terra_CorrectedReflectance_TrueColor`)
- `date`: YYYY-MM-DD format
- `resolution`: `250m`, `500m`, `1km`, etc.
- `z/y/x`: Tile coordinates (zoom level, row, column)
- `format`: `jpg` or `png`

For more details, see the [frontend README](frontend/README.md).

## Usage Guide

### Basic Navigation
- **Zoom**: Mouse wheel, pinch gesture (mobile), or +/- buttons
- **Pan**: Click and drag, or swipe (mobile)
- **Add Markers**: Click "Add Marker" button or press 'M', then click on the map

### Keyboard Shortcuts
- **M**: Toggle add marker mode
- **P**: Toggle control panel

### Changing Imagery
1. Select a layer from the dropdown menu
2. Choose a date (for temporal layers)
3. Click "Update" to refresh the imagery

## Future Enhancements

### Planned Features
- [ ] Multiple layer overlays with opacity control
- [ ] Custom path drawing tools (via Leaflet.draw plugin)
- [ ] Time series animation
- [ ] Layer comparison (split screen)
- [ ] Measurement tools (distance, area)
- [ ] Image export functionality
- [ ] Marker clustering for large datasets
- [ ] Search functionality (geocoding)
- [ ] Data visualization overlays

### Backend Integration (In Progress)
- [ ] User authentication
- [ ] Save/load marker sets
- [ ] Share views via URLs
- [ ] Data analysis tools

## Resources

### NASA GIBS
- **Documentation**: https://nasa-gibs.github.io/gibs-api-docs/
- **Available Products**: https://nasa-gibs.github.io/gibs-api-docs/available-visualizations/
- **Worldview**: https://worldview.earthdata.nasa.gov/
- **GitHub Examples**: https://github.com/nasa-gibs/gibs-web-examples

### Leaflet
- **Documentation**: https://leafletjs.com/
- **Plugins**: https://leafletjs.com/plugins.html
- **Tutorials**: https://leafletjs.com/examples.html

## Browser Compatibility

- ✅ Chrome/Edge - Full support
- ✅ Firefox - Full support
- ✅ Safari - Full support
- ✅ Mobile browsers - Full support with touch gestures

## Contributing

This is a hackathon project for NASA Space Apps Challenge 2025. Feel free to fork and extend!

## Team

Built for NASA Space Apps Challenge 2025 🚀🌍

## License

See [LICENSE](LICENSE) file for details.

---

**Happy Exploring! 🛰️🗺️**
>>>>>>> Stashed changes
