import simpy
import random

ALL_WAIT_TIMES = []
ALL_SERVICE_TIMES = []
TOTAL_PATIENTS_SERVED = 0


def row(cols, widths):
    return " | ".join(str(col).ljust(w) for col, w in zip(cols, widths))


def line(widths):
    total = sum(widths) + 3 * (len(widths) - 1)
    return "-" * total


class Clinic:
    def __init__(self, env, servers, arrival_rate, service_rate):
        self.env = env
        self.staff = simpy.Resource(env, capacity=servers)
        self.arrival_rate = arrival_rate
        self.service_rate = service_rate

    def patient_process(self, name):
        global TOTAL_PATIENTS_SERVED

        arrival = self.env.now
        print(f"{arrival:.4f}: Patient {name} arrives")

        with self.staff.request() as req:
            yield req
            start = self.env.now
            wait = start - arrival
            ALL_WAIT_TIMES.append(wait)
            print(f"{start:.4f}: Patient {name} begins service (wait {wait:.4f})")

            service_time = random.expovariate(self.service_rate)
            ALL_SERVICE_TIMES.append(service_time)

            yield self.env.timeout(service_time)

            end = self.env.now
            TOTAL_PATIENTS_SERVED += 1
            print(f"{end:.4f}: Patient {name} leaves")

    def generator(self):
        pid = 0
        while True:
            inter = random.expovariate(self.arrival_rate)
            yield self.env.timeout(inter)
            pid += 1
            self.env.process(self.patient_process(pid))


def run_simulation(arrival_rate, service_rate, servers, hours):
    ALL_WAIT_TIMES.clear()
    ALL_SERVICE_TIMES.clear()
    global TOTAL_PATIENTS_SERVED
    TOTAL_PATIENTS_SERVED = 0

    random.seed(42)
    env = simpy.Environment()
    clinic = Clinic(env, servers, arrival_rate, service_rate)
    env.process(clinic.generator())

    print(f"--- Patient Flow Simulation ---")
    print(f"Arrival={arrival_rate}/hr  Service={service_rate}/hr  Servers={servers}\n")

    env.run(until=hours)
    print(f"\nSimulation Finished ({hours} hrs)\n")

    return calculate_results(arrival_rate, servers, hours)


def calculate_results(arr_rate, servers, hours):
    print("--- Simulation Results ---\n")

    avg_wait = sum(ALL_WAIT_TIMES) / len(ALL_WAIT_TIMES) if ALL_WAIT_TIMES else 0
    avg_queue = arr_rate * avg_wait
    busy = sum(ALL_SERVICE_TIMES)
    available = servers * hours
    util = busy / available if available else 0

    headers = ["Metric", "Value"]
    widths = [26, 18]

    print(row(headers, widths))
    print(line(widths))

    print(row(["Patients Served", TOTAL_PATIENTS_SERVED], widths))
    print(row(["Average Wait (hrs)", f"{avg_wait:.4f}"], widths))
    print(row(["Avg Queue Length", f"{avg_queue:.4f}"], widths))
    print(row(["Staff Busy Time", f"{busy:.4f}"], widths))
    print(row(["Staff Available Time", f"{available:.4f}"], widths))
    print(row(["Utilisation (%)", f"{util*100:.2f}%"], widths))

    print("\nSystem Check:")
    if util > 1:
        print("System unstable — more staff required.")
    elif util > 0.9:
        print("High utilisation — likely bottleneck.")
    else:
        print("System operating within limits.")

    return {
        "avg_wait_time": avg_wait,
        "avg_queue_length": avg_queue,
        "utilization": util,
    }


if __name__ == "__main__":
    run_simulation(10, 4, 3, 50)
