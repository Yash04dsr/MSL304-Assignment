# How to Test Infeasibility Detection

## Quick Start

1. **Access the Web Interface**
   - Server is running on: http://localhost:5001
   - Open in your browser

2. **Go to Configuration Tab**
   - Click "Configuration" in the top navigation

3. **Test Infeasible Configuration**

### Test Case 1: Overworked Staff (User's Scenario)

**Steps:**
1. Find "Nurse_A" availability field
2. Change from: `Mon_AM, Tue_AM, Wed_AM, Thu_AM, Fri_AM`
3. Change to: `Wed_AM, Thu_AM, Fri_AM`
4. Click "Test Configuration"

**Expected Result:**
- Alert popup showing:
  ```
  Issues:
  • Tech_D: Needed for 7 critical shifts (56hrs) but max_hours is 40
  • Mon_AM: Exactly 2 staff available - no flexibility
  [...]
  
  Suggestions:
  • Increase Tech_D's max_hours from 40 to 56 or more
  ```

### Test Case 2: Insufficient Staff

**Steps:**
1. Set "Nurse_A" availability to: `Wed_AM`
2. Set "Nurse_C" availability to: `Wed_PM`
3. Click "Test Configuration"

**Expected Result:**
- Issues showing multiple shifts without enough staff
- Suggestions to add staff or adjust availability

### Test Case 3: Valid Configuration

**Steps:**
1. Restore default values:
   - Nurse_A: `Mon_AM, Tue_AM, Wed_AM, Thu_AM, Fri_AM`
   - Nurse_B: `Mon_PM, Tue_PM, Wed_PM, Thu_PM, Fri_PM`
   - Nurse_C: `Mon_AM, Tue_AM, Wed_AM, Thu_AM, Fri_AM`
   - Tech_D: `Mon_AM, Mon_PM, Tue_AM, Tue_PM, Wed_AM, Wed_PM, Thu_AM, Thu_PM, Fri_AM, Fri_PM`
2. Click "Test Configuration"

**Expected Result:**
- Green toast: "Configuration is valid! Estimated cost: $800.00"

## Full Optimization Test

1. Make any configuration change
2. Click "Save & Run Optimizer" (instead of Test)
3. If infeasible, you'll see:
   - Red alert box at top
   - Card with red header: "Identified Issues"
   - Card with yellow header: "Suggested Solutions"
4. If feasible, you'll see:
   - Total cost with animation
   - Staff assignment table

## What to Look For

### Infeasibility Display Features:
- ✅ Clean, professional layout
- ✅ Red alert with clear message
- ✅ Icons (⚠️ bug, 💡 lightbulb)
- ✅ Bullet-pointed lists
- ✅ Specific staff/shift names
- ✅ Actionable suggestions (not vague)
- ✅ Smooth fade-in animation

### Console Logging:
- Open browser DevTools (F12)
- Check Console tab for:
  ```
  === Saving Configuration ===
  Staff config: {...}
  Sending PUT request to /api/config...
  Save response: {...}
  ```

## Common Scenarios

### Scenario: Not Enough Staff
**Problem**: Shift requires 3 staff, only 2 available
**Suggestion**: "Add staff for Mon_AM (currently only Nurse_A, Tech_D)"

### Scenario: Overworked Staff
**Problem**: Staff needed 48hrs but max is 40hrs
**Suggestion**: "Increase Nurse_A's max_hours from 40 to 48 or more"

### Scenario: No Flexibility
**Problem**: Exactly required staff, no backup
**Suggestion**: "Add backup staff for Mon_AM"

## Troubleshooting

### If you don't see infeasibility details:
1. Check browser console for errors
2. Verify server is running on port 5001
3. Hard refresh page (Cmd+Shift+R / Ctrl+Shift+F5)
4. Check that `analyze_infeasibility()` exists in optimiser.py

### If server won't start:
```bash
# Stop all Python processes
pkill -f "python.*api.py"

# Restart
cd "/Users/yash/Downloads/MSL Assignment"
source venv/bin/activate
python api.py
```

### If changes don't apply:
- Server auto-reloads on file changes
- If stuck, manually restart server
- Clear browser cache

## API Testing (Advanced)

Test directly with curl:

```bash
# Test infeasible config
curl -X POST http://localhost:5001/api/config/test \
  -H "Content-Type: application/json" \
  -d @test_config.json

# Run optimization
curl -X POST http://localhost:5001/api/optimize \
  -H "Content-Type: application/json" \
  -d '{"export": true}'
```

## Success Criteria

The feature works correctly if:
1. ✅ Infeasible configs show specific issues
2. ✅ Suggestions are actionable (staff names, hour amounts)
3. ✅ Valid configs show success message
4. ✅ UI is clean and professional
5. ✅ No JavaScript errors in console
6. ✅ Server doesn't crash
7. ✅ Toast notifications appear
8. ✅ Test doesn't save changes
9. ✅ Save & Run does save changes
10. ✅ Animations work smoothly
