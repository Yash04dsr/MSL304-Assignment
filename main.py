import inquirer
import argparse
import logging
from pathlib import Path
from datetime import datetime
from simulator import run_simulation
from optimiser import run_optimisation

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/mediflow.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def validate_positive(value: float, name: str) -> bool:
    """Validate that a value is positive."""
    if value <= 0:
        print(f"❌ {name} must be greater than zero.")
        return False
    return True


def prompt_for_simulator(auto_export: bool = False):
    print("\n--- Patient Flow Simulator ---\n")

    try:
        arrival_rate = float(input("Arrival rate (patients/hour): "))
        if not validate_positive(arrival_rate, "Arrival rate"):
            return
            
        service_rate = float(input("Service rate (patients/hour per staff): "))
        if not validate_positive(service_rate, "Service rate"):
            return
            
        num_servers = int(input("Number of staff: "))
        if not validate_positive(num_servers, "Number of staff"):
            return
            
        simulation_time = int(input("Simulation duration (hours): "))
        if not validate_positive(simulation_time, "Simulation duration"):
            return

        # Ask about export
        export_path = None
        if auto_export:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_path = Path(f"results/simulation_{timestamp}.json")
            print(f"✓ Results will be exported to: {export_path}\n")

        print("\nRunning simulation...\n")
        logger.info(f"Starting simulation: λ={arrival_rate}, μ={service_rate}, c={num_servers}, T={simulation_time}")
        
        run_simulation(
            arrival_rate=arrival_rate,
            service_rate=service_rate,
            servers=num_servers,
            hours=simulation_time,
            export_path=export_path
        )
        
        if export_path:
            print(f"\n✓ Results saved to: {export_path}")

    except ValueError:
        print("❌ Invalid input. Please enter numeric values.")
        logger.error("Invalid input in simulator")
    except KeyboardInterrupt:
        print("\n\n⚠️  Simulation cancelled by user.")
        logger.info("Simulation cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Simulation error: {e}", exc_info=True)


def prompt_for_optimiser(auto_export: bool = False):
    """Run the staff rota optimizer with optional export."""
    print("\nRunning optimiser...\n")
    
    try:
        export_path = None
        if auto_export:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_path = Path(f"results/optimisation_{timestamp}.json")
        
        logger.info("Starting optimization")
        results = run_optimisation(export_path=export_path)
        
        if results and export_path:
            print(f"\n✓ Results saved to: {export_path}")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Optimization cancelled by user.")
        logger.info("Optimization cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Optimization error: {e}", exc_info=True)


def main_menu(auto_export: bool = False):
    """
    Main interactive menu.
    
    Args:
        auto_export: Automatically export results to JSON files
    """
    print("\n==============================")
    print("        MediFlow Suite")
    print("==============================")
    if auto_export:
        print("  (Auto-export enabled)")
    print()

    while True:
        try:
            options = [
                inquirer.List(
                    "choice",
                    message="Choose an option:",
                    choices=[
                        "Patient Flow Simulator",
                        "Staff Rota Optimiser",
                        "Exit",
                    ],
                )
            ]

            answer = inquirer.prompt(options)
            if not answer:
                print("\nExiting.\n")
                logger.info("Application exited")
                break

            choice = answer["choice"]

            if choice == "Patient Flow Simulator":
                prompt_for_simulator(auto_export=auto_export)
                input("\nPress Enter to continue...")

            elif choice == "Staff Rota Optimiser":
                prompt_for_optimiser(auto_export=auto_export)
                input("\nPress Enter to continue...")

            else:
                print("\n👋 Goodbye!\n")
                logger.info("Application exited normally")
                break
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            logger.info("Application interrupted by user")
            break


if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    Path("logs").mkdir(exist_ok=True)
    Path("results").mkdir(exist_ok=True)
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="MediFlow Suite - Patient Flow and Staff Scheduling Optimization"
    )
    parser.add_argument(
        "--export",
        action="store_true",
        help="Automatically export results to JSON files"
    )
    parser.add_argument(
        "--simulator",
        action="store_true",
        help="Run simulator directly (non-interactive)"
    )
    parser.add_argument(
        "--optimiser",
        action="store_true",
        help="Run optimiser directly (non-interactive)"
    )
    parser.add_argument(
        "--arrival-rate",
        type=float,
        help="Arrival rate for simulator (patients/hour)"
    )
    parser.add_argument(
        "--service-rate",
        type=float,
        help="Service rate for simulator (patients/hour per staff)"
    )
    parser.add_argument(
        "--servers",
        type=int,
        help="Number of staff for simulator"
    )
    parser.add_argument(
        "--hours",
        type=float,
        help="Simulation duration (hours)"
    )
    
    args = parser.parse_args()
    
    logger.info("MediFlow Suite started")
    
    # Non-interactive modes
    if args.simulator:
        if all([args.arrival_rate, args.service_rate, args.servers, args.hours]):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_path = Path(f"results/simulation_{timestamp}.json") if args.export else None
            
            run_simulation(
                arrival_rate=args.arrival_rate,
                service_rate=args.service_rate,
                servers=args.servers,
                hours=args.hours,
                export_path=export_path
            )
        else:
            print("❌ Error: --simulator requires --arrival-rate, --service-rate, --servers, and --hours")
            
    elif args.optimiser:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_path = Path(f"results/optimisation_{timestamp}.json") if args.export else None
        run_optimisation(export_path=export_path)
        
    else:
        # Interactive mode
        main_menu(auto_export=args.export)


