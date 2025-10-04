# Quick Start Guide

**Embiggen Your Eyes - NASA Space Apps Challenge 2025**

Get up and running in 2 minutes! 🚀

## Step 1: Start the Server

Open Terminal and run:

```bash
cd /Users/psimao/Projects/nasa/embiggen-your-eyes/frontend
./start.sh
```

Or manually with Python:

```bash
cd /Users/psimao/Projects/nasa/embiggen-your-eyes/frontend
python3 -m http.server 8000
```

## Step 2: Open Your Browser

Navigate to:
```
http://localhost:8000
```

## Step 3: Explore!

You should see a map of Earth with NASA satellite imagery. Try these actions:

### 🖱️ Mouse Controls
- **Zoom In/Out**: Scroll wheel
- **Pan**: Click and drag
- **Quick Zoom**: Double-click

### 📱 Mobile/Touch Controls
- **Zoom**: Pinch gesture
- **Pan**: Swipe
- **Quick Zoom**: Double-tap

### 🎯 Adding Markers
1. Click the "Add Marker" button (or press `M`)
2. Click anywhere on the map
3. A marker will appear with coordinates

### 🗺️ Changing Imagery
1. Open the control panel (right side)
2. Select a different layer from the dropdown:
   - MODIS Terra True Color (daily satellite)
   - VIIRS SNPP True Color (high-res daily)
   - Blue Marble (beautiful Earth composite)
   - Land Surface Temperature (thermal imaging)
3. Change the date if needed
4. Click "Update"

### 🧭 Navigate Between Markers
- Click "Go" button next to any marker
- The map will smoothly fly to that location
- The marker popup will open automatically

### ⌨️ Keyboard Shortcuts
- `M` - Toggle add marker mode
- `P` - Toggle control panel

## What You'll See

### Default View
- **Center**: Equator, Prime Meridian (0°, 0°)
- **Zoom Level**: 2 (continental view)
- **Layer**: MODIS Terra True Color
- **Sample Markers**: New York, London, Tokyo (pre-loaded for demo)

### Info Display (Bottom Left)
- Current coordinates (updates as you move mouse)
- Current zoom level

### Control Panel (Right Side)
- Layer selection dropdown
- Date picker
- Add/Clear markers buttons
- List of all markers
- Toggle button to hide/show panel

## Tips for Best Experience

### Performance
- **Fast Internet**: GIBS tiles are high-quality, may take a moment to load
- **Modern Browser**: Chrome, Firefox, Safari, Edge all work great
- **Desktop or Mobile**: Fully responsive on all devices

### Imagery Notes
- **Date Availability**: Recent data may have 24-48 hour delay
- **Cloud Cover**: Visible imagery may show clouds (it's real data!)
- **Time of Day**: MODIS passes Earth twice daily
- **Coverage**: Global coverage, but polar regions may vary by layer

### Exploring Different Regions

Try these interesting locations:

**Natural Features:**
- Grand Canyon: 36.0544° N, -112.1401° W
- Amazon Rainforest: -3.4653° S, -62.2159° W
- Sahara Desert: 23.4162° N, 25.6628° E
- Great Barrier Reef: -18.2871° S, 147.6992° E

**Urban Areas:**
- New York City: 40.7128° N, -74.0060° W
- Tokyo: 35.6762° N, 139.6503° E
- Dubai: 25.2048° N, 55.2708° E
- São Paulo: -23.5505° S, -46.6333° W

**Interesting Phenomena:**
- Nile Delta: 30.8025° N, 31.0992° E
- Iceland Glaciers: 64.9631° N, -19.0208° W
- Coral Triangle: -2.5° S, 118.0° E

## Troubleshooting

### No Map Showing?
✅ **Solution**: Check browser console (F12), look for errors

### Tiles Not Loading?
✅ **Solution**: 
- Check internet connection
- Try a different date (yesterday is usually safe)
- Try a different layer

### Port Already in Use?
✅ **Solution**: 
```bash
# Use a different port
python3 -m http.server 8001
# Then visit http://localhost:8001
```

### Server Won't Start?
✅ **Solution**:
```bash
# Check if Python is installed
python3 --version

# If not installed, install from https://www.python.org/
# Or use Node.js:
npx http-server -p 8000
```

## Next Steps

### Add More Features
Check out `README.md` for information on:
- Adding overlay layers
- Implementing custom drawing tools
- Time series animations
- Exporting views

### Explore NASA Data
See `NASA_GIBS_EXAMPLES.md` for:
- Complete list of available layers
- API request examples
- Different projections
- Advanced queries

### Customize the App
Edit these files:
- `app.js` - Application logic and behavior
- `styles.css` - Visual appearance
- `index.html` - Page structure

## Common Use Cases

### 1. Track Weather Patterns
1. Select "MODIS Terra True Color"
2. Change date to track storms
3. Add markers at interesting locations
4. Compare different dates

### 2. Monitor Environmental Changes
1. Use "Land Surface Temperature" layer
2. Compare different seasons
3. Mark areas of interest
4. Track changes over time

### 3. Educational Exploration
1. Load "Blue Marble" for beautiful Earth view
2. Add markers for cities, landmarks
3. Use as teaching tool for geography
4. Demonstrate Earth's features

### 4. Research and Analysis
1. Load specific scientific layers
2. Mark study areas
3. Navigate between research sites
4. Compare different data products

## Learn More

- **NASA GIBS**: https://nasa-gibs.github.io/gibs-api-docs/
- **Leaflet Docs**: https://leafletjs.com/
- **NASA Worldview**: https://worldview.earthdata.nasa.gov/ (advanced version)
- **Space Apps**: https://www.spaceappschallenge.org/

## Need Help?

- Check the detailed `README.md` in this folder
- Review `NASA_GIBS_EXAMPLES.md` for API details
- Visit NASA GIBS documentation
- Explore NASA Worldview for inspiration

---

**Happy Exploring! 🌍🛰️**

Built for NASA Space Apps Challenge 2025

