# MediFlow Testing & Configuration Guide

## 🧪 New Features Overview

### 1. Enhanced Bottleneck Detection
The simulator now provides **precise, multi-level bottleneck analysis** with:
- 🔴 **Critical** - System unstable (utilization > 100%)
- 🟠 **Warning** - High utilization (> 90%) or long waits
- 🟡 **Caution** - Moderate load (75-90% utilization)
- 🟢 **Healthy** - Optimal operation (< 75% utilization)

**New Metrics:**
- Traffic intensity (ρ = λ/(μ*c))
- Maximum wait time
- Detailed recommendations
- Staffing suggestions

### 2. Editable Staff Configuration
You can now **view and edit** all staff and shift settings through the web interface:
- Add/remove staff members
- Modify hourly costs
- Adjust maximum hours
- Edit shift availability
- Change shift requirements
- **Test configurations** before saving

---

## 📊 Testing Bottleneck Detection

### Scenario 1: Critical Bottleneck (Unstable System)

**CLI Test:**
```bash
python main.py --simulator \
  --arrival-rate 20 \
  --service-rate 4 \
  --servers 3 \
  --hours 100
```

**Expected Output:**
```
🔴 CRITICAL: System Unstable - Immediate Action Required

Recommendations:
• Add at least 2 more staff members
• System is overloaded - queues will grow indefinitely
• Consider reducing arrival rate or improving service speed
```

**What to observe:**
- Utilization > 100%
- Traffic intensity ≥ 1.0
- Growing wait times

**Web Test:**
1. Open http://localhost:5001 (or your port)
2. Navigate to "Simulator"
3. Enter: Arrival Rate=20, Service Rate=4, Servers=3, Hours=100
4. Click "Run Simulation"
5. See red alert with critical warnings

---

### Scenario 2: High Utilization Warning

**CLI Test:**
```bash
python main.py --simulator \
  --arrival-rate 12 \
  --service-rate 4 \
  --servers 3 \
  --hours 100
```

**Expected Output:**
```
🟠 WARNING: High Utilization - Bottleneck Detected

Recommendations:
• Current utilization: 95.2% (target: <90%)
• Average wait time: 0.87 hrs (consider reducing)
• Suggest adding 1 staff member(s)
```

**What to observe:**
- Utilization 90-100%
- Noticeable wait times
- Queue building up

---

### Scenario 3: Moderate Load (Caution)

**CLI Test:**
```bash
python main.py --simulator \
  --arrival-rate 10 \
  --service-rate 4 \
  --servers 3 \
  --hours 50
```

**Expected Output:**
```
🟡 CAUTION: Moderate Load - Monitor Closely

Recommendations:
• System is approaching capacity (83.3%)
• Monitor during peak periods
• Consider contingency staffing plans
```

---

### Scenario 4: Healthy System

**CLI Test:**
```bash
python main.py --simulator \
  --arrival-rate 5 \
  --service-rate 4 \
  --servers 3 \
  --hours 50
```

**Expected Output:**
```
🟢 HEALTHY: System Operating Efficiently

Recommendations:
• Utilization is optimal (41.7%)
• Wait times are acceptable (0.02 hrs)
• Current staffing level is appropriate
```

---

## ⚙️ Testing Staff Configuration Editor

### Access Configuration Editor

**Option 1: Web Interface (Recommended)**
1. Start server: `python api.py` (or use full venv path)
2. Open browser: http://localhost:5001
3. Click "Optimizer" in navigation
4. Configuration automatically loads

**Option 2: Direct API**
```bash
# View current config
curl http://localhost:5001/api/config

# Get formatted output
curl http://localhost:5001/api/config | python -m json.tool
```

---

### Test 1: View and Edit Staff

**Steps:**
1. Open Optimizer page
2. See staff table with current values:
   - Nurse_A: $20/hr, 40 max hours
   - Nurse_B: $20/hr, 40 max hours
   - Nurse_C: $22/hr, 30 max hours
   - Tech_D: $15/hr, 40 max hours

