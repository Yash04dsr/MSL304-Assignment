# MediFlow Suite

**A Modern Decision-Support System for Healthcare Optimization**

[![Version](https://img.shields.io/badge/version-2.0-blue.svg)](https://github.com/Yash04dsr/MSL304-Assignment)
[![Python](https://img.shields.io/badge/python-3.11+-brightgreen.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 🎯 Overview

MediFlow Suite combines **scientifically rigorous queueing theory** and **integer programming optimization** to help healthcare facilities:
- 🔬 Analyze patient flow with M/M/c queueing simulation
- 📊 Identify bottlenecks using traffic intensity analysis (ρ = λ/(μ*c))
- 📅 Generate optimal staff schedules that minimize costs
- ⚡ Make data-driven staffing decisions based on mathematical models

## ✨ Features

### 🏥 Patient Flow Simulator (Enhanced v2.0)
- **Scientifically Accurate Bottleneck Detection** using queueing theory
  - Traffic intensity calculation (ρ = λ/(μ*c))
  - Stability analysis (ρ < 1.0 required)
  - 4 severity levels: Critical, Warning, Caution, Healthy
  - Little's Law verification (L = λW)
  - Coefficient of variation analysis
- **Specific Recommendations** with exact staffing requirements
- Wait times displayed in minutes for intuitive understanding
- Root cause analysis for high variance scenarios
- M/M/c queueing model with Poisson arrivals
- Export results with full scientific context

### 📅 Staff Rota Optimizer
- Generates minimum-cost weekly schedules using integer programming (PuLP)
- **Web-based configuration editor** - no code changes needed
- **Test configurations** before saving to validate feasibility
- **Add/remove staff dynamically** through the UI
- Respects staff availability, maximum hours, and shift requirements
- Ensures no staff works multiple shifts per day
- Produces detailed assignment reports with cost breakdown
- Export optimization results for further analysis

### 🎨 Modern Web Interface
- **Contemporary Design** with gradient backgrounds and glass effects
- **Smooth Animations** for better user experience
- **Toast Notifications** for non-blocking feedback
- **Loading States** with progress indicators
- **Real-time Validation** for form inputs
- **Responsive Design** for desktop and mobile
- **Accessibility Features** with proper focus states

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/Yash04dsr/MSL304-Assignment.git
cd MSL304-Assignment
```

### 2. Create virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

## Usage

### Interactive CLI
```bash
python main.py
```

Select from the menu:
1. **Patient Flow Simulator** - Input arrival rate, service rate, staff count, and duration
2. **Staff Rota Optimiser** - Run optimization with current configuration
3. **Exit**

### Python API

#### Simulator
```python
from simulator import run_simulation

results = run_simulation(
    arrival_rate=10,      # patients/hour
    service_rate=4,       # patients/hour per staff
    servers=3,            # number of staff
    hours=50              # simulation duration
)

print(f"Average wait: {results['avg_wait_time']:.2f} hours")
print(f"Utilization: {results['utilization']*100:.1f}%")
```

#### Optimiser
```python
from optimiser import run_optimisation

run_optimisation()
```

## Configuration

Edit `config.json` to customize:
- Default simulation parameters
- Staff details (cost, hours, availability)
- Shift requirements
- Export and logging settings

## Project Structure

```
MSL Assignment/
├── main.py              # CLI interface
├── simulator.py         # Patient flow simulation
├── optimiser.py         # Staff scheduling optimization
├── config.json          # Configuration file
├── requirements.txt     # Python dependencies
├── README.md            # This file
├── tests/               # Unit tests
│   ├── test_simulator.py
│   └── test_optimiser.py
└── results/             # Exported results (auto-created)
```

## Technical Details

### Simulation Model
- **Type**: M/M/c queue (Poisson arrivals, exponential service)
- **Key Metrics**: 
  - Average wait time (W_q)
  - Average queue length (L_q = λW_q, Little's Law)
  - Staff utilization (ρ = busy time / available time)

### Optimization Model
- **Type**: Binary Integer Programming
- **Objective**: Minimize total labor cost
- **Constraints**:
  - Shift coverage requirements
  - Staff maximum hours
  - Availability restrictions
  - Max 1 shift per staff per day

## Testing

Run tests with pytest:
```bash
pytest tests/ -v
pytest tests/ --cov=. --cov-report=html
```

## Future Enhancements

### Web Interface (Planned)
- Flask/FastAPI backend with REST API
- React/Vue.js frontend
- Real-time simulation visualization
- Scenario comparison dashboard
- Export to CSV/Excel/PDF

### Advanced Features (Planned)
- Multi-facility optimization
- Shift preference scoring
- Fairness constraints
- Historical data integration
- Predictive analytics

## Dependencies

- **simpy** - Discrete-event simulation
- **pulp** - Linear programming
- **inquirer** - Interactive CLI
- **pandas** - Data manipulation
- **pytest** - Testing

## Authors

- Abhikrit Bhardwaj (2022ME21333)
- Sakhare Yash Balram (2022CH71496)

## Course

MSL304 – Operations Management  
Indian Institute of Technology Delhi

## License

This project is for academic purposes.

## References

1. SimPy Documentation: https://simpy.readthedocs.io/
2. PuLP Documentation: https://coin-or.github.io/pulp/
3. Queueing Theory Fundamentals
4. Integer Programming for Staff Scheduling
