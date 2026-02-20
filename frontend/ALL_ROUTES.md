# VayuMap - All Routes Integration Summary

## Backend Routes Overview

Complete list of all backend routes utilized by the frontend, with details on how each is used.

---

## Routes Utilization Matrix

```
┌─────────────────────────────────────────────────────────────────────┐
│                    BACKEND API ROUTES                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  PORT 3001 - SENSOR SERVER (sensor_server.js)                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ GET /aqi                                                    │   │
│  │ ├─ Returns: Live sensor data                               │   │
│  │ ├─ Data: 5 sensors with positions (x, y) and AQI values   │   │
│  │ ├─ Update: Every 3 seconds (small drift)                  │   │
│  │ ├─ Used By:                                               │   │
│  │ │  • HeatmapVisualization (sensor overlay)                │   │
│  │ │  • SensorsList (display all sensors)                    │   │
│  │ │  • Dashboard (requests via apiService.getSensorData) │   │
│  │ └─ Frequency: Every 5 seconds via Dashboard              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  PORT 2000 - PROCESSING SERVER (server.js)                         │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ GET /aqi_matrix                                             │   │
│  │ ├─ Returns: Interpolated AQI across entire area            │   │
│  │ ├─ Data: 100x100 grid + sensor positions                  │   │
│  │ ├─ Calculation: IDW interpolation with power=2            │   │
│  │ ├─ Used By:                                               │   │
│  │ │  • HeatmapVisualization (main heatmap rendering)        │   │
│  │ │  • Dashboard (requests via apiService.getAQIMatrix) │   │
│  │ └─ Frequency: Every 5 seconds via Dashboard              │   │
│  │                                                            │   │
│  │ GET /priority_zones                                        │   │
│  │ ├─ Returns: Top 5 priority zones with scores              │   │
│  │ ├─ Data: Grid positions (x, y) + priority scores         │   │
│  │ ├─ Calculation: 60% AQI + 40% Population                 │   │
│  │ ├─ Used By:                                              │   │
│  │ │  • HeatmapVisualization (priority zone overlay)        │   │
│  │ │  • PriorityZones (display top 5 zones)                │   │
│  │ │  • Dashboard (requests via apiService.getPriorityZones)│   │
│  │ └─ Frequency: Every 5 seconds via Dashboard             │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Detailed Route Information

### Route 1: GET /aqi (Port 3001)

**Server**: Sensor Server
**File**: `sensor_server.js`

```javascript
// Request
GET http://localhost:3001/aqi

// Response
{
  "sensors": [
    { "x": 0.0, "y": 0.0, "aqi": 90 },
    { "x": 1.0, "y": 0.0, "aqi": 130 },
    { "x": 0.0, "y": 1.0, "aqi": 100 },
    { "x": 1.0, "y": 1.0, "aqi": 150 },
    { "x": 0.5, "y": 0.5, "aqi": 115 }
  ]
}
```

**Frontend Integration**:
```javascript
// File: src/services/api.js
export const getSensorData = async () => {
  const response = await axios.get(`http://localhost:3001/aqi`);
  return response.data;
}

// File: src/components/Dashboard.jsx
const sensorData = await apiService.getSensorData();
setSensorData(sensorData);

// Display locations:
// 1. SensorsList - Shows all 5 sensors
// 2. HeatmapVisualization - Overlay blue circles at positions
```

**Update Frequency**: Called every 5 seconds by Dashboard

---

### Route 2: GET /aqi_matrix (Port 2000)

**Server**: Processing Server
**File**: `server.js`

```javascript
// Request
GET http://localhost:2000/aqi_matrix

// Response
{
  "timestamp": 1708420800000,
  "sensors": [
    { "x": 0.0, "y": 0.0, "aqi": 90 },
    // ... 5 sensors
  ],
  "matrix": [
    // 100x100 grid of interpolated AQI values
    [90, 95, 100, 105, ...(100 values)...],
    [92, 97, 102, 107, ...(100 values)...],
    // ... 100 rows
  ]
}
```

**Process**:
1. Fetches sensor data from `/aqi` (port 3001)
2. Performs IDW interpolation across 100x100 grid
3. Returns both original sensors and interpolated matrix

**Frontend Integration**:
```javascript
// File: src/services/api.js
export const getAQIMatrix = async () => {
  const response = await axios.get(`http://localhost:2000/aqi_matrix`);
  return response.data;
}

