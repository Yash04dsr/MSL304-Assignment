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

# Load from config if available
try:
    config = load_config()
    opt_config = config.get("optimiser", {})
    
    # Extract staff configuration
    staff_config = opt_config.get("staff", {})
    STAFF = list(staff_config.keys()) if staff_config else DEFAULT_STAFF
    STAFF_COST = {s: staff_config[s]["cost"] for s in STAFF} if staff_config else DEFAULT_STAFF_COST
    STAFF_MAX_HOURS = {s: staff_config[s]["max_hours"] for s in STAFF} if staff_config else DEFAULT_STAFF_MAX_HOURS
    STAFF_AVAILABILITY = {s: staff_config[s]["availability"] for s in STAFF} if staff_config else DEFAULT_STAFF_AVAILABILITY
    
    DAYS = opt_config.get("days", DEFAULT_DAYS)
    TIMES = opt_config.get("times", DEFAULT_TIMES)
    SHIFTS = [f"{d}_{t}" for d in DAYS for t in TIMES]
    SHIFT_DURATIONS = {sh: opt_config.get("shift_duration_hours", 8) for sh in SHIFTS}
    SHIFT_REQUIREMENTS = opt_config.get("shift_requirements", DEFAULT_SHIFT_REQUIREMENTS)
    
except Exception as e:
    logger.warning(f"Error loading config, using defaults: {e}")
    STAFF = DEFAULT_STAFF
    STAFF_COST = DEFAULT_STAFF_COST
    STAFF_MAX_HOURS = DEFAULT_STAFF_MAX_HOURS
    DAYS = DEFAULT_DAYS
    TIMES = DEFAULT_TIMES
    SHIFTS = [f"{d}_{t}" for d in DAYS for t in TIMES]
    SHIFT_DURATIONS = {sh: 8 for sh in SHIFTS}
    SHIFT_REQUIREMENTS = DEFAULT_SHIFT_REQUIREMENTS
    STAFF_AVAILABILITY = DEFAULT_STAFF_AVAILABILITY


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
    if verbose:
        print("\n--- MediFlow Rota Optimiser ---\n")

    try:
        # Create optimization model
        model = pulp.LpProblem("Staff_Scheduling", pulp.LpMinimize)
        x = pulp.LpVariable.dicts("Assign", (STAFF, SHIFTS), 0, 1, cat="Binary")

        # Build list of allowed (staff, shift) pairs
        allowed = [(s, sh) for s in STAFF for sh in STAFF_AVAILABILITY[s] if sh in SHIFTS]

        # Objective: minimize total cost
        model += pulp.lpSum(x[s][sh] * STAFF_COST[s] * SHIFT_DURATIONS[sh] for s, sh in allowed)

        # Constraint: shift coverage requirements
        for sh in SHIFTS:
            model += pulp.lpSum(x[s][sh] for s in STAFF if (s, sh) in allowed) >= SHIFT_REQUIREMENTS.get(sh, 0)

        # Constraint: maximum hours per staff
        for s in STAFF:
            model += pulp.lpSum(x[s][sh] * SHIFT_DURATIONS[sh] for sh in SHIFTS if (s, sh) in allowed) <= STAFF_MAX_HOURS[s]

        # Constraint: enforce unavailability
        for s in STAFF:
            for sh in SHIFTS:
                if (s, sh) not in allowed:
                    model += x[s][sh] == 0

        # Constraint: at most 1 shift per person per day
        for s in STAFF:
            for d in DAYS:
                shifts = [f"{d}_AM", f"{d}_PM"]
                model += pulp.lpSum(x[s][sh] for sh in shifts if (s, sh) in allowed) <= 1

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
            return None

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

        for s in STAFF:
            assigned = [sh for sh in SHIFTS if (s, sh) in allowed and x[s][sh].value() == 1]
            hours = sum(SHIFT_DURATIONS[sh] for sh in assigned)
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
            "total_cost": cost,
            "assignments": assignments,
            "parameters": {
                "staff": STAFF,
                "shift_requirements": SHIFT_REQUIREMENTS,
                "staff_cost": STAFF_COST,
                "staff_max_hours": STAFF_MAX_HOURS
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
