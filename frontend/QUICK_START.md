# VayuMap Frontend - Quick Start Guide

## What Was Created

A fully functional React frontend with the following components:

### Components ✅
- **Dashboard** - Main container managing all data and layout
- **HeatmapVisualization** - Canvas-based AQI visualization with color-coded grid
- **SensorsList** - Real-time sensor readings with status indicators
- **PriorityZones** - Top 5 priority areas with scoring

### Services ✅
- **api.js** - Backend integration with all available routes

### Features ✅
- Real-time data fetching (every 5 seconds)
- All backend routes integrated:
  - `/aqi` (Sensor Server) - Sensor data
  - `/aqi_matrix` (Processing Server) - Heatmap data
  - `/priority_zones` (Processing Server) - Priority zone calculations
- Responsive design with Tailwind CSS
- Error handling and loading states
- Auto-refresh with manual refresh button

## Getting Started

### Step 1: Start Backend Servers

Open two terminal windows in the backend folder:

**Terminal 1 - Sensor Server (Port 3001)**
```bash
cd C:\Users\meism\Desktop\ClimateHackathon\VayuMap\backend
node sensor_server.js
```
You should see: `AQI Sensor Server running on http://localhost:3001`

**Terminal 2 - Processing Server (Port 2000)**
```bash
cd C:\Users\meism\Desktop\ClimateHackathon\VayuMap\backend
node server.js
```
You should see: `Processing server running on http://localhost:2000`

### Step 2: Start Frontend Development Server

Open a new terminal in the frontend folder:

```bash
cd C:\Users\meism\Desktop\ClimateHackathon\VayuMap\frontend
npm run dev
```

You should see something like:
```
  VITE v7.3.1  ready in 234 ms

  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

### Step 3: Open in Browser

Navigate to: **http://localhost:5173**

You should see the VayuMap dashboard with:
- Interactive heatmap on the left
- Sensor list on the right
- Priority zones information
- Real-time updates

## What Each Backend Route Does

| Route | Server | Purpose | Frontend Component |
|-------|--------|---------|-------------------|
| GET `/aqi` | 3001 | Returns sensor positions and AQI values | HeatmapVisualization, SensorsList |
| GET `/aqi_matrix` | 2000 | Returns interpolated AQI values for 100x100 grid | HeatmapVisualization |
| GET `/priority_zones` | 2000 | Returns top 5 priority zones with scores | HeatmapVisualization, PriorityZones |

## Dashboard Sections

### Left Side - Heatmap Visualization
- **Color Grid**: Each pixel represents an AQI value
- **Blue Circles**: Sensor locations with AQI values
- **Purple Rectangles**: Top 5 priority zones
- **Legend**: AQI color scale

### Right Side - Info Panels
1. **Sensors Panel**
   - Shows all 5 sensors
   - Displays coordinates and AQI values
   - Color-coded health status

2. **Priority Zones Panel**
   - Top 5 zones ranked by priority
   - Priority score (0-100%)
   - Grid coordinates

3. **Stats Panel**
   - Grid size (100x100)
   - Number of active sensors
   - Number of priority zones

4. **Refresh Button**
   - Manual data refresh
   - Shows loading state while fetching

## Folder Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Dashboard.jsx           # Main container
│   │   ├── HeatmapVisualization.jsx # Canvas heatmap
│   │   ├── SensorsList.jsx         # Sensor display
│   │   └── PriorityZones.jsx       # Priority zones display
│   ├── services/
│   │   └── api.js                  # Backend API calls
│   ├── App.jsx                     # Main app component
│   ├── App.css                     # Custom styles
│   ├── index.css                   # Global styles
│   └── main.jsx                    # Entry point
├── package.json                    # Dependencies
├── tailwind.config.js              # Tailwind configuration
├── vite.config.js                  # Vite configuration
├── FRONTEND_README.md              # Detailed documentation
├── API_INTEGRATION.md              # Backend integration details
└── QUICK_START.md                  # This file
```

## Common Tasks

### Change Backend URLs
Edit `src/services/api.js`:
```javascript
const API_BASE_URL = 'http://localhost:2000';
const SENSOR_API_URL = 'http://localhost:3001';
```

### Change Refresh Interval
Edit `src/components/Dashboard.jsx` (find the `useEffect`):
```javascript
const interval = setInterval(fetchData, 5000); // Change 5000 for different interval (milliseconds)
```

### Adjust Heatmap Size
Edit `src/components/HeatmapVisualization.jsx`:
```javascript
<canvas
  ref={canvasRef}
  width={600}  // Change canvas width
  height={600} // Change canvas height
  className="border-2 border-gray-300 rounded"
/>
```

## Troubleshooting

### Issue: "Failed to fetch data" / Network Error

**Solution**: Ensure both backend servers are running
```bash
# Check if ports are in use
netstat -ano | findstr :2000
netstat -ano | findstr :3001

# Kill process on port if needed
taskkill /PID <PID> /F
```

### Issue: Heatmap not showing

**Solution**: 
1. Check browser console (F12) for errors
2. Verify sensor data is coming through (check Network tab)
3. Clear browser cache (Ctrl+Shift+Delete)
4. Restart frontend dev server

### Issue: Sensors showing but no heatmap

**Solution**:
1. Verify `/aqi_matrix` endpoint returns valid data
2. Check that it's a 100x100 array
3. Ensure processing server is running

### Issue: No priority zones showing

**Solution**:
1. Check that `population_data/` folder has JSON files
2. Verify priority API endpoint works: `http://localhost:2000/priority_zones`
3. Check backend server logs for errors

## Performance Tips

- Auto-refresh every 5 seconds is balanced for performance
- Canvas rendering is optimized for speed
- State updates are minimal
- All API calls run in parallel

## Next Steps

1. ✅ Verify all three API endpoints work
2. ✅ Check data is displaying correctly
3. ✅ Monitor sensors updating in real-time
4. Consider adding:
   - Historical data views
   - Alerts for high AQI
   - Data export functionality
   - Time-based filtering

## For More Information

- See **FRONTEND_README.md** for detailed component documentation
- See **API_INTEGRATION.md** for backend integration details
- Check backend files for route information

## Quick Reference - Running Everything

```bash
# Terminal 1 - Sensor Server
cd VayuMap\backend
node sensor_server.js

# Terminal 2 - Processing Server
cd VayuMap\backend
node server.js

# Terminal 3 - Frontend
cd VayuMap\frontend
npm run dev

# Open browser
http://localhost:5173
```

Enjoy your VayuMap dashboard! 🗺️✨
