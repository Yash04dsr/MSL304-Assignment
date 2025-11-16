# ✅ NEW CHECKBOX INTERFACE - USER GUIDE

## What Changed?

### OLD Interface (Comma-Separated Input) ❌
- Had to type: "Mon_AM, Tue_AM, Wed_AM, Thu_AM, Fri_AM"
- Easy to make typos
- Hard to see what's selected
- Parsing errors common

### NEW Interface (Checkbox Grid) ✅
- Visual checkboxes for each shift
- Click to select/deselect
- "Select All" / "Clear All" buttons
- No typing needed
- Error-proof input

---

## How to Use

### 1. Access Configuration
- Open http://localhost:5001
- Click **"Configuration"** tab
- Wait for config to load

### 2. Edit Staff Member

Each staff member now has a **card** with:

```
┌─────────────────────────────────────┐
│ [Nurse_A                      ] [🗑️] │  ← Name and Delete button
├─────────────────────────────────────┤
│ Cost ($/hr): [25]  Max Hours: [40]  │  ← Numbers
│                                     │
│ Availability (select shifts):       │
│ ☑ Mon_AM    ☑ Mon_PM               │
│ ☑ Tue_AM    ☑ Tue_PM               │  ← Checkboxes!
│ ☑ Wed_AM    ☑ Wed_PM               │
│ ☑ Thu_AM    ☑ Thu_PM               │
│ ☑ Fri_AM    ☑ Fri_PM               │
│                                     │
│ [Select All] [Clear All]            │  ← Quick buttons
└─────────────────────────────────────┘
```

### 3. Make Changes

**To enable shifts**: Click checkboxes ✅
**To disable shifts**: Unclick checkboxes ⬜
**Quick select all**: Click "Select All"
**Quick clear all**: Click "Clear All"

### 4. Test or Save

- **"Test Config"** = Check if it works (doesn't save)
- **"Save & Optimize"** = Save and run (automatically switches to Results tab)

---

## Example: Limit Nurse_A to Wednesdays Only

1. Find Nurse_A card
2. Click "Clear All" to uncheck everything
3. Check ONLY:
   - ☑ Wed_AM
   - ☑ Wed_PM
4. Click "Test Config"
5. See if it's feasible

---

## Visual Indicators

### Staff Card Colors:
- **Light gray header**: Normal staff card
- **Name field**: White input box
- **Checkboxes**: Blue when selected

### Buttons:
- **Green "Add Staff"**: Add new staff member
- **Blue "Select All"**: Check all shifts for this person
- **Gray "Clear All"**: Uncheck all shifts
- **Red 🗑️**: Delete this staff member
- **Blue "Test Config"**: Check feasibility without saving
- **Green "Save & Optimize"**: Save and run optimization

---

## Benefits

1. **No Typos**: Click instead of type
2. **Visual Feedback**: See exactly what's selected
3. **Faster**: Select All/Clear All buttons
4. **Reliable**: Data captured correctly every time
5. **Professional**: Modern card-based interface

---

## Common Actions

### Add Full-Time Staff (All Shifts)
1. Click "Add Staff"
2. Name: [Your Name]
3. Cost: [Your Rate]
4. Max Hours: 80
5. Click "Select All"

### Add Part-Time Staff (AM Only)
1. Click "Add Staff"
2. Name: [Your Name]
3. Max Hours: 40
4. Check only: Mon_AM, Tue_AM, Wed_AM, Thu_AM, Fri_AM

### Add Weekend Coverage
(Note: Current version only has Mon-Fri, but same concept)

### Remove Staff Member
1. Find their card
2. Click red 🗑️ button in top-right

---

## Troubleshooting

### Issue: Can't see checkboxes
**Solution**: Hard refresh browser (Cmd+Shift+R or Ctrl+Shift+F5)

### Issue: Changes not saving
**Solution**: Click "Save & Optimize", not just "Test Config"

### Issue: Infeasible even with staff available
**Solution**: 
1. Check if staff max_hours is enough
2. Check if enough staff available for each shift
3. Look at suggestions in red box

### Issue: Page looks weird
**Solution**: 
1. Clear browser cache
2. Hard refresh
3. Make sure JavaScript is enabled

---

## Pro Tips

### Quickly test scenarios:
1. Click "Test Config" (doesn't save)
2. See if feasible
3. Adjust checkboxes
4. Test again
5. When satisfied, click "Save & Optimize"

### Copy staff availability:
1. Look at existing staff's checkboxes
2. Add new staff
3. Check same boxes

### See all shifts:
Look at the "Available Shifts" panel on the right:
- Mon_AM, Mon_PM
- Tue_AM, Tue_PM
- Wed_AM, Wed_PM
- Thu_AM, Thu_PM
- Fri_AM, Fri_PM

---

## What Hasn't Changed

- **Shift requirements** still editable in table
- **Cost per hour** still number input
- **Max hours** still number input
- **Optimization algorithm** same (PuLP linear programming)
- **Infeasibility analysis** same detailed output

---

## Testing the New Interface

### Quick Test (30 seconds):
1. Open Configuration tab
2. Find Nurse_A
3. Click "Clear All"
4. Check only Wed_AM
5. Click "Test Config"
6. Should see infeasibility

### Full Test (2 minutes):
1. Use Test Case 2 from TEST_CASES.md
2. Configure as specified
3. Verify infeasibility detection
4. Use Test Case 1
5. Verify feasibility

---

## Success!

If you can:
- ✅ See checkboxes instead of text input
- ✅ Click checkboxes to select shifts
- ✅ Use Select All / Clear All buttons
- ✅ Test Config without errors
- ✅ Save & Optimize works
- ✅ Results tab shows assignments

Then the new interface is working perfectly! 🎉
