# MediFlow Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies
```bash
cd "/Users/yash/Downloads/MSL Assignment"
pip install -r requirements.txt
```

**Note:** If you only want the CLI (no web), install just:
```bash
pip install simpy pulp inquirer
```

### Step 2: Choose Your Interface

---

## Option A: Command-Line Interface (CLI)

### Basic Interactive Mode
```bash
python main.py
```
Then follow the menu:
1. Select "Patient Flow Simulator" or "Staff Rota Optimiser"
2. Enter parameters when prompted
3. View results in terminal

### With Auto-Export (Recommended)
```bash
python main.py --export
```
Results automatically saved to `results/` folder.

### Non-Interactive (Automation)
```bash
# Run simulation directly
python main.py --simulator \
  --arrival-rate 10 \
  --service-rate 4 \
  --servers 3 \
  --hours 50 \
  --export

# Run optimizer directly
python main.py --optimiser --export
```

---

## Option B: Web Interface (Recommended)

### Start the Server
```bash
python api.py
```

You'll see:
```
╔═══════════════════════════════════════════╗
║       MediFlow API Server Started         ║
╠═══════════════════════════════════════════╣
║  Access the API at:                       ║
║  http://localhost:5000                    ║
╚═══════════════════════════════════════════╝
```

### Open in Browser
Visit: **http://localhost:5000**

The web interface provides:
- 📊 Interactive forms for simulation
- 📅 One-click staff optimization
- 📈 Visual result displays
- 💾 Result history and downloads

---

## Testing the Installation

### Run Quick Test
```bash
# Test simulator
python -c "from simulator import run_simulation; print(run_simulation(10, 4, 3, 10, verbose=False))"

# Test optimizer
python -c "from optimiser import run_optimisation; run_optimisation(verbose=False)"
```

### Run Full Test Suite
```bash
pytest tests/ -v
```

Expected output: 20+ tests passing ✓

---

## Using the Simulator

### CLI Example
```bash
python main.py --simulator \
  --arrival-rate 10 \
  --service-rate 4 \
  --servers 3 \
  --hours 50
```

### Python API Example
```python
from simulator import run_simulation
from pathlib import Path

results = run_simulation(
    arrival_rate=10,      # patients/hour
    service_rate=4,       # patients/hour per staff
    servers=3,            # number of staff
    hours=50,             # simulation duration
    seed=42,              # for reproducibility
    verbose=True,         # show detailed output
    export_path=Path("results/my_sim.json")  # optional export
)

print(f"Average wait: {results['avg_wait_time']:.2f} hours")
print(f"Utilization: {results['utilization']*100:.1f}%")
```

### Web Interface
1. Click "Simulator" in navigation
2. Adjust sliders/inputs for parameters
3. Click "Run Simulation"
4. View results with metrics and status

---

## Using the Optimizer

### CLI Example
```bash
python main.py --optimiser --export
```

### Python API Example
```python
from optimiser import run_optimisation
from pathlib import Path

results = run_optimisation(
    verbose=True,
    export_path=Path("results/my_schedule.json")
)

if results:
    print(f"Total cost: ${results['total_cost']:.2f}")
    for staff, data in results['assignments'].items():
        print(f"{staff}: {len(data['shifts'])} shifts, {data['hours']} hours")
```

### Web Interface
1. Click "Optimizer" in navigation
2. Click "Run Optimization"
3. View optimal schedule and cost

---

## Configuration

### Edit Settings
Open `config.json` and modify:

```json
{
  "simulator": {
    "default_arrival_rate": 10,
    "default_service_rate": 4,
    "default_servers": 3,
    "default_simulation_hours": 50
  },
  "optimiser": {
    "staff": {
      "Nurse_A": {
        "cost": 20,
        "max_hours": 40,
        "availability": ["Mon_AM", "Tue_AM", ...]
      }
    },
    "shift_requirements": {
      "Mon_AM": 2,
      "Mon_PM": 1,
      ...
    }
  }
}
```

Changes take effect immediately for CLI.  
For web API, restart the server: `Ctrl+C` then `python api.py`

---

## Viewing Results

### Results Location
All exports saved to: `results/`

Files named:
- `simulation_YYYYMMDD_HHMMSS.json`
- `optimisation_YYYYMMDD_HHMMSS.json`

### View Result File
```bash
cat results/simulation_20251116_142530.json | python -m json.tool
```

### Via Web Interface
1. Click "Results" in navigation
2. Browse all saved results
3. Click "View" to see details

### Via API
```bash
# List all results
curl http://localhost:5000/api/results

# Get specific result
curl http://localhost:5000/api/results/simulation_20251116_142530
```

---

## Common Scenarios

### Scenario 1: What-if Analysis
```bash
# Test different staffing levels
for servers in 2 3 4 5; do
  python main.py --simulator \
    --arrival-rate 10 \
    --service-rate 4 \
    --servers $servers \
    --hours 100 \
    --export
done

# Compare results in results/ folder
```

### Scenario 2: Weekly Schedule
```bash
# Generate optimal weekly schedule
python main.py --optimiser --export

# Result shows:
# - Total weekly cost
# - Each staff member's assignments
# - Hours per person
```

### Scenario 3: Bottleneck Identification
```bash
# High arrival rate to test capacity
python main.py --simulator \
  --arrival-rate 20 \
  --service-rate 4 \
  --servers 3 \
  --hours 100

# Check if utilization > 90% (bottleneck warning)
```

---

## Troubleshooting

### Error: Module not found
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Error: Permission denied (logs/)
```bash
# Create directories manually
mkdir -p logs results
chmod 755 logs results
```

### Error: Port 5000 already in use
```bash
# Use different port
python api.py  # Edit line: app.run(port=5001)
```

### Web interface not loading
1. Check server is running: `python api.py`
2. Verify URL: `http://localhost:5000` (not https)
3. Check browser console for errors (F12)

### Tests failing
```bash
# Run tests with verbose output
pytest tests/ -v --tb=short

# Run specific test file
pytest tests/test_simulator.py -v
```

---

## Next Steps

### Learn More
- Read `README.md` for detailed documentation
- Read `WEB_UI_PLAN.md` for web architecture
- Read `IMPROVEMENTS_SUMMARY.md` for all changes

### Extend the System
1. **Add new staff types** - Edit `config.json`
2. **Custom shifts** - Modify shift requirements
3. **New constraints** - Edit `optimiser.py`
4. **Visualization** - Add charts to web UI

### Deploy to Production
```bash
# Use production server (Gunicorn)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 api:app

# Or use Docker (create Dockerfile)
docker build -t mediflow .
docker run -p 5000:5000 mediflow
```

---

## Support

### Check Logs
```bash
# View application logs
tail -f logs/mediflow.log

# Search for errors
grep ERROR logs/mediflow.log
```

### Run Diagnostics
```bash
# Test imports
python -c "import simpy, pulp, inquirer, flask; print('All imports OK')"

# Test configuration
python -c "from optimiser import load_config; print(load_config())"

# Test API health
curl http://localhost:5000/api/health
```

---

## Summary

**CLI:**
```bash
python main.py                    # Interactive mode
python main.py --export           # With auto-save
python main.py --simulator ...    # Direct simulation
```

**Web:**
```bash
python api.py                     # Start server
# Open: http://localhost:5000
```

**Tests:**
```bash
pytest tests/ -v                  # Run all tests
```

**That's it! You're ready to use MediFlow Suite. 🎉**
