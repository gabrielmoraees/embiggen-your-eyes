# 🔭 Embiggen Your Eyes

**NASA Space Apps Challenge 2025** - A platform for exploring, analyzing, and annotating NASA satellite imagery across multiple celestial bodies with Google Maps-like functionality.

## 🎯 Project Overview

This platform enables users to:
- 🌍 **Explore** Earth, Mars, and Moon imagery
- 🔍 **Search** NASA satellite imagery by celestial body, date, and layer type
- 🗺️ **Visualize** massive images with smooth pan and zoom
- ✏️ **Annotate** images with points, polygons, and notes
- 🔗 **Link** related images to create narrative connections
- 📊 **Compare** images side-by-side, overlay, or swipe modes
- 🤖 **Discover** related content through smart suggestions
- 📚 **Organize** images into collections

## 🌌 Supported Celestial Bodies

### 🌍 Earth (NASA GIBS)
- VIIRS SNPP True Color & False Color
- MODIS Terra True Color & False Color
- Time-series data (daily imagery)
- Up to zoom level 9

### 🔴 Mars (NASA Trek)
- Viking Orbiter Colorized Mosaic (232m/px)
- Static high-resolution imagery
- Up to zoom level 12

### 🌕 Moon (NASA Trek)
- LRO Wide Angle Camera Mosaic (100m/px)
- Clementine UV-VIS 750nm Mosaic (118m/px)
- Static high-resolution imagery
- Up to zoom level 10

## 🚀 Quick Start

### Backend (FastAPI)

```bash
cd backend

# Create virtual environment (first time only)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn main:app --host 0.0.0.0 --port 8000

# View API docs
open http://localhost:8000/docs
```

**API Features:**
- Search imagery across Earth, Mars, and Moon
- Create/manage annotations
- Link images together
- Build collections
- Get smart suggestions
- Graph navigation

📖 **Full API documentation**: See [backend/README.md](backend/README.md)

### Frontend (Vanilla JS + Leaflet)

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
- ✅ Celestial body selector (Earth, Mars, Moon)
- ✅ Dynamic layer loading based on celestial body
- ✅ Image search via backend
- ✅ Persistent annotations (saved to backend)
- ✅ Interactive map with Leaflet
- ✅ Date picker (for Earth time-series)
- ✅ Marker tools with annotations
- ✅ Mobile-friendly Material Design UI
- ✅ Floating control panel
- 🚧 Collections (backend ready, UI pending)
- 🚧 Image linking (backend ready, UI pending)
- 🚧 Smart suggestions (backend ready, UI pending)

## 🎨 Architecture

```
┌──────────────┐
│   Frontend   │  ← Vanilla JS + Leaflet + Material Design
│  (Browser)   │     - Celestial body selection
│              │     - Dynamic layer loading
└──────┬───────┘     - Annotations & markers
       │ REST API
┌──────▼───────┐
│   Backend    │  ✅ FastAPI
│  (FastAPI)   │     - Multi-body support
│              │     - Annotations & links
└──────┬───────┘     - Collections & suggestions
   ┌───┴────┐
   │        │
┌──▼──┐  ┌─▼────────┐
│NASA │  │  NASA    │
│GIBS │  │   Trek   │  ← NASA provides: Tiles & Metadata
│Earth│  │Mars/Moon │
└─────┘  └──────────┘
```

## 💡 Key Features

### 1. 🌍 Multi-Celestial Body Support
Switch between Earth, Mars, and Moon with automatic layer updates:
- **Earth**: Time-series data with date picker
- **Mars/Moon**: Static high-resolution mosaics

### 2. 🔍 Smart Search
Search across NASA's vast imagery catalog:
```javascript
POST /api/search/images
{
  "celestial_body": "earth",
  "layer": "MODIS_Terra_CorrectedReflectance_TrueColor",
  "date_start": "2024-09-01",
  "date_end": "2024-10-01"
}
```

### 3. ✏️ Rich Annotations
Draw on images and add context:
- Points (markers)
- Polygons (areas)
- Rectangles (bounding boxes)
- Circles (radii)
- Text notes with metadata

### 4. 🔗 Image Linking
Create relationships between images:
- **before_after**: Time series comparison
- **same_location**: Different spectral bands
- **related_event**: Connected phenomena
- **comparison**: Cross-body comparisons

### 5. 📚 Collections
Organize images into stories:
- "California Wildfires 2024"
- "Mars Valles Marineris Study"
- "Lunar South Pole Analysis"

### 6. 🎨 Modern UI/UX
- Material Design with neutral colors
- Mobile-first responsive design
- Floating control panel
- Quick action buttons
- Touch gesture support

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server
- **In-memory storage**: MVP (replace with DB for production)

