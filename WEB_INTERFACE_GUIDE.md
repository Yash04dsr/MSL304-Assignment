# MediFlow Suite - Web Interface Guide

**Complete Guide to Features and Backend Science**

---

## 🌐 Web Interface Overview

The MediFlow Suite provides a modern, responsive web interface for healthcare optimization. Access it at `http://localhost:5000` (or ports 5001-5009 if 5000 is busy).

---

## 📊 Features & Backend Science

### 1. Patient Flow Simulator

#### **What It Does**
Simulates patient flow through a healthcare facility to identify bottlenecks and optimize staffing.

#### **User Interface**
- **Input Parameters:**
  - Arrival Rate (λ): Patients arriving per hour
  - Service Rate (μ): Patients served per hour per staff
  - Servers (c): Number of staff members
  - Duration: Simulation time in hours
  - Random Seed: For reproducible results

- **Visual Results:**
  - Animated counters showing key metrics
  - Color-coded status alerts (Critical/Warning/Caution/Healthy)
  - Specific recommendations with exact numbers
  - Scientific verification using Little's Law

#### **Backend Science: M/M/c Queueing Theory**

**Mathematical Model:**
```
M/M/c Queue:
- First M: Memoryless (Poisson) arrivals
- Second M: Memoryless (Exponential) service times  
- c: Multiple parallel servers
```

**Key Calculations:**

1. **Traffic Intensity (ρ)**
   ```
   ρ = λ/(μ × c)
   ```
   - **Critical Rule:** ρ < 1.0 required for stability
   - When ρ ≥ 1.0: Queues grow infinitely (mathematical proof)
   - Example: λ=10, μ=4, c=3 → ρ=0.833 (stable)

2. **Average Queue Length (L)**
   ```
   L = λ × W  (Little's Law)
   ```
   - L: Average number in queue
   - λ: Arrival rate
   - W: Average wait time

3. **Utilization (U)**
   ```
   U = (Total Busy Time) / (Total Available Time)
   U = Σ(service times) / (c × hours)
   ```
   - Industry standard: Keep U < 90%
   - Optimal range: 75-85%

4. **Coefficient of Variation (CoV)**
   ```
   CoV = σ / μ
   ```
   - Measures wait time consistency
   - CoV > 1.5 indicates high variability

**Backend Process:**
1. SimPy creates discrete-event simulation environment
2. Patient arrivals generated from Poisson process: `inter = random.expovariate(λ)`
3. Service times from exponential distribution: `service = random.expovariate(μ)`
4. Resource (staff) allocated using simpy.Resource(capacity=c)
5. Results calculated using queueing theory formulas
6. Exported to JSON with timestamp

**Bottleneck Detection Algorithm:**
```python
if traffic_intensity >= 1.0:
    level = "CRITICAL"
    required_servers = ceil(λ/μ) + 1
    recommendation = f"Add {required_servers - c} staff"
elif utilization > 0.90:
    level = "WARNING"  
    target_servers = ceil(c × U / 0.85)
    recommendation = f"Add {target_servers - c} staff for 85% target"
elif utilization > 0.75:
    level = "CAUTION"
    recommendation = "Monitor during peaks"
else:
    level = "HEALTHY"
    if utilization < 0.50:
        recommendation = "Consider reducing off-peak staff"
```

---

### 2. Staff Rota Optimizer

#### **What It Does**
Generates optimal weekly staff schedules that minimize cost while meeting all shift requirements and constraints.

#### **User Interface**
- **Configuration Editor:**
  - Editable staff table (name, cost, max hours, availability)
  - Add/remove staff members dynamically
  - Shift requirements per day/time
  - Test configuration before saving
  
- **Quick Actions:**
  - Save & Optimize: Saves config and runs optimization
  - Test Config: Validates without saving
  - Reset: Reloads from config.json

- **Results Display:**
  - Total weekly cost with animation
  - Staff assignments table
  - Hours worked per staff member

#### **Backend Science: Integer Linear Programming**

**Mathematical Model:**
```
Minimize: Σ (cost[s] × hours_worked[s]) for all staff s

Subject to:
1. Coverage constraint: Σ x[s,sh] ≥ required[sh] for each shift sh
2. Availability constraint: x[s,sh] = 0 if s not available for sh
3. Max hours constraint: Σ x[s,sh] × duration[sh] ≤ max_hours[s]
4. One shift per day: Σ x[s,sh] ≤ 1 for all sh in same day
5. Binary constraint: x[s,sh] ∈ {0, 1}
```

