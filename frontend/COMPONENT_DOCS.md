# VayuMap Frontend - Complete Component Documentation

## Overview

This document provides comprehensive documentation for all frontend components, services, and their integration with the backend API.

---

## Service Layer

### `src/services/api.js`

Handles all communication with backend servers.

#### Functions

**`getAQIMatrix()`**
- **Purpose**: Fetch interpolated AQI values across the monitoring area
- **Endpoint**: `GET http://localhost:2000/aqi_matrix`
- **Returns**: 
  ```javascript
  {
    timestamp: number,
    sensors: Array<{x: number, y: number, aqi: number}>,
    matrix: Array<Array<number>>  // 100x100 grid
  }
  ```
- **Usage**: Feed to HeatmapVisualization component

**`getPriorityZones()`**
- **Purpose**: Get top 5 priority zones for intervention
- **Endpoint**: `GET http://localhost:2000/priority_zones`
- **Returns**:
  ```javascript
  {
    timestamp: number,
    top_5: Array<{x: number, y: number, score: number}>
  }
  ```
- **Score Calculation**: 60% AQI weight + 40% Population weight
- **Usage**: Feed to PriorityZones component and overlay on heatmap

**`getSensorData()`**
- **Purpose**: Fetch real-time sensor readings
- **Endpoint**: `GET http://localhost:3001/aqi`
- **Returns**:
  ```javascript
  {
    sensors: Array<{x: number, y: number, aqi: number}>
  }
  ```
- **Update Frequency**: Sensor values drift every 3 seconds
- **Usage**: Display in SensorsList and overlay on heatmap

---

## Component Layer

### `src/components/Dashboard.jsx`

**Main orchestrator component responsible for:**
- Data fetching and state management
- Layout and responsive design
- Auto-refresh functionality
- Error handling

#### Props
None - This is the root component

#### State Variables
```javascript
aqiData: object          // Heatmap matrix and sensor positions
priorityData: object     // Priority zones with scores
sensorData: object       // Raw sensor readings
loading: boolean         // Loading state
error: string            // Error messages if any
lastUpdate: string       // Last update timestamp
```

#### Features
- **Parallel API Calls**: All three endpoints called simultaneously for performance
- **Auto-refresh**: Updates every 5 seconds via `setInterval`
- **Cleanup**: Interval cleared on component unmount
- **Error Boundary**: User-friendly error display with instructions
- **Stats**: Shows grid size and active sensor count

#### Component Tree
```
Dashboard
├── ErrorBoundary (conditional)
├── HeatmapVisualization
│   ├── Canvas (600x600)
│   └── Color Legend
├── SensorsList
│   └── Sensor Cards (map)
├── PriorityZones
│   └── Zone Cards (map)
├── Stats Panel
│   ├── Grid Size
│   ├── Active Sensors
│   └── Priority Zones Count
└── Refresh Button
```

---

### `src/components/HeatmapVisualization.jsx`

**Canvas-based visualization of AQI heatmap with overlays**

#### Props
```javascript
{
  aqiMatrix: Array<Array<number>>,        // 100x100 grid of AQI values
  sensors: Array<{x, y, aqi}>,            // Sensor positions and values
  priorityZones: Array<{x, y, score}>     // Top 5 priority zones
}
```

#### Rendering Pipeline

1. **Clear Canvas**: White background

2. **Draw Heatmap**: 
   - Iterate through 100x100 grid
   - Map AQI value to color
   - Draw colored square for each cell

3. **Draw Sensors**:
   - Blue circle at normalized position (x, y)
   - White AQI value label inside
   - Radius: 8px

4. **Draw Priority Zones**:
   - Purple rectangle outline
   - Numbered label above zone
   - Indicates top priority areas

#### Color Mapping Function

```javascript
getColor(aqi_value) {
  0-50:     #00E400  (Green)      Good
  51-100:   #FFE400  (Yellow)     Moderate
  101-150:  #FFA500  (Orange)     Unhealthy for SG
  151-200:  #FF0000  (Red)        Unhealthy
  201-300:  #8B0000  (Dark Red)   Very Unhealthy
  300+:     #4B0082  (Indigo)     Hazardous
}
```

