#!/usr/bin/env python3
"""
Test optimizer with current config to see what's happening.
"""

import json
from optimiser import run_optimisation, get_current_config

print("=" * 60)
print("Testing Current Configuration")
print("=" * 60)

# Get current config
cfg = get_current_config()

print("\nCurrent Configuration:")
print(f"Staff: {cfg['staff']}")
print(f"\nStaff Cost: {cfg['staff_cost']}")
print(f"Staff Max Hours: {cfg['staff_max_hours']}")
print(f"\nStaff Availability:")
for staff, avail in cfg['staff_availability'].items():
    print(f"  {staff}: {avail}")

print(f"\nShift Requirements:")
for shift, req in sorted(cfg['shift_requirements'].items()):
    print(f"  {shift}: {req}")

print("\n" + "=" * 60)
print("Running Optimization...")
print("=" * 60)

results = run_optimisation(verbose=True, export_path=None)

print("\n" + "=" * 60)
print("Results:")
print("=" * 60)

if results:
    print(f"\nStatus: {results.get('status')}")
    print(f"Feasible: {results.get('feasible', 'N/A')}")
    
    if results.get('feasible', True):
        print(f"Total Cost: ${results.get('total_cost', 0):.2f}")
        print("\nAssignments:")
        for staff, data in results.get('assignments', {}).items():
            print(f"  {staff}: {', '.join(data['shifts']) if data['shifts'] else 'None'} ({data['hours']}hrs)")
    else:
        print("\n--- Infeasibility Analysis ---")
        analysis = results.get('analysis', {})
        
        if analysis.get('issues'):
            print("\nIssues:")
            for issue in analysis['issues']:
                print(f"  • {issue}")
        
        if analysis.get('suggestions'):
            print("\nSuggestions:")
            for suggestion in analysis['suggestions']:
                print(f"  ✓ {suggestion}")
else:
    print("\nNo results returned")
