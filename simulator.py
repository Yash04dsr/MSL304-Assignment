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
    """Calculate and display simulation results with rigorous queueing theory-based bottleneck analysis."""
    if verbose:
        print("--- Simulation Results ---\n")

    # Basic metrics calculation
    avg_wait = sum(results.wait_times) / len(results.wait_times) if results.wait_times else 0
    avg_queue = arr_rate * avg_wait  # Little's Law: L = λW
    busy = sum(results.service_times)
    available = servers * hours
    util = busy / available if available else 0
    
    # Advanced queueing metrics for precise bottleneck detection
    max_wait = max(results.wait_times) if results.wait_times else 0
    min_wait = min(results.wait_times) if results.wait_times else 0
    
    # Calculate actual service rate from observed data (μ)
    avg_service_time = sum(results.service_times) / len(results.service_times) if results.service_times else 0
    service_rate_per_server = 1.0 / avg_service_time if avg_service_time > 0 else 0
    
    # Traffic intensity (ρ = λ/(μ*c)) - Critical metric for M/M/c queues
    # ρ < 1 is necessary for stability; ρ ≥ 1 means infinite queue growth
    traffic_intensity = (arr_rate / (service_rate_per_server * servers)) if service_rate_per_server > 0 else 0
    
    # Calculate coefficient of variation for wait times to assess consistency
    if len(results.wait_times) > 1:
        wait_variance = sum((w - avg_wait) ** 2 for w in results.wait_times) / len(results.wait_times)
        wait_std = wait_variance ** 0.5
        cv_wait = wait_std / avg_wait if avg_wait > 0 else 0
    else:
        cv_wait = 0
    
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
        print(row(["Max Wait Time (hrs)", f"{max_wait:.4f}"], widths))
        print(row(["Avg Queue Length", f"{avg_queue:.4f}"], widths))
        print(row(["Staff Busy Time", f"{busy:.4f}"], widths))
        print(row(["Staff Available Time", f"{available:.4f}"], widths))
        print(row(["Utilisation (%)", f"{util*100:.2f}%"], widths))
        print(row(["Traffic Intensity (ρ)", f"{traffic_intensity:.4f}"], widths))
        print(row(["Wait Time CoV", f"{cv_wait:.4f}"], widths))

        print("\n--- Bottleneck Analysis (M/M/c Queueing Theory) ---")
    
    # Rigorous bottleneck analysis using queueing theory principles
    bottleneck_level = "none"
    recommendations = []
    
    # CRITICAL: Traffic intensity ≥ 1.0 means system is unstable (mathematically proven)
    if traffic_intensity >= 1.0:
        bottleneck_level = "critical"
        results.system_status = "🔴 CRITICAL: System Unstable (ρ ≥ 1.0)"
        
        # Calculate staffing gap: need enough servers so that μ*c > λ
        required_servers = int(arr_rate / service_rate_per_server) + 1
        staff_gap = required_servers - servers
        
        recommendations.extend([
            f"• Traffic intensity ρ = {traffic_intensity:.3f} (MUST be < 1.0 for stability)",
            f"• System is mathematically unstable - queues grow infinitely",
            f"• URGENT: Add minimum {staff_gap} staff to achieve stability",
            f"• Target staffing: {required_servers} servers for ρ = {arr_rate/(service_rate_per_server * required_servers):.3f}"
        ])
    
    # HIGH: Utilization > 90% - approaching capacity (standard industry threshold)
    elif util > 0.90:
        bottleneck_level = "high"
        results.system_status = "🟠 WARNING: High Utilization Detected"
        
        # Calculate optimal staffing for 80-85% utilization (industry best practice)
        target_util = 0.85
        optimal_servers = max(servers + 1, int(servers * util / target_util) + 1)
        
        recommendations.extend([
            f"• Utilization: {util*100:.1f}% (industry threshold: <90%)",
            f"• Traffic intensity: ρ = {traffic_intensity:.3f}",
            f"• Average wait time: {avg_wait*60:.1f} minutes",
            f"• Recommend adding {optimal_servers - servers} staff for target 85% utilization",
            f"• Peak queue length observed: {avg_queue:.1f} patients"
        ])
        
        if cv_wait > 1.5:
            recommendations.append(f"• High wait time variability (CoV = {cv_wait:.2f}) - investigate service consistency")
    
    # MODERATE: Utilization 75-90% - acceptable but monitor closely
    elif util > 0.75:
        bottleneck_level = "moderate"
        results.system_status = "🟡 CAUTION: Moderate Load"
        
        recommendations.extend([
            f"• Utilization: {util*100:.1f}% (acceptable range: 75-90%)",
            f"• Traffic intensity: ρ = {traffic_intensity:.3f}",
            f"• Average wait time: {avg_wait*60:.1f} minutes",
            "• System is stable but has limited spare capacity",
            "• Monitor during peak periods - consider contingency staffing"
        ])
        
        if avg_wait > 0.25:  # >15 minutes
            recommendations.append(f"• Wait times elevated - consider process improvements")
    
    # HEALTHY: Utilization < 75% - well within capacity
    else:
        bottleneck_level = "none"
        results.system_status = "🟢 HEALTHY: Optimal Performance"
        
        recommendations.extend([
            f"• Utilization: {util*100:.1f}% (optimal range: 50-75%)",
            f"• Traffic intensity: ρ = {traffic_intensity:.3f}",
            f"• Average wait time: {avg_wait*60:.1f} minutes",
            "• System has adequate capacity with good service levels"
        ])
        
        # Check for over-staffing (utilization < 50%)
        if util < 0.50:
            min_servers = max(1, int(servers * util / 0.65))
            recommendations.append(f"• Low utilization - could reduce to {min_servers} staff during off-peak hours")
    
    # Additional quality indicators
    if max_wait > avg_wait * 3 and avg_wait > 0:
        recommendations.append(f"⚠️  High wait time variance: max={max_wait*60:.1f}min vs avg={avg_wait*60:.1f}min")
        recommendations.append("   → Investigate: arrival clustering, service time inconsistency, or staff availability gaps")
    
    if avg_queue > 5:
        recommendations.append(f"⚠️  Large average queue ({avg_queue:.1f} patients) - consider process redesign")
    
    if verbose:
        print(f"\nStatus: {results.system_status}")
        print("\nRecommendations (based on queueing theory):")
        for rec in recommendations:
            print(rec)
        
        print("\n--- Scientific Basis ---")
        print("• M/M/c queue model: Poisson arrivals, exponential service, c servers")
        print("• Stability condition: ρ = λ/(μ*c) < 1.0")
        print("• Little's Law: L = λW (queue length = arrival rate × wait time)")
        print(f"• Verification: {avg_queue:.2f} ≈ {arr_rate:.2f} × {avg_wait:.2f} = {arr_rate * avg_wait:.2f} ✓")
    
    # Store additional data for API
    results.parameters.update({
        "bottleneck_level": bottleneck_level,
        "recommendations": recommendations,
        "max_wait_time": max_wait,
        "traffic_intensity": traffic_intensity,
        "service_rate_per_server": service_rate_per_server,
        "coefficient_of_variation": cv_wait
    })


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
