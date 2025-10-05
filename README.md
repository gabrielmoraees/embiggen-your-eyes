# 🔭 Embiggen Your Eyes

**NASA Space Apps Challenge 2025** - A platform for exploring, analyzing, and annotating NASA satellite imagery across multiple celestial bodies with Google Maps-like functionality.

## 🎯 Project Overview

A comprehensive platform for exploring, analyzing, and annotating satellite imagery with interactive mapping and data management capabilities.

## 🌌 Data Structure

The application uses a hierarchical catalog system:

- **Categories**: High-level groupings (Planets, Moons, Galaxies, Nebulae, etc.)
- **Subjects**: Specific celestial objects (Earth, Mars, Moon, Mercury, etc.)
- **Datasets**: Specific map products from data providers (e.g., "VIIRS SNPP", "Mars Viking")
- **Variants**: Visualization variants of datasets (True Color, False Color, etc.)
- **Sources**: Data providers (NASA GIBS, NASA Trek, OpenPlanetaryMap, USGS, Custom)

### Available Subjects

- **Earth** (Planet): VIIRS SNPP, MODIS Terra with time-series support
- **Mars** (Planet): Viking Mosaic, OpenPlanetaryMap basemap
- **Moon** (Moon): Lunar basemap, USGS Unified Geologic Map
- **Mercury** (Planet): MESSENGER basemap
- **Custom**: User-uploaded gigapixel images

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

Comprehensive REST API for imagery management and analysis.

📖 **Full documentation**: `backend/ARCHITECTURE.md` and `backend/CUSTOM_IMAGES.md`

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

Interactive map viewer with mobile-friendly Material Design UI. Core features complete, advanced features in development.

## 🎨 Architecture

```
┌──────────────┐
│   Frontend   │  Vanilla JS + Leaflet + Material Design
│  (Browser)   │
└──────┬───────┘
       │ REST API
┌──────▼───────┐
│   Backend    │  FastAPI + Clean Architecture
│  (FastAPI)   │
└──────┬───────┘
       │
   ┌───┴────┐
   │        │
┌──▼──┐  ┌─▼────────┐
│NASA │  │  Custom  │  External tile services
│APIs │  │  Uploads │
└─────┘  └──────────┘
```

## 💡 Key Features

### Core Features
- **Multi-Subject Exploration**: Browse datasets across planets, moons, and custom imagery
- **Dataset Variants**: Multiple visualization modes (True Color, False Color, etc.)
- **Time-Series Support**: View Earth datasets across different dates
- **Interactive Annotations**: Add markers, paths, rectangles, and circles directly on the map
- **Views**: Save and restore complete map configurations
- **Collections**: Organize multiple views into thematic collections
- **iOS-Inspired UI**: Glassmorphism design with adaptive bottom sheet navigation

### Backend Capabilities
- Clean architecture with separation of concerns
- RESTful API with automatic documentation
- Custom image upload and tile processing
- In-memory storage (MVP) with database-ready structure
- Comprehensive test suite

## 🛠️ Technology Stack

**Backend**: 
- FastAPI with clean architecture (models, services, routes, data layers)
- Pydantic for data validation
- GDAL for image processing
- Comprehensive test suite

**Frontend**: 
- Vanilla JavaScript (ES6+)
- Leaflet.js for interactive mapping
- Material Design icons
- iOS 26-inspired glassmorphism UI

**Data Sources**: 
- NASA GIBS (Earth real-time imagery)
- NASA Trek (Planetary mapping)
- OpenPlanetaryMap (Mars, Moon, Mercury)
- USGS Astrogeology (Geologic maps)
- Custom user uploads

## 📁 Project Structure

```
embiggen-your-eyes/
├── backend/          # FastAPI with clean architecture
│   ├── app/          # Core application (models, services, routes)
│   ├── tests/        # Comprehensive test suite
│   └── main.py       # Entry point
│
└── frontend/         # Vanilla JS + Leaflet
```

## 📊 Use Cases

Supports environmental monitoring, planetary science research, and comparative analysis workflows.

## 🎯 Status

**Backend**: ✅ Complete with clean architecture and comprehensive API  
**Frontend**: ✅ Core features complete, advanced features in development

## 🌟 Innovation Points

1. **Unified Catalog System**: Hierarchical organization (Category → Subject → Dataset → Variant) allows intuitive exploration
2. **Flexible Data Model**: Clean separation between catalog data, user views, and annotations
3. **Mobile-First Design**: iOS-inspired interface with adaptive bottom sheet navigation
4. **Multi-Source Integration**: Seamlessly combines data from NASA GIBS, Trek, OpenPlanetaryMap, USGS, and custom uploads
5. **Interactive Annotation Tools**: Direct map interaction for adding markers, paths, and shapes with default naming and inline editing

## 🏆 NASA Space Apps Challenge 2025

### Impact
Enable climate monitoring, planetary science research, and education through accessible satellite imagery analysis.

### Creativity
Novel approach to multi-body satellite imagery exploration with intelligent navigation and custom data integration.

### Functionality
Clean architecture leveraging NASA's infrastructure with mobile-friendly interface and scalable design.

## 🤝 Contributing

Contributions welcome! Fork, enhance, and submit pull requests. Future enhancements include expanded data sources, ML capabilities, and production-ready features.

## 📄 License

See LICENSE file.

## 🙏 Acknowledgments

**NASA** for satellite imagery services, **NASA Space Apps Challenge 2025** for the opportunity, and the open source community.

## 📞 Documentation

API docs at `http://localhost:8000/docs` • Architecture guide in `backend/ARCHITECTURE.md`

---

**Built for NASA Space Apps Challenge 2025** 🚀🛰️🌍🔴🌕

*Zoom in on worlds. Zoom out on possibilities.*
