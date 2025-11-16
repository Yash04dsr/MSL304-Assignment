import pulp

STAFF = ["Nurse_A", "Nurse_B", "Nurse_C", "Tech_D"]

STAFF_COST = {
    "Nurse_A": 20,
    "Nurse_B": 20,
    "Nurse_C": 22,
    "Tech_D": 15
}

STAFF_MAX_HOURS = {
    "Nurse_A": 40,
    "Nurse_B": 40,
    "Nurse_C": 30,
    "Tech_D": 40
}

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]
TIMES = ["AM", "PM"]
SHIFTS = [f"{d}_{t}" for d in DAYS for t in TIMES]

SHIFT_DURATIONS = {sh: 8 for sh in SHIFTS}

SHIFT_REQUIREMENTS = {
    "Mon_AM": 2, "Mon_PM": 1,
    "Tue_AM": 2, "Tue_PM": 2,
    "Wed_AM": 2, "Wed_PM": 1,
    "Thu_AM": 2, "Thu_PM": 2,
    "Fri_AM": 2, "Fri_PM": 1
}

STAFF_AVAILABILITY = {
    "Nurse_A": ["Mon_AM", "Tue_AM", "Wed_AM", "Thu_AM", "Fri_AM"],
    "Nurse_B": ["Mon_PM", "Tue_PM", "Wed_PM", "Thu_PM", "Fri_PM"],
    "Nurse_C": ["Mon_AM", "Tue_AM", "Wed_PM", "Thu_AM", "Fri_PM"],
    "Tech_D":  ["Mon_AM", "Mon_PM", "Tue_AM", "Tue_PM", "Wed_AM", "Thu_PM", "Fri_AM"]
}


def row(cols, widths):
    return " | ".join(str(col).ljust(w) for col, w in zip(cols, widths))


def line(widths):
    total = sum(widths) + 3 * (len(widths) - 1)
    return "-" * total


def run_optimisation():
    print("\n--- MediFlow Rota Optimiser ---\n")

    model = pulp.LpProblem("Staff_Scheduling", pulp.LpMinimize)
    x = pulp.LpVariable.dicts("Assign", (STAFF, SHIFTS), 0, 1, cat="Binary")

    allowed = [(s, sh) for s in STAFF for sh in STAFF_AVAILABILITY[s] if sh in SHIFTS]

    model += pulp.lpSum(x[s][sh] * STAFF_COST[s] * SHIFT_DURATIONS[sh] for s, sh in allowed)

    for sh in SHIFTS:
        model += pulp.lpSum(x[s][sh] for s in STAFF if (s, sh) in allowed) >= SHIFT_REQUIREMENTS[sh]

    for s in STAFF:
        model += pulp.lpSum(x[s][sh] * SHIFT_DURATIONS[sh] for sh in SHIFTS if (s, sh) in allowed) <= STAFF_MAX_HOURS[s]

    for s in STAFF:
        for sh in SHIFTS:
            if (s, sh) not in allowed:
                model += x[s][sh] == 0

    for s in STAFF:
        for d in DAYS:
            shifts = [f"{d}_AM", f"{d}_PM"]
            model += pulp.lpSum(x[s][sh] for sh in shifts if (s, sh) in allowed) <= 1

    model.solve()
    status = pulp.LpStatus[model.status]
    print(f"Status: {status}")

    if status != "Optimal":
        print("No optimal solution.")
        return

    cost = pulp.value(model.objective)
    print(f"\nMinimum Weekly Cost: ${cost:.2f}\n")

    print("Staff Assignments\n")

    headers = ["Staff", "Assigned Shifts", "Hours"]
    widths = [12, 40, 8]

    print(row(headers, widths))
    print(line(widths))

    for s in STAFF:
        assigned = [sh for sh in SHIFTS if (s, sh) in allowed and x[s][sh].value() == 1]
        hours = sum(SHIFT_DURATIONS[sh] for sh in assigned)
        shifts = ", ".join(assigned) if assigned else "-"
        print(row([s, shifts, hours], widths))


if __name__ == "__main__":
    run_optimisation()
