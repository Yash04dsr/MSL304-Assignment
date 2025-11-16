# MediFlow Web UI Implementation Plan

## Architecture Overview

### Backend: Flask REST API
- **Framework**: Flask with Flask-CORS
- **Purpose**: Expose simulation and optimization as REST endpoints
- **Features**:
  - `/api/simulate` - POST endpoint for running simulations
  - `/api/optimize` - POST endpoint for staff scheduling
  - `/api/results` - GET endpoint for retrieving saved results
  - `/api/config` - GET/PUT endpoints for configuration
  - WebSocket support for real-time simulation progress

### Frontend: Modern Web UI
**Option 1: React.js** (Recommended for rich interactivity)
- Components: Simulation form, Results dashboard, Charts
- Libraries: Recharts (visualization), Ant Design/Material-UI (components)
- State management: React Context or Redux

**Option 2: Vue.js** (Lighter, faster development)
- Components: Similar structure to React
- Libraries: Chart.js, Vuetify
- State management: Vuex or Pinia

**Option 3: Simple HTML/JS** (Quick prototype)
- Vanilla JavaScript with Fetch API
- Bootstrap for styling
- Chart.js for visualization

## API Endpoints Specification

### POST /api/simulate
**Request**:
```json
{
  "arrival_rate": 10,
  "service_rate": 4,
  "servers": 3,
  "hours": 50,
  "seed": 42
}
```

**Response**:
```json
{
  "status": "success",
  "results": {
    "avg_wait_time": 0.247,
    "avg_queue_length": 2.47,
    "utilization": 0.83,
    "patients_served": 498,
    "system_status": "Operating within limits"
  },
  "export_id": "simulation_20251116_142530"
}
```

### POST /api/optimize
**Request**:
```json
{
  "custom_config": {
    "shift_requirements": {...},
    "staff": {...}
  }
}
```

**Response**:
```json
{
  "status": "success",
  "results": {
    "total_cost": 2552,
    "assignments": {...},
    "status": "Optimal"
  },
  "export_id": "optimisation_20251116_142530"
}
```

### GET /api/results/{export_id}
Returns saved JSON result file.

### GET /api/config
Returns current system configuration.

### PUT /api/config
Updates system configuration.

## UI Components

### 1. Dashboard (Home)
- Welcome message
- Quick stats (recent runs, total saved results)
- Navigation cards to Simulator and Optimizer

### 2. Simulator Page
- **Input Form**:
  - Arrival rate (slider + input)
  - Service rate (slider + input)
  - Number of servers (stepper)
  - Simulation hours (slider)
  - Seed (optional)
- **Run Button** with loading indicator
- **Results Panel**:
  - Key metrics in cards
  - Utilization gauge chart
  - Wait time histogram
  - Queue length over time (line chart)
  - System status alert
- **Export Options**: Download JSON, CSV
- **Save to History** button

### 3. Optimizer Page
- **Configuration Editor** (JSON editor or form)
- **Staff Table** (editable):
  - Name, Cost, Max Hours, Availability
- **Shift Requirements Table**
- **Run Button**
- **Results Panel**:
  - Total cost (large display)
  - Staff assignment table/calendar view
  - Utilization by staff (bar chart)
  - Cost breakdown (pie chart)
- **Export Options**: Download JSON, Excel schedule

### 4. Results History Page
- Table of all saved results
- Filter by type (simulation/optimization)
- Search by date
- Click to view details
- Compare multiple results
- Delete old results

### 5. Configuration Page
- Editable JSON/YAML configuration
- Form-based editor for common settings
- Validate and save
- Reset to defaults

## Visualization Components

### Charts for Simulator:
1. **Utilization Gauge** - Shows % utilization with color coding
2. **Wait Time Distribution** - Histogram
3. **Queue Length Over Time** - Line chart
4. **Patient Flow** - Animated visualization (advanced)

### Charts for Optimizer:
1. **Schedule Calendar** - Weekly grid view
2. **Cost Breakdown** - Pie chart by staff
3. **Hours Distribution** - Bar chart by staff
4. **Coverage Heatmap** - Shift requirements vs actual

## Implementation Steps

### Phase 1: Backend API (Priority: High)
1. Create `api.py` with Flask app
2. Implement `/api/simulate` endpoint
3. Implement `/api/optimize` endpoint
4. Add CORS support
5. Test with Postman/curl

### Phase 2: Simple Frontend (Priority: High)
1. Create `static/` directory
2. Build `index.html` with Bootstrap
3. Create `app.js` with Fetch API calls
4. Add basic forms and result display
5. Deploy and test

### Phase 3: Enhanced Frontend (Priority: Medium)
1. Set up React/Vue project
2. Create reusable components
3. Add state management
4. Implement all pages
5. Add charts and visualizations

### Phase 4: Advanced Features (Priority: Low)
1. Real-time simulation progress (WebSocket)
2. Scenario comparison tool
3. What-if analysis dashboard
4. Historical trends
5. Export to PDF reports
6. User authentication
7. Multi-facility support

## Deployment Options

### Development:
```bash
flask run --host=0.0.0.0 --port=5000
# Frontend: npm start (React) or serve static files
```

### Production:
- **Backend**: Gunicorn + Nginx
- **Frontend**: Static hosting (Netlify, Vercel, S3)
- **Database**: PostgreSQL for history (optional)
- **Cache**: Redis for session management (optional)

## File Structure for Web Version

```
MSL Assignment/
├── api.py                 # Flask REST API
├── web/
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── js/
│   │   │   ├── app.js
│   │   │   ├── simulator.js
│   │   │   └── optimizer.js
│   │   └── img/
│   ├── templates/
│   │   ├── index.html
│   │   ├── simulator.html
│   │   ├── optimizer.html
│   │   └── results.html
│   └── react-app/         # Optional: React frontend
│       ├── src/
│       ├── public/
│       └── package.json
├── main.py                # CLI version
├── simulator.py
├── optimiser.py
└── config.json
```

## Security Considerations

1. **Input Validation**: Sanitize all user inputs
2. **Rate Limiting**: Prevent API abuse
3. **CORS**: Configure allowed origins
4. **File Upload**: Validate config files
5. **Authentication**: Add JWT tokens for production
6. **HTTPS**: Use SSL certificates

## Next Steps

To implement the web UI, run:
```bash
# Install web dependencies
pip install flask flask-cors flask-socketio

# Create API file
# (see api.py starter template)

# Create simple HTML frontend
# (see web/templates/ starter files)

# Run the web server
python api.py
```

Then visit `http://localhost:5000` in your browser.