3. **Edit values** directly in the table:
   - Change Nurse_A cost to $25
   - Change Tech_D max hours to 35

4. Click "Save & Optimize"
5. See updated schedule with new costs

**What to verify:**
- ✓ Total cost reflects new hourly rate
- ✓ Tech_D assigned ≤ 35 hours
- ✓ Configuration persists in config.json

---

### Test 2: Add New Staff Member

**Steps:**
1. In Optimizer page, click "Add Staff"
2. Fill in new row:
   - Name: "Nurse_E"
   - Cost: $18
   - Max Hours: 30
   - Availability: "Wed_AM, Thu_AM, Fri_AM"

3. Click "Test Config" to verify feasibility
4. If feasible, click "Save & Optimize"

**What to verify:**
- ✓ New staff appears in results
- ✓ Assigned only to available shifts
- ✓ Respects 30-hour limit

---

### Test 3: Modify Shift Requirements

**Steps:**
1. Scroll to "Shift Requirements" table
2. Change "Wed_AM" from 2 to 3
3. Click "Test Config"

**Expected:** 
- If feasible: "✓ Configuration is valid!"
- If infeasible: "⚠️ No valid solution - adjust availability"

**What to verify:**
- ✓ System detects if impossible to staff
- ✓ Provides feedback before saving

---

### Test 4: Test Infeasible Configuration

**Create impossible scenario:**
1. Set all shift requirements to 10
2. Keep only 4 staff members
3. Click "Test Config"

**Expected Result:**
```
⚠️ Configuration is infeasible - no valid solution found.

Please adjust staff availability or shift requirements.
```

**What to verify:**
- ✓ System detects infeasibility
- ✓ Doesn't save bad configuration
- ✓ Provides helpful error message

---

### Test 5: Reset Configuration

**Steps:**
1. Make several edits to staff/shifts
2. Click "Reset to Defaults"
3. Confirm the dialog

**Expected:**
- Configuration reloads from config.json
- All manual edits are discarded
- Returns to original values

---

## 🔬 Advanced Testing Scenarios

### Scenario A: Peak Hour Staffing

**Problem:** High arrival rate during specific shifts

**Test:**
```bash
# Simulate morning rush
python main.py --simulator \
  --arrival-rate 25 \
  --service-rate 5 \
  --servers 4 \
  --hours 4
```

**Expected recommendations:**
- Suggest adding temporary staff
- Identify morning shifts as bottleneck
- Calculate optimal staffing level

**Then optimize:**
1. Go to Optimizer
2. Increase Mon_AM, Tue_AM requirements to 3
3. Test configuration
4. Save and run

---

### Scenario B: Cost Optimization

**Goal:** Reduce labor costs while maintaining service

**Steps:**
1. Start with current config
2. Note total cost (e.g., $2552)
3. Reduce high-cost staff hours:
   - Nurse_C: 30 → 20 max hours
4. Test configuration
5. If feasible, save and compare costs

**What to verify:**
- ✓ Cost decreased
- ✓ All shifts still covered
- ✓ No one exceeds limits

---

### Scenario C: Staff Availability Changes

**Problem:** Staff member on vacation

**Steps:**
1. Select Nurse_B
2. Remove all availability (blank the field)
3. Test configuration
4. See if system can compensate

**Expected:**
- Either: "Still feasible with remaining staff"
- Or: "Need to hire temporary replacement"

---

## 📋 Configuration File Examples

### Example 1: Night Shift Addition

Edit `config.json`:
```json
{
  "optimiser": {
    "times": ["AM", "PM", "Night"],
    "shift_requirements": {
      "Mon_AM": 2,
      "Mon_PM": 1,
      "Mon_Night": 1,
      ...
    }
  }
}
```

Then reload in web interface.

---

### Example 2: Weekend Coverage