**Variables:**
- `x[s,sh]`: Binary (0 or 1) - whether staff s works shift sh
- `cost[s]`: Hourly cost for staff s
- `required[sh]`: Minimum staff needed for shift sh
- `max_hours[s]`: Maximum weekly hours for staff s

**Backend Process:**
1. PuLP creates linear programming problem
2. Decision variables: `x[(staff, shift)]` for all combinations
3. Objective function: Minimize total cost
   ```python
   objective = Σ (STAFF_COST[s] × SHIFT_DURATION[sh] × x[s,sh])
   ```
4. Constraints added:
   ```python
   # Coverage
   for shift in SHIFTS:
       problem += Σ x[s,shift] >= SHIFT_REQUIREMENTS[shift]
   
   # Availability  
   for staff in STAFF:
       for shift not in STAFF_AVAILABILITY[staff]:
           problem += x[staff,shift] == 0
   
   # Max hours
   for staff in STAFF:
       problem += Σ (x[staff,sh] × duration[sh]) <= MAX_HOURS[staff]
   
   # One shift per day
   for staff in STAFF:
       for day in DAYS:
           problem += Σ x[staff,shift] <= 1 for shift in day
   ```
5. PuLP solver finds optimal solution (CBC, GLPK, or CPLEX)
6. Results extracted and formatted

**Feasibility Check:**
- Problem marked "Infeasible" if constraints cannot be satisfied
- Common reasons: Insufficient staff availability, conflicting requirements
- Test endpoint validates before saving

---

### 3. Results Management

#### **What It Does**
Lists and retrieves previously saved simulation and optimization results.

#### **User Interface**
- Table showing all saved results
- Type badges (Simulation/Optimization)
- Timestamp and unique ID
- View button to see details

#### **Backend Process**
1. Scans `results/` directory for JSON files
2. Parses filenames: `simulation_YYYYMMDD_HHMMSS.json`
3. Extracts metadata (type, ID, timestamp)
4. Returns sorted list by date
5. Individual results loaded from JSON on request

---

## 🎨 UI/UX Design Principles

### **Visual Design**
- **Color System:** Purple-blue gradient background for modern feel
- **Glass Morphism:** Navbar uses backdrop blur and transparency
- **Elevation:** 5-level shadow system for depth hierarchy
- **Typography:** Inter font with 8 weight variations (400-800)

### **Animations**
- **Counter Animations:** Numbers count up smoothly (800ms duration)
- **Staggered Lists:** Recommendations appear one-by-one (50ms delay)
- **Fade Transitions:** Views fade in/out (300ms cubic-bezier easing)
- **Hover Effects:** Cards lift with shadow increase (transform: translateY)

### **User Feedback**
- **Toast Notifications:** Non-blocking, auto-dismiss after 3s
- **Loading States:** Spinners on buttons with disabled state
- **Form Validation:** Real-time with red borders for errors
- **Progress Indicators:** Loading overlays for async operations

---

## 🔧 Technical Architecture

### **Frontend Stack**
```
HTML5 + Bootstrap 5
├── CSS Custom Properties (design system)
├── Vanilla JavaScript (no frameworks)
└── Fetch API (AJAX requests)
```

### **Backend Stack**
```
Flask REST API (Python)
├── SimPy (discrete-event simulation)
├── PuLP (linear programming)
└── JSON (configuration & results)
```

### **API Endpoints**
```
GET  /                      → Serve web interface
GET  /api                   → API information
GET  /api/health            → Health check
POST /api/simulate          → Run simulation
POST /api/optimize          → Run optimization
GET  /api/config            → Get configuration
PUT  /api/config            → Update configuration
POST /api/config/test       → Test configuration
GET  /api/results           → List all results
GET  /api/results/<id>      → Get specific result
```

### **Data Flow**

**Simulation:**
```
User Input → JavaScript Form
    ↓
Fetch POST /api/simulate
    ↓
Flask validates parameters
    ↓
SimPy creates environment
    ↓
Patient generator (Poisson arrivals)
    ↓
Service process (Exponential service)
    ↓
Calculate metrics (queueing theory)
    ↓
JSON response with results
    ↓
JavaScript displays with animations
```

**Optimization:**
```
User edits config → JavaScript collects data
    ↓
Fetch PUT /api/config (save)
    ↓
Fetch POST /api/optimize
    ↓
Flask loads config.json
    ↓
PuLP creates LP problem
    ↓
Add constraints (coverage, availability, hours)
    ↓
Solver finds optimal solution
    ↓
Extract assignments
    ↓
JSON response with results
    ↓
JavaScript displays in table
```

