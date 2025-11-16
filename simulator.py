import simpy
import random
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def row(cols, widths):
    return " | ".join(str(col).ljust(w) for col, w in zip(cols, widths))


def line(widths):
    total = sum(widths) + 3 * (len(widths) - 1)
    return "-" * total


class SimulationResults:
    """Container for simulation results with export capabilities."""
    
    def __init__(self):
        self.wait_times: List[float] = []
        self.service_times: List[float] = []
        self.patients_served: int = 0
        self.avg_wait_time: float = 0.0
        self.avg_queue_length: float = 0.0
        self.utilization: float = 0.0
        self.system_status: str = ""
        self.parameters: Dict = {}
        
    def to_dict(self) -> Dict:
        """Export results as dictionary."""
        return {
            "parameters": self.parameters,
            "metrics": {
                "patients_served": self.patients_served,
                "avg_wait_time": self.avg_wait_time,
                "avg_queue_length": self.avg_queue_length,
                "utilization": self.utilization,
                "system_status": self.system_status
            },
            "raw_data": {
                "wait_times": self.wait_times,
                "service_times": self.service_times
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def save_json(self, filepath: Path) -> None:
        """Save results to JSON file."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        logger.info(f"Results saved to {filepath}")


class Clinic:
    """Discrete-event simulation of a clinic with patient arrivals and service."""
    
    def __init__(self, env, servers, arrival_rate, service_rate, results: SimulationResults, verbose: bool = True):
        self.env = env
        self.staff = simpy.Resource(env, capacity=servers)
        self.arrival_rate = arrival_rate
        self.service_rate = service_rate
        self.results = results
        self.verbose = verbose

    def patient_process(self, name):
        """Simulate a single patient's journey through the clinic."""
        arrival = self.env.now
        if self.verbose:
            print(f"{arrival:.4f}: Patient {name} arrives")

        with self.staff.request() as req:
            yield req
            start = self.env.now
            wait = start - arrival
            self.results.wait_times.append(wait)
            if self.verbose:
                print(f"{start:.4f}: Patient {name} begins service (wait {wait:.4f})")

            service_time = random.expovariate(self.service_rate)
            self.results.service_times.append(service_time)

            yield self.env.timeout(service_time)

            end = self.env.now
            self.results.patients_served += 1
            if self.verbose:
                print(f"{end:.4f}: Patient {name} leaves")

    def generator(self):
        """Generate patient arrivals according to Poisson process."""
        pid = 0
        while True:
            inter = random.expovariate(self.arrival_rate)
            yield self.env.timeout(inter)
            pid += 1
            self.env.process(self.patient_process(pid))


def run_simulation(
    arrival_rate: float,
    service_rate: float,
    servers: int,
    hours: float,
    seed: Optional[int] = 42,
    verbose: bool = True,
    export_path: Optional[Path] = None
) -> Dict:
    """
    Run patient flow simulation.
    
    Args:
        arrival_rate: Patient arrival rate (patients/hour)
        service_rate: Service rate per staff (patients/hour)
        servers: Number of staff members
        hours: Simulation duration in hours
        seed: Random seed for reproducibility (None for random)
        verbose: Print detailed simulation events
        export_path: Path to export results JSON (None to skip export)
    
    Returns:
        Dictionary with simulation results
    """
    # Initialize results container
    results = SimulationResults()
    results.parameters = {
        "arrival_rate": arrival_rate,
        "service_rate": service_rate,
        "servers": servers,
        "hours": hours,
        "seed": seed
    }
    
    # Set random seed
    if seed is not None:
        random.seed(seed)
    
    # Create simulation environment
    env = simpy.Environment()
    clinic = Clinic(env, servers, arrival_rate, service_rate, results, verbose)
    env.process(clinic.generator())

    if verbose:
        print(f"--- Patient Flow Simulation ---")
        print(f"Arrival={arrival_rate}/hr  Service={service_rate}/hr  Servers={servers}\n")

    try:
        env.run(until=hours)
        if verbose:
            print(f"\nSimulation Finished ({hours} hrs)\n")
        logger.info(f"Simulation completed: {results.patients_served} patients served")
    except Exception as e:
        logger.error(f"Simulation error: {e}")
        raise

    # Calculate and store results
    calculate_results(results, arrival_rate, servers, hours, verbose)
    
    # Export if requested
    if export_path:
        results.save_json(export_path)
    
    return {
        "avg_wait_time": results.avg_wait_time,
        "avg_queue_length": results.avg_queue_length,
        "utilization": results.utilization,
        "patients_served": results.patients_served,
        "system_status": results.system_status
    }


def calculate_results(results: SimulationResults, arr_rate: float, servers: int, hours: float, verbose: bool = True):
    """Calculate and display simulation results."""
    if verbose:
        print("--- Simulation Results ---\n")

    avg_wait = sum(results.wait_times) / len(results.wait_times) if results.wait_times else 0
    avg_queue = arr_rate * avg_wait  # Little's Law
    busy = sum(results.service_times)
    available = servers * hours
    util = busy / available if available else 0
    
    # Store results
    results.avg_wait_time = avg_wait
    results.avg_queue_length = avg_queue
    results.utilization = util

    if verbose:
        headers = ["Metric", "Value"]
        widths = [26, 18]

        print(row(headers, widths))
        print(line(widths))

        print(row(["Patients Served", results.patients_served], widths))
        print(row(["Average Wait (hrs)", f"{avg_wait:.4f}"], widths))
        print(row(["Avg Queue Length", f"{avg_queue:.4f}"], widths))
        print(row(["Staff Busy Time", f"{busy:.4f}"], widths))
        print(row(["Staff Available Time", f"{available:.4f}"], widths))
        print(row(["Utilisation (%)", f"{util*100:.2f}%"], widths))

        print("\nSystem Check:")
    
    if util > 1:
        results.system_status = "Unstable - More staff required"
        if verbose:
            print("⚠️  System unstable — more staff required.")
    elif util > 0.9:
        results.system_status = "High utilization - Likely bottleneck"
        if verbose:
            print("⚠️  High utilisation — likely bottleneck.")
    else:
        results.system_status = "Operating within limits"
        if verbose:
            print("✓ System operating within limits.")


if __name__ == "__main__":
    # Example usage with export
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_path = Path(f"results/simulation_{timestamp}.json")
    
    results = run_simulation(
        arrival_rate=10,
        service_rate=4,
        servers=3,
        hours=50,
        export_path=export_path
    )
    
    print(f"\n✓ Results exported to: {export_path}")
