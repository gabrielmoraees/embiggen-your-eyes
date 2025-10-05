# 🔭 Embiggen Your Eyes

**NASA Space Apps Challenge 2025** - A platform for exploring, analyzing, and annotating NASA satellite imagery across multiple celestial bodies with Google Maps-like functionality.

## 🎯 Project Overview

A comprehensive platform for exploring, analyzing, and annotating satellite imagery with interactive mapping and data management capabilities.

## 🌌 Data Sources

Integrates NASA satellite imagery services and supports custom user-uploaded imagery with automatic tile processing.

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

Multi-body catalog system with advanced search and analysis capabilities, modern responsive UI.

## 🛠️ Technology Stack

**Backend**: FastAPI with clean architecture and tile processing  
**Frontend**: Vanilla JavaScript with Leaflet.js mapping  
**Data**: NASA satellite imagery services with custom upload support

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

Unified multi-body catalog with intelligent navigation, custom image integration, and flexible data management.

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
