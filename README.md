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

### Backend (MVP - Ready to Use)

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

### Frontend (To Be Built)

```bash
cd frontend

# Recommended stack:
# - React/Vue/Svelte
# - Leaflet or OpenLayers
# - Tailwind CSS
# - Axios for API calls

# Example with React:
npx create-react-app .
npm install leaflet react-leaflet axios
```

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

- **[Backend API Documentation](backend/README.md)** - Full API reference
- **[Architecture Guide](backend/ARCHITECTURE.md)** - System design deep dive
- **[API Quick Start](backend/API_QUICKSTART.md)** - Usage examples and patterns

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