```json
{
  "optimiser": {
    "days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    "shift_requirements": {
      "Sat_AM": 1,
      "Sat_PM": 1,
      "Sun_AM": 1,
      "Sun_PM": 1
    }
  }
}
```

---

## 🧪 Validation Tests

### Test Valid Input Ranges

**Simulator:**
```python
# Valid
arrival_rate: 0.1 to 1000 (any positive float)
service_rate: 0.1 to 1000
servers: 1 to 100
hours: 1 to 10000

# Invalid (should error)
arrival_rate: 0 or negative
servers: 0
```

**Optimizer:**
```python
# Valid
cost: 0 to 1000 ($/hour)
max_hours: 1 to 168 (per week)
availability: any valid shift list

# Invalid
cost: negative
max_hours: 0 or > 168
availability: non-existent shifts
```

---

## 📊 Expected Bottleneck Thresholds

| Utilization | Traffic Intensity | Status | Action |
|-------------|------------------|--------|--------|
| > 100% | ≥ 1.0 | 🔴 Critical | Add staff immediately |
| 90-100% | 0.9-1.0 | 🟠 Warning | Plan to add staff |
| 75-90% | 0.75-0.9 | 🟡 Caution | Monitor closely |
| < 75% | < 0.75 | 🟢 Healthy | Optimal |
| < 50% | < 0.5 | 🟢 Healthy | Consider reducing staff |

---

## 🎯 Test Checklist

### Simulator Tests
- [ ] Test critical bottleneck (util > 100%)
- [ ] Test warning level (util 90-100%)
- [ ] Test caution level (util 75-90%)
- [ ] Test healthy system (util < 75%)
- [ ] Verify recommendations appear
- [ ] Check max wait time display
- [ ] Test traffic intensity calculation

### Optimizer Tests
- [ ] Load existing configuration
- [ ] Edit staff member details
- [ ] Add new staff member
- [ ] Delete staff member
- [ ] Modify shift requirements
- [ ] Test configuration feasibility
- [ ] Save configuration
- [ ] Run optimization with new config
- [ ] Reset to defaults

### Web Interface Tests
- [ ] Config editor loads correctly
- [ ] All fields are editable
- [ ] "Test Config" works
- [ ] "Save & Optimize" updates and runs
- [ ] Error messages display properly
- [ ] Results show updated costs

### API Tests
- [ ] GET /api/config returns current settings
- [ ] PUT /api/config saves new settings
- [ ] POST /api/config/test validates without saving
- [ ] POST /api/simulate returns recommendations
- [ ] POST /api/optimize uses updated config

---

## 🚀 Quick Test Commands

```bash
# Terminal 1: Start server
python api.py

# Terminal 2: Test API
curl http://localhost:5001/api/config
curl http://localhost:5001/api/health

# Terminal 3: Run simulations
python main.py --simulator --arrival-rate 20 --service-rate 4 --servers 3 --hours 50
python main.py --optimiser --export

# Test with different parameters
for rate in 5 10 15 20 25; do
  echo "Testing arrival rate: $rate"
  python main.py --simulator --arrival-rate $rate --service-rate 4 --servers 3 --hours 20
  echo "---"
done
```

---

## 📝 Notes

- **Web port:** Automatically selects 5000-5009
- **Config changes:** Take effect immediately for optimizer
- **Simulator:** Uses seed=42 by default for reproducibility
- **Export:** Results saved to `results/` with timestamps
- **Logs:** Check `logs/mediflow.log` for debugging

---

## 🎓 Learning Objectives

These new features teach:
1. **Queueing Theory:** Understanding utilization and traffic intensity
2. **Constraint Programming:** Feasibility of staff schedules
3. **What-if Analysis:** Testing scenarios before implementation
4. **UI/UX Design:** Editable configuration interfaces
5. **API Design:** RESTful endpoints for configuration management

**Your system is now fully interactive and production-ready!** 🎉
