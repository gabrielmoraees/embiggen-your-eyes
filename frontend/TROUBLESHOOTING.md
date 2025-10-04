# Troubleshooting Guide

Quick fixes for common issues with Embiggen Your Eyes.

## 🔍 Issue: Nothing Loads / Gray Screen

### Quick Fix #1: Try Blue Marble Layer
1. Open the control panel (right side)
2. Change "Layer Selection" to **"Blue Marble (Static)"**
3. This layer is static and always available

### Quick Fix #2: Use Older Date
1. The default date is already set to 3 days ago
2. Try changing to 5-7 days ago in the date picker
3. Click "Update" button
4. NASA GIBS has 24-48 hour delay for recent imagery

### Quick Fix #3: Check Browser Console
1. Press **F12** to open Developer Tools
2. Go to **Console** tab
3. Look for error messages
4. You should see: "✓ Tiles loading successfully"

## 🧪 Test NASA GIBS Connection

Run the test script:
```bash
cd /Users/psimao/Projects/nasa/embiggen-your-eyes/front-end
./test-gibs.sh
```

This will test if NASA GIBS is accessible from your network.

## 🐛 Common Issues & Solutions

### Issue: "Tile loading error" in console

**Possible Causes:**
1. **Date too recent** - GIBS has 24-48 hour delay
2. **Layer has no data for that date** - Some layers update less frequently
3. **Network/firewall blocking** - Corporate networks may block external APIs

**Solutions:**
- Switch to "Blue Marble" layer (always works)
- Use date from 3-5 days ago
- Try different layer (VIIRS vs MODIS)
- Check internet connection

### Issue: Map shows but tiles are gray

**Cause:** Selected date has no imagery available

**Solutions:**
1. Click "Blue Marble" in layer dropdown
2. Change date to last week
3. Try different layer

### Issue: Server won't start

**Error:** "Port 8000 already in use"

**Solution:**
```bash
# Use different port
python3 -m http.server 8001
# Then visit http://localhost:8001
```

**Error:** "python3: command not found"

**Solution:**
```bash
# Try python instead
python -m http.server 8000

# Or use Node.js
npx http-server -p 8000

# Or use PHP
php -S localhost:8000
```

### Issue: Leaflet not loading

**Symptoms:** Blank page, no map controls

**Solutions:**
1. Check internet connection (Leaflet loads from CDN)
2. Open browser console (F12) for errors
3. Try different browser
4. Clear browser cache

### Issue: Tiles load slowly

**Causes:**
- First load downloads tiles from NASA
- High-resolution imagery is large
- Network speed

**Solutions:**
- Be patient, tiles cache after first load
- Zoom out for faster initial load
- Use lower resolution layer if available

## 📋 Checklist

Before reporting issues, check:

- [ ] Server is running (`./start.sh` or `python3 -m http.server 8000`)
- [ ] Browser shows http://localhost:8000
- [ ] Browser console (F12) open to see messages
- [ ] Tried "Blue Marble" layer
- [ ] Tried date from 3-5 days ago
- [ ] Internet connection working
- [ ] No firewall blocking NASA domains

## 🔧 Advanced Debugging

### Check Specific Tile URL

Open this URL in your browser (should download an image):
```
https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/BlueMarble_NextGeneration/default/2004-08-01/500m/2/1/1.jpg
```

If this **doesn't work**: Your network is blocking NASA GIBS
If this **works**: The issue is with date/layer selection

### Check Current Date Being Used

Open browser console (F12) and type:
```javascript
console.log(AppState.currentDate);
console.log(AppState.currentLayer);
```

This shows what date and layer the app is trying to load.

### Test Different Layers Manually

Try these URLs directly in your browser:

**MODIS Terra (3 days ago):**
```
https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/2024-10-01/250m/2/1/1.jpg
```

**Blue Marble (always works):**
```
https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/BlueMarble_NextGeneration/default/2004-08-01/500m/2/1/1.jpg
```

### Check Network Tab

1. Open Developer Tools (F12)
2. Go to **Network** tab
3. Refresh page
4. Filter by "img" or "jpg"
5. See which tile requests are failing
6. Click failed request to see error details

## 🌍 Layer-Specific Issues

### MODIS Terra/Aqua True Color
- **Update Frequency**: Twice daily
- **Latency**: 3-4 hours
- **Safe Date**: 2-3 days ago
- **Common Issue**: Cloud cover (real data)

### VIIRS SNPP True Color
- **Update Frequency**: Daily
- **Latency**: 24-48 hours
- **Safe Date**: 3-4 days ago
- **Common Issue**: Higher resolution = more tiles = slower load

### Blue Marble
- **Update Frequency**: Static (2004 composite)
- **Date**: Always use 2004-08-01
- **Should**: Always work
- **If fails**: Network/firewall issue

### Land Surface Temperature
- **Update Frequency**: Daily
- **Latency**: 24-48 hours
- **Safe Date**: 3-4 days ago
- **Format**: PNG (supports transparency)

## 🔗 Useful Links

- **NASA GIBS Status**: https://status.earthdata.nasa.gov/
- **NASA Worldview**: https://worldview.earthdata.nasa.gov/ (to test layers)
- **GIBS Documentation**: https://nasa-gibs.github.io/gibs-api-docs/
- **Available Layers**: https://nasa-gibs.github.io/gibs-api-docs/available-visualizations/

## 💡 Pro Tips

1. **Blue Marble = Emergency Fallback**
   - Always works
   - No date dependency
   - Great for testing if app works at all

2. **Date = 3-5 Days Ago**
   - GIBS processing delay
   - Recent dates often don't have data yet
   - Older dates are safer

3. **Browser Console = Your Friend**
   - Press F12
   - Look for green checkmarks or red errors
   - App logs helpful messages

4. **Test Script**
   ```bash
   ./test-gibs.sh
   ```
   - Tests NASA connection
   - Verifies which layers work
   - Shows exact URLs being used

## 🆘 Still Not Working?

If you've tried everything above:

1. **Verify basic HTML/CSS loads**
   - You should see the control panel on right
   - Buttons and dropdowns should be visible
   - Even without tiles, UI should appear

2. **Test with different browser**
   - Chrome/Edge
   - Firefox
   - Safari

3. **Check NASA GIBS status**
   - Visit: https://status.earthdata.nasa.gov/
   - Verify services are operational

4. **Test on different network**
   - Mobile hotspot
   - Different WiFi
   - Corporate firewalls often block external APIs

5. **Try NASA Worldview directly**
   - Visit: https://worldview.earthdata.nasa.gov/
   - If this doesn't work, GIBS is down or blocked
   - If this works, issue is with your app code

## 📝 Reporting Issues

If you need to report a bug, include:

1. **Browser & Version**: (e.g., Chrome 120)
2. **Operating System**: (e.g., macOS 14)
3. **Console Errors**: (F12 → Console tab)
4. **Layer Tried**: (e.g., MODIS Terra)
5. **Date Tried**: (e.g., 2024-10-01)
6. **Network Tab**: (Any failed requests)
7. **Test Script Result**: (Output of `./test-gibs.sh`)

---

**Most Common Fix**: Switch to "Blue Marble" layer and it should work immediately! 🌍✨