### Frontend
- **Leaflet.js**: Lightweight mapping library
- **Vanilla JavaScript**: No framework dependencies
- **Material Design**: Modern, clean UI
- **Inter Font**: Clean typography

### Data Sources
- **NASA GIBS**: Earth imagery tiles
- **NASA Trek**: Mars and Moon imagery tiles
- **NASA CMR**: Metadata search (future)

## 📁 Project Structure

```
embiggen-your-eyes/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── requirements.txt        # Python dependencies
│   ├── venv/                   # Virtual environment
│   ├── example_usage.py        # API usage examples
│   ├── README.md               # Backend documentation
│   ├── ARCHITECTURE.md         # Architecture deep dive
│   └── API_QUICKSTART.md       # API reference
├── frontend/
│   ├── index.html              # Main HTML structure
│   ├── styles.css              # Material Design styles
│   ├── app.js                  # Application logic
│   ├── start.sh                # Quick start script
│   └── package.json            # Package metadata
├── README.md                   # This file
└── LICENSE
```

## 📊 Use Cases

### 🔥 Wildfire Monitoring (Earth)
1. Search for fire thermal anomaly layers
2. Annotate active fire zones
3. Link daily images to track progression
4. Compare with historical data

### 🔴 Mars Geological Survey
1. Explore Mars Viking imagery
2. Annotate geological features
3. Link regions of interest
4. Create collection: "Mars Valley Systems"

### 🌕 Lunar Landing Site Analysis
1. Browse LRO high-resolution imagery
2. Annotate potential landing sites
3. Measure crater dimensions
4. Compare with Clementine data

### 🌊 Hurricane Tracking (Earth)
1. Search for true color imagery over Atlantic
2. Annotate hurricane eye position daily
3. Link temporal sequence
4. Measure path and intensity

## 🎯 MVP Features Checklist

### Backend ✅ (Complete)
- [x] Multi-celestial body support
- [x] Search API with date/location filters
- [x] Annotation CRUD operations
- [x] Image linking system
- [x] Graph navigation
- [x] Collections management
- [x] Smart suggestions engine
- [x] Comparison preparation
- [x] Analytics endpoint
- [x] Layer metadata endpoint

### Frontend ✅ (Complete)
- [x] Map viewer with Leaflet
- [x] Celestial body selector
- [x] Dynamic layer loading
- [x] Search interface
- [x] Annotation markers
- [x] Mobile-friendly UI
- [x] Material Design styling
- [x] Touch gesture support

### Frontend 🚧 (To Build)
- [ ] Advanced drawing tools (polygons, circles)
- [ ] Link creation UI
- [ ] Collection manager
- [ ] Comparison view (side-by-side, overlay, swipe)
- [ ] Graph visualization
- [ ] Suggestion display

## 🌟 Innovation Points

What makes this unique:
1. **Multi-celestial body support** - Explore Earth, Mars, and Moon seamlessly
2. **Graph-based navigation** - Explore images as interconnected network
3. **Smart suggestions** - AI guides you to related content
4. **Material Design** - Clean, modern, mobile-first UI
5. **Rich annotations** - Not just markers, but contextual metadata
6. **Story building** - Collections create narratives from data

## 🏆 NASA Space Apps Judging Criteria

### Impact
- **Climate monitoring**: Track environmental changes on Earth
- **Planetary science**: Enable Mars and Moon exploration
- **Education**: Make satellite data accessible
- **Research**: Enable scientific discovery across celestial bodies

### Creativity
- **Multi-body exploration**: Novel integration of Earth, Mars, and Moon data
- **Graph navigation**: Unique way to explore image relationships
- **Smart suggestions**: AI-assisted discovery
- **Comparison modes**: Multiple ways to analyze change

### Functionality
- **Works with NASA's infrastructure**: No reinventing the wheel
- **Fast & responsive**: MVP-focused backend
- **Scalable architecture**: Can grow to production
- **Mobile-friendly**: Works on any device

## 🤝 Contributing

For the NASA Space Apps Challenge:
1. Fork this repository
2. Enhance features
3. Submit your solution

Post-challenge:
- Add more NASA data sources
- Implement ML-based features
- Add user authentication
- Deploy to production

## 📄 License

See LICENSE file.

## 🙏 Acknowledgments

- **NASA** for GIBS and Trek tile services
- **NASA Space Apps Challenge** for the opportunity
- **FastAPI** for the amazing framework
- **Leaflet.js** for the mapping library

## 📞 Support

- **API Issues**: See [backend/README.md](backend/README.md)
- **API Docs**: http://localhost:8000/docs
- **Example Code**: [backend/example_usage.py](backend/example_usage.py)

---

**Built for NASA Space Apps Challenge 2025** 🚀🛰️🌍🔴🌕

*"Making NASA's eyes (satellite imagery) embiggen (bigger, more accessible) for everyone across multiple worlds!"*
