import inquirer
from simulator import run_simulation
from optimiser import run_optimisation


def prompt_for_simulator():
    print("\n--- Patient Flow Simulator ---\n")

    try:
        arrival_rate = float(input("Arrival rate (patients/hour): "))
        service_rate = float(input("Service rate (patients/hour per staff): "))
        num_servers = int(input("Number of staff: "))
        simulation_time = int(input("Simulation duration (hours): "))

        if min(arrival_rate, service_rate, num_servers, simulation_time) <= 0:
            print("Values must be greater than zero.")
            return

        print("\nRunning simulation...\n")
        run_simulation(arrival_rate, service_rate, num_servers, simulation_time)

    except ValueError:
        print("Invalid input. Enter numeric values.")
    except Exception as e:
        print(f"Error: {e}")


def main_menu():
    print("\n==============================")
    print("        MediFlow Suite")
    print("==============================\n")

    while True:
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
            break

        choice = answer["choice"]

        if choice == "Patient Flow Simulator":
            prompt_for_simulator()
            input("\nPress Enter to continue...")

        elif choice == "Staff Rota Optimiser":
            print("\nRunning optimiser...\n")
            run_optimisation()
            input("\nPress Enter to continue...")

        else:
            print("\nGoodbye.\n")
            break


if __name__ == "__main__":
    main_menu()


