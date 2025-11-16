import pulp
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path: Path = Path("config.json")) -> Dict:
    """Load configuration from JSON file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Config file {config_path} not found, using defaults")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config file: {e}")
        raise


# Default configuration (fallback)
DEFAULT_STAFF = ["Nurse_A", "Nurse_B", "Nurse_C", "Tech_D"]

DEFAULT_STAFF_COST = {
    "Nurse_A": 20,
    "Nurse_B": 20,
    "Nurse_C": 22,
    "Tech_D": 15
}

DEFAULT_STAFF_MAX_HOURS = {
    "Nurse_A": 40,
    "Nurse_B": 40,
    "Nurse_C": 30,
    "Tech_D": 40
}

DEFAULT_DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]
DEFAULT_TIMES = ["AM", "PM"]

DEFAULT_SHIFT_REQUIREMENTS = {
    "Mon_AM": 2, "Mon_PM": 1,
    "Tue_AM": 2, "Tue_PM": 2,
    "Wed_AM": 2, "Wed_PM": 1,
    "Thu_AM": 2, "Thu_PM": 2,
    "Fri_AM": 2, "Fri_PM": 1
}

DEFAULT_STAFF_AVAILABILITY = {
    "Nurse_A": ["Mon_AM", "Tue_AM", "Wed_AM", "Thu_AM", "Fri_AM"],
    "Nurse_B": ["Mon_PM", "Tue_PM", "Wed_PM", "Thu_PM", "Fri_PM"],
    "Nurse_C": ["Mon_AM", "Tue_AM", "Wed_PM", "Thu_AM", "Fri_PM"],
    "Tech_D":  ["Mon_AM", "Mon_PM", "Tue_AM", "Tue_PM", "Wed_AM", "Thu_PM", "Fri_AM"]
}

def get_current_config() -> Dict:
    """
    Get current configuration from file, reload each time to pick up changes.
    Returns a dictionary with all configuration values.
    """
    try:
        config = load_config()
        opt_config = config.get("optimiser", {})
        
        # Extract staff configuration
        staff_config = opt_config.get("staff", {})
        
        if staff_config:
            staff_list = list(staff_config.keys())
            staff_cost = {s: staff_config[s]["cost"] for s in staff_list}
            staff_max_hours = {s: staff_config[s]["max_hours"] for s in staff_list}
            staff_availability = {s: staff_config[s]["availability"] for s in staff_list}
        else:
            staff_list = DEFAULT_STAFF
            staff_cost = DEFAULT_STAFF_COST
            staff_max_hours = DEFAULT_STAFF_MAX_HOURS
            staff_availability = DEFAULT_STAFF_AVAILABILITY
        
        days = opt_config.get("days", DEFAULT_DAYS)
        times = opt_config.get("times", DEFAULT_TIMES)
        shifts = [f"{d}_{t}" for d in days for t in times]
        shift_durations = {sh: opt_config.get("shift_duration_hours", 8) for sh in shifts}
        shift_requirements = opt_config.get("shift_requirements", DEFAULT_SHIFT_REQUIREMENTS)
        
        return {
            "staff": staff_list,
            "staff_cost": staff_cost,
            "staff_max_hours": staff_max_hours,
            "staff_availability": staff_availability,
            "days": days,
            "times": times,
            "shifts": shifts,
            "shift_durations": shift_durations,
            "shift_requirements": shift_requirements
        }
        
    except Exception as e:
        logger.warning(f"Error loading config, using defaults: {e}")
        return {
            "staff": DEFAULT_STAFF,
            "staff_cost": DEFAULT_STAFF_COST,
            "staff_max_hours": DEFAULT_STAFF_MAX_HOURS,
            "staff_availability": DEFAULT_STAFF_AVAILABILITY,
            "days": DEFAULT_DAYS,
            "times": DEFAULT_TIMES,
            "shifts": [f"{d}_{t}" for d in DEFAULT_DAYS for t in DEFAULT_TIMES],
            "shift_durations": {f"{d}_{t}": 8 for d in DEFAULT_DAYS for t in DEFAULT_TIMES},
            "shift_requirements": DEFAULT_SHIFT_REQUIREMENTS
        }


# Load initial config for backward compatibility (used by API endpoint)
_initial_config = get_current_config()
STAFF = _initial_config["staff"]
STAFF_COST = _initial_config["staff_cost"]
STAFF_MAX_HOURS = _initial_config["staff_max_hours"]
STAFF_AVAILABILITY = _initial_config["staff_availability"]
DAYS = _initial_config["days"]
TIMES = _initial_config["times"]
SHIFTS = _initial_config["shifts"]
SHIFT_DURATIONS = _initial_config["shift_durations"]
SHIFT_REQUIREMENTS = _initial_config["shift_requirements"]


def analyze_infeasibility(cfg: Dict) -> Dict:
    """
    Analyze configuration to identify why optimization might be infeasible.
    
    Args:
        cfg: Configuration dictionary from get_current_config()
    
    Returns:
        Dictionary with analysis and suggestions
    """
    staff = cfg["staff"]
    staff_max_hours = cfg["staff_max_hours"]
    staff_availability = cfg["staff_availability"]
    shifts = cfg["shifts"]
    shift_durations = cfg["shift_durations"]
    shift_requirements = cfg["shift_requirements"]
    
    issues = []
    suggestions = []
    
    # Check 1: Insufficient staff for shifts
    for shift in shifts:
        required = shift_requirements.get(shift, 0)
        available_staff = [s for s in staff if shift in staff_availability[s]]
        
        if len(available_staff) < required:
            issues.append(f"❌ {shift}: Requires {required} staff but only {len(available_staff)} available ({', '.join(available_staff) if available_staff else 'none'})")
            suggestions.append(f"• Add more staff available for {shift} or reduce requirement from {required} to {len(available_staff)}")
        elif len(available_staff) == required:
            issues.append(f"⚠️  {shift}: Exactly {required} staff available - no flexibility")
    
    # Check 2: Staff hour constraints
    for s in staff:
        available_shifts = [sh for sh in shifts if sh in staff_availability[s]]
        max_possible_hours = len(available_shifts) * shift_durations.get(available_shifts[0], 8)
        
        if max_possible_hours > staff_max_hours[s]:
            # This is normal, but if they're needed for many shifts it could be an issue
            pass
    
    # Check 3: Overworked staff (needed for many critical shifts)
    for s in staff:
        critical_shifts = []
        for shift in shifts:
            if shift in staff_availability[s]:
                available_for_shift = [st for st in staff if shift in staff_availability[st]]
                if len(available_for_shift) <= shift_requirements.get(shift, 0):
                    critical_shifts.append(shift)
        
        if len(critical_shifts) * 8 > staff_max_hours[s]:
            issues.append(f"⚠️  {s}: Needed for {len(critical_shifts)} critical shifts ({len(critical_shifts)*8}hrs) but max_hours is {staff_max_hours[s]}")
            suggestions.append(f"• Increase {s}'s max_hours from {staff_max_hours[s]} to {len(critical_shifts)*8} or more")
    
    # Check 4: Total coverage capacity
    total_required_hours = sum(shift_requirements.get(sh, 0) * shift_durations[sh] for sh in shifts)
    total_available_hours = sum(staff_max_hours[s] for s in staff)
    
    if total_required_hours > total_available_hours:
        issues.append(f"❌ Total required hours ({total_required_hours}) exceeds total available hours ({total_available_hours})")
        suggestions.append(f"• Add more staff or increase existing staff max_hours")
    
    # General suggestions if issues found
    if not suggestions:
        suggestions.append("• Try adding a new staff member with flexible availability")
        suggestions.append("• Review shift requirements - can any be reduced?")
        suggestions.append("• Check staff availability - ensure adequate coverage overlap")
    
    return {
        "has_issues": len(issues) > 0,
        "issues": issues,
        "suggestions": list(set(suggestions))  # Remove duplicates
    }


def row(cols, widths):
    return " | ".join(str(col).ljust(w) for col, w in zip(cols, widths))


def line(widths):
    total = sum(widths) + 3 * (len(widths) - 1)
    return "-" * total


def run_optimisation(verbose: bool = True, export_path: Optional[Path] = None) -> Optional[Dict]:
    """
    Run staff scheduling optimization.
    
    Args:
        verbose: Print detailed optimization results
        export_path: Path to export results JSON (None to skip export)
    
    Returns:
        Dictionary with optimization results, or None if infeasible
    """
    # Reload configuration from file to pick up any changes
    cfg = get_current_config()
    staff = cfg["staff"]
    staff_cost = cfg["staff_cost"]
    staff_max_hours = cfg["staff_max_hours"]
    staff_availability = cfg["staff_availability"]
    days = cfg["days"]
    shifts = cfg["shifts"]
    shift_durations = cfg["shift_durations"]
    shift_requirements = cfg["shift_requirements"]
    
    if verbose:
        print("\n--- MediFlow Rota Optimiser ---\n")
        print(f"Loaded configuration: {len(staff)} staff, {len(shifts)} shifts\n")

    try:
        # Create optimization model
        model = pulp.LpProblem("Staff_Scheduling", pulp.LpMinimize)
        x = pulp.LpVariable.dicts("Assign", (staff, shifts), 0, 1, cat="Binary")

        # Build list of allowed (staff, shift) pairs
        allowed = [(s, sh) for s in staff for sh in staff_availability[s] if sh in shifts]

        # Objective: minimize total cost
        model += pulp.lpSum(x[s][sh] * staff_cost[s] * shift_durations[sh] for s, sh in allowed)

        # Constraint: shift coverage requirements
        for sh in shifts:
            model += pulp.lpSum(x[s][sh] for s in staff if (s, sh) in allowed) >= shift_requirements.get(sh, 0)

        # Constraint: maximum hours per staff
        for s in staff:
            model += pulp.lpSum(x[s][sh] * shift_durations[sh] for sh in shifts if (s, sh) in allowed) <= staff_max_hours[s]

        # Constraint: enforce unavailability
        for s in staff:
            for sh in shifts:
                if (s, sh) not in allowed:
                    model += x[s][sh] == 0

        # Constraint: at most 1 shift per person per day
        for s in staff:
            for d in days:
                day_shifts = [f"{d}_AM", f"{d}_PM"]
                model += pulp.lpSum(x[s][sh] for sh in day_shifts if (s, sh) in allowed) <= 1

        # Solve
        logger.info("Starting optimization...")
        model.solve(pulp.PULP_CBC_CMD(msg=0))  # Silent solver
        status = pulp.LpStatus[model.status]
        
        if verbose:
            print(f"Status: {status}")

        if status != "Optimal":
            logger.warning(f"Optimization status: {status}")
            if verbose:
                print("⚠️  No optimal solution found.")
                print("\n--- Infeasibility Analysis ---\n")
            
            # Analyze why it's infeasible
            analysis = analyze_infeasibility(cfg)
            
            if verbose:
                if analysis["issues"]:
                    print("Potential Issues:")
                    for issue in analysis["issues"]:
                        print(f"  {issue}")
                
                print("\nSuggestions to Fix:")
                for suggestion in analysis["suggestions"]:
                    print(f"  {suggestion}")
            
            # Return infeasibility details
            return {
                "status": status,
                "feasible": False,
                "analysis": analysis,
                "message": "No feasible solution found - constraints cannot be satisfied"
            }

        cost = pulp.value(model.objective)
        logger.info(f"Optimal solution found with cost: ${cost:.2f}")
        
        if verbose:
            print(f"\nMinimum Weekly Cost: ${cost:.2f}\n")
            print("Staff Assignments\n")

        # Collect results
        assignments = {}
        headers = ["Staff", "Assigned Shifts", "Hours"]
        widths = [12, 40, 8]

        if verbose:
            print(row(headers, widths))
            print(line(widths))

        for s in staff:
            assigned = [sh for sh in shifts if (s, sh) in allowed and x[s][sh].value() == 1]
            hours = sum(shift_durations[sh] for sh in assigned)
            shifts_str = ", ".join(assigned) if assigned else "-"
            assignments[s] = {
                "shifts": assigned,
                "hours": hours
            }
            if verbose:
                print(row([s, shifts_str, hours], widths))
        
        # Prepare export data
        results = {
            "status": status,
            "feasible": True,
            "total_cost": cost,
            "assignments": assignments,
            "parameters": {
                "staff": staff,
                "shift_requirements": shift_requirements,
                "staff_cost": staff_cost,
                "staff_max_hours": staff_max_hours
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Export if requested
        if export_path:
            export_path.parent.mkdir(parents=True, exist_ok=True)
            with open(export_path, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"Results saved to {export_path}")
        
        return results
        
    except Exception as e:
        logger.error(f"Optimization error: {e}")
        if verbose:
            print(f"❌ Error during optimization: {e}")
        raise


if __name__ == "__main__":
    # Example usage with export
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_path = Path(f"results/optimisation_{timestamp}.json")
    
    results = run_optimisation(export_path=export_path)
    
    if results:
        print(f"\n✓ Results exported to: {export_path}")