#### Canvas Configuration
- **Dimensions**: 600x600px (configurable)
- **Cell Size**: 600 / 100 = 6px per cell
- **Image Rendering**: Pixelated (no anti-aliasing)

#### Legend Display
- Color-coded status boxes
- AQI ranges for each color
- 2 rows x 3 columns layout

---

### `src/components/SensorsList.jsx`

**Displays all active sensors with real-time AQI readings**

#### Props
```javascript
{
  sensors: Array<{x, y, aqi}>,  // Sensor array from API
  loading: boolean              // Loading state
}
```

#### Features
- **Status Indicators**: Color-coded health status
- **Coordinates**: Shows normalized position (0.0 to 1.0)
- **Real-time Updates**: Reflects latest sensor values
- **Responsive Design**: Stacks on mobile

#### Status Categories

| AQI Range | Status | Background | Border Color |
|-----------|--------|-----------|------------|
| 0-50 | Good | `bg-green-100` | `border-green-300` |
| 51-100 | Moderate | `bg-yellow-100` | `border-yellow-300` |
| 101-150 | Unhealthy for SG | `bg-orange-100` | `border-orange-300` |
| 151-200 | Unhealthy | `bg-red-100` | `border-red-300` |
| 201-300 | Very Unhealthy | `bg-purple-100` | `border-purple-300` |
| 300+ | Hazardous | `bg-indigo-100` | `border-indigo-300` |

#### Card Layout
```
┌─────────────────────────────┐
│ Sensor 1                    │
│ Location: (0.00, 0.50)  45 │
│                            │
│          ┌─────────────┐   │
│          │  AQI Value  │   │
│          │   Status    │   │
│          └─────────────┘   │
└─────────────────────────────┘
```

#### Error States
- **No Sensors**: Shows "No sensors available" message
- **Loading**: Shows "Loading sensors..." text
- **Graceful Fallback**: Empty array renders nothing

---

### `src/components/PriorityZones.jsx`

**Displays ranked priority zones for intervention**

#### Props
```javascript
{
  zones: Array<{x, y, score}>,  // Priority zone data
  loading: boolean              // Loading state
}
```

#### Calculation Method
- **Score Range**: 0.0 to 1.0 (scaled to 0-100%)
- **Formula**: 0.6 × (normalized AQI) + 0.4 × (normalized Population)
- **Purpose**: Identify areas needing most urgent intervention

#### Color Coding by Priority

| Score Range | Background | Interpretation |
|------------|-----------|-----------------|
| 80-100% | `bg-red-100` | Critical Priority |
| 60-79% | `bg-orange-100` | High Priority |
| 40-59% | `bg-yellow-100` | Medium Priority |
| 0-39% | `bg-green-100` | Low Priority |

#### Zone Card Layout
```
┌──────────────────────────────┐
│ Zone 1                       │
│ Grid Position: (45, 67)      │
│                              │
│ Priority Score: 85.3%        │
│ ████████████████░░░░ 85.3%   │
└──────────────────────────────┘
```

#### Features
- **Progress Bars**: Visual representation of priority score
- **Grid Coordinates**: Exact position in 100x100 grid
- **Ranked List**: Top 5 zones ordered by score
- **Percentages**: Score displayed as 0-100%

#### Data Interpretation
- **High Scores (>80%)**: Combine high AQI AND high population
- **Medium Scores (40-80%)**: Significant concern for one factor
- **Low Scores (<40%)**: Lower priority for intervention

---

## Main App Component

### `src/App.jsx`

Simple entry point that renders the Dashboard component.

```jsx
import Dashboard from './components/Dashboard';

function App() {
  return <Dashboard />;
}

export default App;
```

#### Purpose
- Minimal wrapper for the application
- Allows easy addition of global providers (Auth, Theme, etc.)
- Routes can be added here later

---

## Styling Architecture

### `src/App.css`

Custom application styles including:

**Features:**
- Fade-in animations
- Smooth scrolling
- Canvas pixelation for heatmap
- Responsive breakpoints

**Animations:**
```css
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
```

### `src/index.css`

Global styles with Tailwind CSS integration:
```css
@import "tailwindcss";
```