// File: src/components/Dashboard.jsx
const aqiData = await apiService.getAQIMatrix();
setAqiData(aqiData);

// Display locations:
// 1. HeatmapVisualization - Renders 100x100 color grid
// 2. HeatmapVisualization - Overlays sensor positions
// 3. Stats panel - Shows grid size (100x100)
```

**Update Frequency**: Called every 5 seconds by Dashboard

**Canvas Rendering**:
- Grid cells: 100x100
- Canvas size: 600x600
- Cell size: 6x6 pixels
- Color mapping based on AQI value (0-300)

---

### Route 3: GET /priority_zones (Port 2000)

**Server**: Processing Server
**File**: `server.js`

```javascript
// Request
GET http://localhost:2000/priority_zones

// Response
{
  "timestamp": 1708420800000,
  "top_5": [
    { "x": 45, "y": 67, "score": 0.95 },
    { "x": 23, "y": 34, "score": 0.87 },
    { "x": 78, "y": 12, "score": 0.82 },
    { "x": 5, "y": 89, "score": 0.76 },
    { "x": 56, "y": 45, "score": 0.71 }
  ]
}
```

**Calculation Algorithm**:
```javascript
// For each cell in 100x100 grid:
priority_score = 0.6 * (normalized_AQI) + 0.4 * (normalized_Population)

// Then sort by score and return top 5
```

**Frontend Integration**:
```javascript
// File: src/services/api.js
export const getPriorityZones = async () => {
  const response = await axios.get(`http://localhost:2000/priority_zones`);
  return response.data;
}

// File: src/components/Dashboard.jsx
const priorityData = await apiService.getPriorityZones();
setPriorityData(priorityData);

// Display locations:
// 1. HeatmapVisualization - Purple rectangles on map
// 2. PriorityZones - Card display of top 5
// 3. Stats panel - Shows count of priority zones
```

**Update Frequency**: Called every 5 seconds by Dashboard

**Zone Display**:
- Purple rectangle highlights on heatmap
- Numbered (1-5) for ranking
- Score shown as percentage (0-100%)
- Progress bar visualization

---

## Data Flow Visualization

```
Dashboard Component (Orchestrator)
│
├─ useEffect (5s interval)
│  │
│  └─ fetchData()
│     │
│     ├─ apiService.getAQIMatrix()
│     │  └─ GET http://localhost:2000/aqi_matrix
│     │     └─ Returns: { matrix: 100x100, sensors: [ {x,y,aqi} ] }
│     │
│     ├─ apiService.getPriorityZones()
│     │  └─ GET http://localhost:2000/priority_zones
│     │     └─ Returns: { top_5: [ {x,y,score} ] }
│     │
│     └─ apiService.getSensorData()
│        └─ GET http://localhost:3001/aqi
│           └─ Returns: { sensors: [ {x,y,aqi} ] }
│
└─ State Updates
   │
   ├─ setAqiData() → HeatmapVisualization
   │                 + SensorsList
   │
   ├─ setPriorityData() → HeatmapVisualization
   │                     + PriorityZones
   │
   └─ setSensorData() → SensorsList
```

---

## Component-Endpoint Mapping

| Component | Endpoint 1 | Endpoint 2 | Endpoint 3 | Usage |
|-----------|-----------|-----------|-----------|-------|
| HeatmapVisualization | `/aqi_matrix` | `/aqi_matrix` sensors | `/priority_zones` | Main visualization |
| SensorsList | `/aqi` | - | - | Display sensors |
| PriorityZones | `/priority_zones` | - | - | Display top zones |
| Dashboard | All 3 | All 3 | All 3 | Orchestration |
| Stats Panel | `/aqi_matrix` | `/aqi` | `/priority_zones` | Display metrics |

---

## Network Requests Timeline

```
Time  Event
────────────────────────────────────────────────────────────
0ms   Dashboard mounts
      └─ fetchData() starts
         ├─ Request: GET /aqi_matrix (port 2000)
         ├─ Request: GET /priority_zones (port 2000)
         ├─ Request: GET /aqi (port 3001)
         │
~100ms Component receives data
       └─ All state updates trigger re-renders
       
~150ms HeatmapVisualization renders
       └─ Canvas 600x600 drawn with 100x100 cells
       
