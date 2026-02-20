# VayuMap Frontend - Air Quality Monitoring System

A React-based frontend for the VayuMap air quality monitoring and prediction system. This interface visualizes real-time AQI data, sensor readings, and priority zones using interactive heatmaps and comprehensive dashboards.

## Features

- **Real-time Heatmap Visualization**: Interactive canvas-based visualization of air quality across a 100x100 grid
- **Sensor Monitoring**: Live display of all active AQI sensors with status indicators
- **Priority Zones**: Identification of top 5 priority zones based on AQI levels and population density
- **Color-coded AQI Indicators**: Visual representation of air quality from Good to Hazardous levels
- **Auto-refresh**: Data automatically updates every 5 seconds
- **Responsive Design**: Fully responsive layout that works on all screen sizes

## Project Structure

```
src/
├── components/
│   ├── Dashboard.jsx           # Main dashboard container
│   ├── HeatmapVisualization.jsx # Canvas-based heatmap component
│   ├── SensorsList.jsx         # Sensors display component
│   └── PriorityZones.jsx       # Priority zones display component
├── services/
│   └── api.js                  # Backend API integration
├── App.jsx                     # Main application component
├── App.css                     # Application styles
├── index.css                   # Global styles with Tailwind
└── main.jsx                    # Application entry point
```

## Available Components

### Dashboard
Main container component that orchestrates data fetching and layout management.
- Fetches data from all backend endpoints
- Manages loading and error states
- Auto-refreshes every 5 seconds

### HeatmapVisualization
Canvas-based heatmap renderer that displays:
- Interpolated AQI values across the grid
- Colored cells based on AQI levels
- Sensor locations and AQI values (blue circles with AQI number)
- Priority zones highlighted in purple

**AQI Color Scale:**
- Green: Good (0-50)
- Yellow: Moderate (51-100)
- Orange: Unhealthy for Sensitive Groups (101-150)
- Red: Unhealthy (151-200)
- Dark Red: Very Unhealthy (201-300)
- Indigo: Hazardous (300+)

### SensorsList
Displays all active sensors with:
- Sensor ID and location coordinates
- Real-time AQI readings
- Status indicators (Good, Moderate, Unhealthy, etc.)
- Color-coded status badges

### PriorityZones
Shows top 5 priority zones with:
- Grid position coordinates
- Priority score (0-100%)
- Visual progress bar
- Zones ranked by combined AQI and population impact

## Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Ensure backend servers are running:**
   - Sensor Server: http://localhost:3001
   - Processing Server: http://localhost:2000

## Configuration

The frontend connects to two backend servers:

- **Sensor Server** (port 3001): `http://localhost:3001/aqi`
  - Returns live sensor data
  
- **Processing Server** (port 2000):
  - `http://localhost:2000/aqi_matrix` - AQI heatmap data
  - `http://localhost:2000/priority_zones` - Priority zone calculations

If you need to change the backend URLs, edit `src/services/api.js`:

```javascript
const API_BASE_URL = 'http://localhost:2000';
const SENSOR_API_URL = 'http://localhost:3001';
```

## Running the Frontend

### Development Mode

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Build for Production

```bash
npm build
```

### Preview Production Build

```bash
npm run preview
```

## API Integration

The frontend uses the following API endpoints:

### 1. Get AQI Matrix
```
GET http://localhost:2000/aqi_matrix
```
Returns:
- `timestamp`: Timestamp of data
- `sensors`: Array of sensor objects with (x, y, aqi)
- `matrix`: 100x100 grid of interpolated AQI values

### 2. Get Priority Zones
```
GET http://localhost:2000/priority_zones
```
Returns:
- `timestamp`: Timestamp of calculation
- `top_5`: Array of top 5 priority zones with (x, y, score)

### 3. Get Sensor Data
```
GET http://localhost:3001/aqi
```
Returns:
- `sensors`: Array of all active sensors with positions and AQI readings

## Styling

The frontend uses:
- **Tailwind CSS**: Utility-first CSS framework for styling
- **Custom CSS**: Additional animations and effects in App.css
- **Responsive Grid**: Auto-adjusts layout based on screen size

## Performance Optimizations

- Canvas rendering for efficient heatmap display
- Automatic interval cleanup on component unmount
- Parallel data fetching for multiple endpoints
- Efficient state management with React hooks

## Error Handling

The dashboard includes comprehensive error handling:
- Network error messages if backend services are unavailable
- Graceful fallbacks for missing data
- User-friendly error notifications

## Browser Compatibility

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Development Dependencies

- React 19.2.0
- Vite 7.3.1
- Tailwind CSS 4.2.0
- Axios 1.13.5
- ESLint for code quality

## Troubleshooting

### Data not loading?
1. Verify backend servers are running on ports 2000 and 3001
2. Check browser console for CORS errors
3. Ensure CORS is enabled on backend servers

### Heatmap not displaying?
1. Clear browser cache
2. Check that canvas element is properly mounted
3. Verify sensor data format from API

### Refresh not working?
1. Check network tab in dev tools
2. Verify API endpoints are correct
3. Ensure backend servers respond with 200 status

## Future Enhancements

- Real-time alerts for dangerous AQI levels
- Historical data visualization
- Custom time range selection
- Export data to CSV/PDF
- Integration with weather API
- Machine learning predictions
- Mobile app version