All Tailwind utilities available throughout application.

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────┐
│                   Dashboard                         │
│                                                     │
│  ┌────────────────────────────────────────────┐    │
│  │ useEffect (mount)                          │    │
│  │  → fetchData()                             │    │
│  │    ├─ getAQIMatrix()                       │    │
│  │    ├─ getPriorityZones()                   │    │
│  │    └─ getSensorData()                      │    │
│  └────────────────────────────────────────────┘    │
│           ↓ State Updates ↓                        │
│  ┌──────────────┬──────────────┬─────────────┐    │
│  │ Heatmap      │ SensorsList  │ PriorityZ.  │    │
│  │              │              │             │    │
│  │ Canvas (600) │ Cards Map    │ Cards Map   │    │
│  │ + Overlay    │              │             │    │
│  └──────────────┴──────────────┴─────────────┘    │
│                                                     │
│  setInterval(fetchData, 5000)                      │
└─────────────────────────────────────────────────────┘
```

---

## State Management

### Dashboard State
```javascript
const [aqiData, setAqiData] = useState(null);           // Heatmap + Sensors
const [priorityData, setPriorityData] = useState(null); // Top 5 Zones
const [sensorData, setSensorData] = useState(null);     // Sensor readings
const [loading, setLoading] = useState(true);           // Loading flag
const [error, setError] = useState(null);               // Error message
const [lastUpdate, setLastUpdate] = useState(null);     // Update timestamp
```

### Component-Level State

**HeatmapVisualization**
- Uses `useRef` for canvas reference
- Re-renders on prop changes via `useEffect`

**SensorsList & PriorityZones**
- Stateless components
- Render based on props
- Use conditional rendering for loading/error states

---

## Performance Optimizations

1. **Parallel API Calls**
   - All three endpoints called with `Promise.all()`
   - Faster data loading

2. **Canvas Rendering**
   - Efficient pixel-by-pixel drawing
   - Only redraws on data change

3. **Interval Management**
   - Cleanup on unmount prevents memory leaks
   - Consistent 5-second refresh rate

4. **Conditional Rendering**
   - Components skip rendering during loading
   - Error states render without re-fetching

---

## Error Handling Strategy

1. **Network Errors**: Caught in try-catch blocks
2. **JSON Parsing**: Automatic via axios
3. **Missing Data**: Conditional rendering checks
4. **User Feedback**: Clear error messages with recovery steps

---

## Future Enhancement Opportunities

1. **Real-time WebSocket Integration**
   - Replace polling with WebSocket connection
   - Lower latency updates

2. **Advanced Heatmap Features**
   - Zoom functionality
   - Mouse hover AQI tooltip
   - Drag to pan

3. **Historical Analysis**
   - Timeline slider
   - Historical trend graphs
   - Comparison views

4. **Alerts & Notifications**
   - AQI threshold alerts
   - Push notifications
   - Email reports

5. **Export Functionality**
   - CSV export
   - PDF reports
   - PNG screenshots

6. **Mobile Responsiveness**
   - Touch interactions
   - Mobile-optimized layout
   - Native app version

---

## Testing Considerations

### Component Testing
- Mock API responses
- Test loading/error states
- Verify canvas rendering

### Integration Testing
- Test data flow from API to UI
- Verify state updates
- Check refresh behavior

### Performance Testing
- Monitor render times
- Check memory usage
- Verify interval cleanup

---

## Browser Compatibility

| Browser | Version | Status |
|---------|---------|--------|
| Chrome | 90+ | ✅ Full Support |
| Firefox | 88+ | ✅ Full Support |
| Safari | 14+ | ✅ Full Support |
| Edge | 90+ | ✅ Full Support |

---

## Troubleshooting Guide

| Issue | Cause | Solution |
|-------|-------|----------|
| Heatmap blank | Data not loaded | Check `/aqi_matrix` endpoint |
| No sensors visible | Sensor data missing | Verify `/aqi` endpoint |
| No priority zones | API error | Check `/priority_zones` endpoint |
| App won't render | Component error | Check browser console |
| Data not updating | Interval issue | Check browser dev tools |

---

## Summary

The VayuMap frontend is a well-structured React application that:
- ✅ Integrates all backend routes
- ✅ Provides real-time data visualization
- ✅ Handles errors gracefully
- ✅ Maintains clean component architecture
- ✅ Optimizes for performance
- ✅ Uses modern React patterns (hooks, functional components)

All components work together to create a comprehensive air quality monitoring dashboard.
