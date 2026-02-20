# Backend API Integration Guide

This document outlines how the VayuMap frontend integrates with the backend servers and which routes are utilized.

## Backend Architecture

The VayuMap system uses two separate backend servers:

### 1. Sensor Server (Port 3001)
**File**: `sensor_server.js`

Provides real-time sensor data with dynamic AQI updates.

#### Endpoint: `/aqi`
- **Method**: GET
- **Purpose**: Retrieve all active AQI sensors and their readings
- **Response**:
  ```json
  {
    "sensors": [
      {
        "x": 0.0,
        "y": 0.0,
        "aqi": 90
      },
      {
        "x": 1.0,
        "y": 0.0,
        "aqi": 130
      },
      // ... more sensors
    ]
  }
  ```
- **Update Frequency**: AQI values drift by -2 to +2 every 3 seconds
- **Frontend Usage**: Displayed in SensorsList component and overlaid on heatmap

---

### 2. Processing Server (Port 2000)
**File**: `server.js`

Performs data processing, interpolation, and priority calculations.

#### Endpoint: `/aqi_matrix`
- **Method**: GET
- **Purpose**: Get interpolated AQI values across the entire monitoring area
- **Response**:
  ```json
  {
    "timestamp": 1708420800000,
    "sensors": [
      {
        "x": 0.0,
        "y": 0.0,
        "aqi": 90
      },
      // ... all sensors
    ],
    "matrix": [
      [90, 95, 100, ...],
      [92, 97, 102, ...],
      // ... 100x100 grid
    ]
  }
  ```
- **Key Features**:
  - Fetches sensor data from port 3001
  - Uses Inverse Distance Weighting (IDW) interpolation with power=2
  - Returns 100x100 grid of interpolated values
  - Includes original sensor positions for overlay
- **Frontend Usage**: Heatmap visualization and color coding

#### Endpoint: `/priority_zones`
- **Method**: GET
- **Purpose**: Identify high-priority zones based on AQI and population
- **Response**:
  ```json
  {
    "timestamp": 1708420800000,
    "top_5": [
      {
        "x": 45,
        "y": 67,
        "score": 0.95
      },
      {
        "x": 23,
        "y": 34,
        "score": 0.87
      },
      // ... up to 5 zones
    ]
  }
  ```
- **Calculation Method**:
  1. Fetches AQI matrix from `/aqi_matrix`
  2. Loads random population matrix from `population_data/`
  3. Normalizes both AQI and population data to 0-1 range
  4. Calculates priority score: `0.6 * AQI_normalized + 0.4 * Population_normalized`
  5. Returns top 5 zones by priority score
- **Frontend Usage**: PriorityZones component with score visualization

---

## Frontend Data Flow

```
Dashboard Component
├── useEffect on mount
│   └── Calls fetchData()
│
├── fetchData() - Parallel requests
│   ├── apiService.getAQIMatrix()     → Sensor Server (port 3001) + Processing Server (port 2000)
│   ├── apiService.getPriorityZones() → Processing Server (port 2000)
│   └── apiService.getSensorData()    → Sensor Server (port 3001)
│
├── State Updates
│   ├── aqiData → HeatmapVisualization
│   ├── priorityData → HeatmapVisualization + PriorityZones
│   └── sensorData → SensorsList
│
└── Auto-refresh every 5 seconds
```

## API Service Module

**File**: `src/services/api.js`

Provides three main functions for backend communication:

```javascript
// Get interpolated AQI matrix with sensors
apiService.getAQIMatrix()
  // Calls: GET http://localhost:2000/aqi_matrix

// Get priority zones
apiService.getPriorityZones()
  // Calls: GET http://localhost:2000/priority_zones

// Get raw sensor data
apiService.getSensorData()
  // Calls: GET http://localhost:3001/aqi
```

All requests use axios and include error handling.

## Data Visualization Mapping

### Heatmap Component
Uses the AQI matrix to create a visual representation:

1. **Grid Rendering**: Each cell in the 100x100 matrix is rendered as a pixel on canvas
2. **Color Mapping**: Cell color determined by AQI value
   - 0-50: Green (Good)
   - 51-100: Yellow (Moderate)
   - 101-150: Orange (Unhealthy for Sensitive Groups)
   - 151-200: Red (Unhealthy)
   - 201-300: Dark Red (Very Unhealthy)
   - 300+: Indigo (Hazardous)
3. **Sensor Overlay**: Blue circles at sensor positions with AQI values
4. **Priority Zones**: Purple rectangles around top 5 priority areas

### Sensors List Component
Displays all sensor readings:
- Converts AQI to status descriptors
- Color-codes by health impact
- Shows exact grid coordinates (0.0 to 1.0 normalized)

### Priority Zones Component
Shows top 5 zones:
- Grid coordinates as (x, y) indices
- Priority score as percentage
- Visual progress bar representation

## Server Dependencies

### Processing Server Requirements
- **Sensor Server**: Must have `/aqi` endpoint operational
  - Timeout: Server returns error if sensor data unavailable
- **Population Data**: Requires JSON files in `population_data/` folder
  - Randomly selects one of available population matrices
  - Used for priority calculation

### Environment
- **GRID_SIZE**: 100x100 (fixed)
- **IDW Power**: 2 (inverse distance weighting exponent)
- **Priority Weight**: 60% AQI, 40% Population

## Error Handling

The frontend includes comprehensive error handling:

### Connection Errors
- Displays user-friendly error message
- Shows instruction to start backend servers
- Provides port numbers for reference

### Data Errors
- Graceful fallbacks if API returns invalid data
- Console logs for debugging
- Continues fetching despite partial failures

### Loading States
- Shows loading indicators during data fetch
- Disables refresh button while loading
- Displays last update timestamp

## Performance Considerations

1. **Parallel Fetching**: All three API calls run simultaneously
2. **Canvas Optimization**: Uses pixelated rendering for heatmap
3. **Update Interval**: 5 seconds balances freshness and server load
4. **Memory**: Stores only current state, no historical data buffering

## CORS Configuration

Both backend servers must have CORS enabled:
```javascript
const cors = require("cors");
app.use(cors());
```

This allows frontend (typically on port 5173 during dev) to access APIs.

## Testing the Integration

1. **Start Sensor Server**:
   ```bash
   cd backend
   node sensor_server.js
   ```
   Should print: `AQI Sensor Server running on http://localhost:3001`

2. **Start Processing Server**:
   ```bash
   cd backend
   node server.js
   ```
   Should print: `Processing server running on http://localhost:2000`

3. **Test Endpoints in Browser or Curl**:
   ```bash
   # Test sensor data
   curl http://localhost:3001/aqi
   
   # Test AQI matrix
   curl http://localhost:2000/aqi_matrix
   
   # Test priority zones
   curl http://localhost:2000/priority_zones
   ```

4. **Start Frontend**:
   ```bash
   npm run dev
   ```
   Navigate to `http://localhost:5173`

## Troubleshooting

### Frontend shows "Sensor server unavailable"
- Check that `sensor_server.js` is running on port 3001
- Verify CORS is enabled
- Check browser console for network errors

### Heatmap not updating
- Verify `/aqi_matrix` endpoint returns valid 100x100 array
- Check that sensor server is providing data
- Inspect network tab for response size

### Priority zones always empty
- Ensure `population_data/` folder contains JSON files
- Verify population matrices are valid arrays
- Check server logs for interpolation errors

## Future API Enhancements

Potential additions to backend:
- Historical data endpoints
- Custom time range queries
- Alerts/threshold management
- Machine learning predictions
- Weather data integration
- Export/reporting endpoints
