#!/usr/bin/env python3
"""
Test script to verify infeasibility analysis works correctly.
Tests the exact scenario user reported: Nurse_A only available Wed/Thu/Fri
"""

import json
from optimiser import run_optimisation

# Modify config temporarily to test infeasibility
test_config = {
    "optimiser": {
        "staff": {
            "Nurse_A": {
                "cost": 25,
                "max_hours": 40,
                "availability": ["Wed_AM", "Thu_AM", "Fri_AM"]  # User's test case
            },
            "Nurse_B": {
                "cost": 25,
                "max_hours": 40,
                "availability": ["Mon_PM", "Tue_PM", "Wed_PM", "Thu_PM", "Fri_PM"]
            },
            "Nurse_C": {
                "cost": 25,
                "max_hours": 40,
                "availability": ["Mon_AM", "Tue_AM", "Wed_AM", "Thu_AM", "Fri_AM"]
            },
            "Tech_D": {
                "cost": 20,
                "max_hours": 40,
                "availability": ["Mon_AM", "Mon_PM", "Tue_AM", "Tue_PM", "Wed_AM", "Wed_PM", "Thu_AM", "Thu_PM", "Fri_AM", "Fri_PM"]
            }
        },
        "days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
        "shifts": ["Mon_AM", "Mon_PM", "Tue_AM", "Tue_PM", "Wed_AM", "Wed_PM", "Thu_AM", "Thu_PM", "Fri_AM", "Fri_PM"],
        "shift_durations": {
            "Mon_AM": 8, "Mon_PM": 8,
            "Tue_AM": 8, "Tue_PM": 8,
            "Wed_AM": 8, "Wed_PM": 8,
            "Thu_AM": 8, "Thu_PM": 8,
            "Fri_AM": 8, "Fri_PM": 8
        },
        "shift_requirements": {
            "Mon_AM": 2, "Mon_PM": 2,
            "Tue_AM": 2, "Tue_PM": 2,
            "Wed_AM": 2, "Wed_PM": 2,
            "Thu_AM": 2, "Thu_PM": 2,
            "Fri_AM": 2, "Fri_PM": 2
        }
    }
}

# Save test config
with open('config.json', 'w') as f:
    json.dump(test_config, f, indent=2)

print("=" * 60)
print("Testing Infeasibility Analysis")
print("=" * 60)
print("\nScenario: Nurse_A only available Wed_AM, Thu_AM, Fri_AM")
print("Expected: INFEASIBLE (Mon_AM needs 2 staff, only Nurse_C and Tech_D)")
print()

# Run optimization
results = run_optimisation(verbose=True, export_path=None)

print("\n" + "=" * 60)
print("Results:")
print("=" * 60)

if results:
    print(f"\nStatus: {results.get('status')}")
    print(f"Feasible: {results.get('feasible', 'N/A')}")
    
    if not results.get('feasible', True):
        print("\n--- Infeasibility Analysis ---")
        analysis = results.get('analysis', {})
        
        if analysis.get('issues'):
            print("\nIssues Identified:")
            for issue in analysis['issues']:
                print(f"  • {issue}")
        
        if analysis.get('suggestions'):
            print("\nSuggestions:")
            for suggestion in analysis['suggestions']:
                print(f"  ✓ {suggestion}")
    else:
        print(f"\nTotal Cost: ${results.get('total_cost', 0):.2f}")
        print("\nThis should NOT happen - configuration should be infeasible!")
else:
    print("\nNo results returned (old behavior - should not happen)")

print("\n" + "=" * 60)