~200ms SensorsList renders
       └─ 5 sensor cards displayed
       
~250ms PriorityZones renders
       └─ 5 zone cards displayed

5000ms setInterval triggers fetchData() again
       └─ Repeat from 0ms
```

---

## Error Handling by Route

### Route 1: /aqi

**Possible Errors:**
- CORS blocked (check backend CORS config)
- Port 3001 not running
- Sensor data unavailable

**Frontend Handling:**
```javascript
try {
  const response = await axios.get(`http://localhost:3001/aqi`);
  return response.data;
} catch (error) {
  console.error('Error fetching sensor data:', error);
  throw error;
  // Caught in Dashboard → setError()
}
```

### Route 2: /aqi_matrix

**Possible Errors:**
- Port 2000 not running
- Sensor server (3001) unreachable from processing server
- Invalid interpolation data

**Frontend Handling:**
```javascript
try {
  const response = await axios.get(`http://localhost:2000/aqi_matrix`);
  return response.data;
} catch (error) {
  console.error('Error fetching AQI matrix:', error);
  throw error;
}
```

**Server Response:**
```javascript
res.status(500).json({ error: "Sensor server unavailable" });
```

### Route 3: /priority_zones

**Possible Errors:**
- Port 2000 not running
- Population data files missing
- Invalid calculation logic

**Frontend Handling:**
```javascript
try {
  const response = await axios.get(`http://localhost:2000/priority_zones`);
  return response.data;
} catch (error) {
  console.error('Error fetching priority zones:', error);
  throw error;
}
```

**Server Response:**
```javascript
res.status(500).json({ error: "Failed to compute priority" });
```

---

## Testing Each Route Individually

### Test Sensor Server (/aqi)

```bash
# Start sensor server
cd VayuMap/backend
node sensor_server.js

# In another terminal, test endpoint
curl http://localhost:3001/aqi

# Expected output:
# {"sensors":[{"x":0,"y":0,"aqi":90},...]}
```

### Test Processing Server (/aqi_matrix)

```bash
# Ensure sensor server running on 3001
# Then start processing server
node server.js

# Test AQI matrix endpoint
curl http://localhost:2000/aqi_matrix

# Expected output:
# {"timestamp":..., "sensors":[...], "matrix":[[...],[...],...]}
```

### Test Priority Zones

```bash
# Test priority zones endpoint
curl http://localhost:2000/priority_zones

# Expected output:
# {"timestamp":..., "top_5":[{"x":45,"y":67,"score":0.95},...]}
```

---

## Performance Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| Data Fetch Interval | 5000ms | Configurable |
| Parallel API Calls | 3 | All called simultaneously |
| Expected Response Time | 50-200ms | Depends on server load |
| Canvas Render Time | 20-50ms | Depends on browser |
| Total Update Cycle | 100-300ms | Fetch + Render |
| Sensor Update Frequency | 3000ms | Server-side |
| Grid Size | 100x100 | 10,000 cells |

---

## Complete Route Reference

```
SENSOR SERVER (Port 3001)
├─ GET /aqi
│  ├─ Response: 200 OK
│  │  └─ Data: {sensors: [{x, y, aqi},...]}
│  └─ Error: 500 Internal Server Error
│

PROCESSING SERVER (Port 2000)
├─ GET /aqi_matrix
│  ├─ Response: 200 OK
│  │  └─ Data: {timestamp, sensors[], matrix[][]}
│  └─ Error: 500 - "Sensor server unavailable"
│
└─ GET /priority_zones
   ├─ Response: 200 OK
   │  └─ Data: {timestamp, top_5: [{x, y, score},...]}
   └─ Error: 500 - "Failed to compute priority"
```

---

## Summary

The VayuMap frontend successfully integrates with all three backend routes:

✅ **GET /aqi** (Port 3001)
- Provides real-time sensor data
- Updated every 3 seconds on server
- Used for sensor display and heatmap overlay

✅ **GET /aqi_matrix** (Port 2000)
- Provides interpolated AQI grid (100x100)
- Used for main heatmap visualization
- Combines sensor data with IDW interpolation

✅ **GET /priority_zones** (Port 2000)
- Identifies critical intervention areas
- Combines AQI and population data
- Shows top 5 prioritized zones

All routes are called by the Dashboard component every 5 seconds via the apiService module, ensuring real-time updates for the entire application.