---

## 📈 Performance Considerations

### **Simulation Performance**
- Time complexity: O(n) where n = number of patients
- Memory: O(n) to store wait/service times
- Typical simulation: 500 patients in <1 second

### **Optimization Performance**
- Complexity: NP-hard (integer programming)
- Variables: |STAFF| × |SHIFTS| (typically 40-100)
- Constraints: O(|STAFF| × |SHIFTS|)
- Solve time: <1 second for typical problems

### **Frontend Performance**
- Animations: Hardware-accelerated (GPU)
- 60 FPS target using transform/opacity
- Debounced input validation
- Lazy loading for results list

---

## 🔐 Configuration System

### **config.json Structure**
```json
{
  "simulator": {
    "default_arrival_rate": 10,
    "default_service_rate": 4,
    "default_servers": 3,
    "default_hours": 50
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
    },
    "shift_duration_hours": 8,
    "days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
    "times": ["AM", "PM"]
  }
}
```

### **Configuration Workflow**
1. Load from `config.json` at startup
2. Edit via web interface
3. Test validates feasibility
4. Save updates file atomically
5. Reload modules to apply changes

---

## 🧪 Testing & Validation

### **Simulation Tests**
- **Deterministic:** Same seed produces same results
- **Little's Law:** L ≈ λW (within 1% tolerance)
- **Stability:** ρ < 1.0 ensures bounded queues
- **Edge Cases:** Zero arrivals, single server, high load

### **Optimization Tests**
- **Feasibility:** Valid constraints produce solution
- **Infeasibility:** Conflicting constraints detected
- **Cost Calculation:** Manual verification of objective value
- **Constraint Satisfaction:** All requirements met

### **UI Tests**
- **Responsive:** Works on mobile, tablet, desktop
- **Accessibility:** Keyboard navigation, focus states
- **Error Handling:** Invalid inputs rejected gracefully
- **Cross-browser:** Chrome, Firefox, Safari, Edge

---

## 🎓 Key Takeaways

### **For Healthcare Managers**
- **Trust the Math:** Bottleneck detection uses proven queueing theory
- **Actionable Insights:** Specific recommendations (e.g., "Add 2 staff")
- **Cost Optimization:** Find minimum-cost schedules automatically
- **What-If Analysis:** Test scenarios before implementing

### **For Data Analysts**
- **Scientific Rigor:** M/M/c model with mathematical verification
- **Transparent Methods:** All formulas and calculations explained
- **Exportable Results:** JSON format for further analysis
- **Reproducible:** Random seed ensures repeatability

### **For Developers**
- **Clean Architecture:** REST API, modular components
- **Modern Stack:** Flask, SimPy, PuLP, Bootstrap
- **Extensible:** Easy to add new features/endpoints
- **Well-Documented:** Code comments and type hints

---

## 📚 Scientific References

1. **Queueing Theory**
   - Kleinrock, L. (1975). *Queueing Systems, Volume 1: Theory*
   - Gross, D., & Harris, C. M. (1998). *Fundamentals of Queueing Theory*

2. **Little's Law**
   - Little, J. D. (1961). "A Proof for the Queuing Formula: L = λW"
   - Operations Research, 9(3), 383-387

3. **Integer Programming**
   - Wolsey, L. A. (1998). *Integer Programming*
   - Bertsimas, D., & Weismantel, R. (2005). *Optimization over Integers*

4. **Healthcare Applications**
   - Green, L. (2006). "Queueing Analysis in Healthcare"
   - Carter, M. W., & Lapierre, S. D. (2001). "Scheduling Emergency Room Physicians"

---

## 🚀 Quick Reference

### **Starting the Server**
```bash
cd "/Users/yash/Downloads/MSL Assignment"
python api.py
```

### **Running Tests**
```bash
pytest tests/
```

### **Example Simulation Input**
- Arrival Rate: 10 patients/hour
- Service Rate: 4 patients/hour/staff
- Servers: 3 staff members
- Duration: 50 hours
- Expected: Healthy system (ρ = 0.833)

### **Example Optimization**
- 4 staff members with different costs
- 10 shifts (5 days × 2 times)
- Various availability constraints
- Expected: Minimum cost schedule meeting all requirements

---

**Version:** 2.0  
**Last Updated:** November 16, 2025  
**Documentation:** Complete feature and science guide
