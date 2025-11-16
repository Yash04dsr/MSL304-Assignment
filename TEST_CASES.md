# Rota Optimizer Test Cases

## How to Test

1. Open http://localhost:5001 in your browser
2. Go to **Configuration** tab
3. For each test case below:
   - Set the configuration as specified
   - Click **"Test Config"** to check feasibility (doesn't save)
   - Or click **"Save & Optimize"** to save and run
4. Verify the expected result

---

## Test Case 1: Default Valid Configuration ✅

**Purpose**: Verify basic functionality works

**Configuration**:
- **Nurse_A**: Cost $25/hr, Max 40hrs
  - Availability: Mon_AM, Tue_AM, Wed_AM, Thu_AM, Fri_AM
- **Nurse_B**: Cost $25/hr, Max 40hrs
  - Availability: Mon_PM, Tue_PM, Wed_PM, Thu_PM, Fri_PM
- **Nurse_C**: Cost $25/hr, Max 40hrs
  - Availability: Mon_AM, Tue_AM, Wed_AM, Thu_AM, Fri_AM
- **Tech_D**: Cost $20/hr, Max 48hrs
  - Availability: All shifts (Mon-Fri, AM & PM)

**Shift Requirements**: All shifts need 2 staff

**Expected Result**: ✅ **FEASIBLE**
- Total Cost: $3600
- All shifts covered
- No staff overworked

---

## Test Case 2: Insufficient Staff ❌

**Purpose**: Test infeasibility detection when not enough staff

**Configuration**:
- **Nurse_A**: Cost $25/hr, Max 40hrs
  - Availability: **ONLY Wed_AM, Thu_AM, Fri_AM** (remove Mon & Tue)
- **Nurse_B**: Cost $25/hr, Max 40hrs
  - Availability: Mon_PM, Tue_PM, Wed_PM, Thu_PM, Fri_PM
- **Nurse_C**: Cost $25/hr, Max 40hrs
  - Availability: Mon_AM, Tue_AM, Wed_AM, Thu_AM, Fri_AM
- **Tech_D**: Cost $20/hr, Max **40hrs** (reduce from 48)
  - Availability: All shifts

**Shift Requirements**: All shifts need 2 staff

**Expected Result**: ❌ **INFEASIBLE**
- Issue: Tech_D needed for 7 critical shifts (56hrs) but max is 40hrs
- Suggestion: "Increase Tech_D's max_hours from 40 to 56 or more"

---

## Test Case 3: Minimal Staffing ✅

**Purpose**: Test with minimum requirements

**Configuration**:
- **Nurse_A**: Cost $25/hr, Max 40hrs
  - Availability: Mon_AM, Tue_AM, Wed_AM, Thu_AM, Fri_AM
- **Tech_B**: Cost $20/hr, Max 40hrs
  - Availability: Mon_PM, Tue_PM, Wed_PM, Thu_PM, Fri_PM

**Shift Requirements**: All shifts need **1 staff** (reduce from 2)

**Expected Result**: ✅ **FEASIBLE**
- Total Cost: $1800
- Simple 1:1 assignment

---

## Test Case 4: High Demand ❌

**Purpose**: Test when demand exceeds capacity

**Configuration**:
- Keep default 4 staff with same availability

**Shift Requirements**: All shifts need **3 staff** (increase from 2)

**Expected Result**: ❌ **INFEASIBLE**
- Issue: Several shifts don't have 3 available staff
- Suggestion: "Add more staff" or "Reduce requirements"

---

## Test Case 5: Single Day Only ✅

**Purpose**: Test partial week scheduling

**Configuration**:
- **Nurse_A**: Cost $25/hr, Max 16hrs
  - Availability: **ONLY Mon_AM, Mon_PM** (Monday only)
- **Nurse_B**: Cost $25/hr, Max 16hrs
  - Availability: **ONLY Mon_AM, Mon_PM** (Monday only)

**Shift Requirements**:
- Mon_AM: 2
- Mon_PM: 2
- All other shifts: **0** (set Tue-Fri to 0)

**Expected Result**: ✅ **FEASIBLE**
- Total Cost: $800 (2 staff × 16hrs × $25)
- Only Monday scheduled

---

## Test Case 6: Overlapping Availability ✅

**Purpose**: Test optimal assignment with multiple options

**Configuration**:
- **Nurse_A**: Cost $30/hr, Max 40hrs
  - Availability: All AM shifts
- **Nurse_B**: Cost $25/hr, Max 40hrs
  - Availability: All PM shifts
- **Nurse_C**: Cost $20/hr, Max 40hrs
  - Availability: **All shifts** (both AM and PM)
- **Tech_D**: Cost $15/hr, Max 40hrs
  - Availability: **All shifts**

**Shift Requirements**: All shifts need 2 staff

**Expected Result**: ✅ **FEASIBLE**
- Should prefer cheaper staff (Tech_D and Nurse_C)
- Total Cost: Lower than default (around $2800-$3000)

---

## Test Case 7: No Availability ❌

**Purpose**: Test complete infeasibility

**Configuration**:
- **Nurse_A**: Cost $25/hr, Max 40hrs
  - Availability: **NONE** (uncheck all boxes)

**Shift Requirements**: Any shift needs 1+ staff

**Expected Result**: ❌ **INFEASIBLE**
- Issue: "Nurse_A has no availability"
- OR: "Mon_AM requires 2 staff but only 0 available"

---

## Test Case 8: Exact Capacity ⚠️

**Purpose**: Test edge case with no buffer

**Configuration**:
- **Nurse_A**: Cost $25/hr, Max **80hrs**
  - Availability: **All 10 shifts**
- No other staff (delete Nurse_B, Nurse_C, Tech_D)

**Shift Requirements**: All shifts need 1 staff

**Expected Result**: ✅ **FEASIBLE** but warning
- Total Cost: $2000 (80hrs × $25)
- Should show warning: "No flexibility - exactly required staff"

---

## Test Case 9: Cost Optimization ✅

**Purpose**: Verify cost minimization

**Configuration**:
- **Expensive_Nurse**: Cost **$50/hr**, Max 80hrs
  - Availability: All shifts
- **Cheap_Tech**: Cost **$10/hr**, Max 80hrs
  - Availability: All shifts

**Shift Requirements**: All shifts need 1 staff

**Expected Result**: ✅ **FEASIBLE**
- Should assign ALL shifts to Cheap_Tech (cost $10/hr)
- Total Cost: $800 (80hrs × $10)
- Expensive_Nurse assigned to 0 hours

---

## Test Case 10: Real-World Scenario ✅

**Purpose**: Realistic hospital scheduling

**Configuration**:
- **Dr_Smith**: Cost $80/hr, Max 40hrs
  - Availability: Mon_AM, Wed_AM, Fri_AM
- **Dr_Jones**: Cost $80/hr, Max 40hrs
  - Availability: Tue_AM, Thu_AM
- **Nurse_Alice**: Cost $35/hr, Max 40hrs
  - Availability: All AM shifts
- **Nurse_Bob**: Cost $35/hr, Max 40hrs
  - Availability: All PM shifts
- **Tech_Charlie**: Cost $20/hr, Max 48hrs
  - Availability: All shifts

**Shift Requirements**:
- All AM shifts: 2 staff
- All PM shifts: 1 staff

**Expected Result**: ✅ **FEASIBLE**
- Doctors used sparingly (expensive)
- Nurses and tech fill gaps
- Total Cost: ~$3500-$4000

---

## Quick Test Procedure

1. **Test Default**: Load page → Click "Optimize" → Should show $3600
2. **Test Checkbox Input**: 
   - Go to Config tab
   - Uncheck some boxes for Nurse_A
   - Click "Test Config"
   - Should see infeasibility if too few checked
3. **Test Real Change**:
   - Change Nurse_A to only Wed_AM, Thu_AM, Fri_AM
   - Set Tech_D max_hours to 40
   - Click "Save & Optimize"
   - Should see infeasibility with Tech_D overwork message

---

## Expected Behaviors

### When Feasible:
- ✅ Green toast notification
- Results tab shows cost and assignments
- Table shows which shifts each staff works
- Hours add up correctly

### When Infeasible:
- ❌ Red alert box appears
- Lists specific issues (e.g., "Tech_D needs 56hrs but max is 40")
- Shows actionable suggestions (e.g., "Increase max_hours to 56")
- No assignment table shown

### Always:
- Configuration saves to file
- Each optimization creates new result file
- Console shows detailed logs
- No JavaScript errors in browser console

---

## Debugging Tips

If tests fail:

1. **Open Browser Console** (F12)
2. **Check for errors** (red text)
3. **Look for logs**:
   - "Collected config:" - shows what was sent
   - "Save response:" - shows API response
4. **Verify checkboxes**: 
   - Click "Select All" for a staff member
   - Test Config should work
5. **Hard refresh**: Cmd+Shift+R (Mac) or Ctrl+Shift+F5 (Windows)

---

## Success Criteria

All tests pass if:
- ✅ Test 1, 3, 5, 6, 9, 10 show FEASIBLE
- ❌ Test 2, 4, 7 show INFEASIBLE with correct suggestions
- ⚠️ Test 8 shows FEASIBLE (maybe with warning)
- Cost calculations are accurate
- No JavaScript errors
- Each run produces different results when config changes
