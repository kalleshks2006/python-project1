
import random
import csv
from collections import deque
import heapq


# ============================================================
# 1. AUTOMATIC TEST SCENARIO GENERATION
# ============================================================

def generate_test_scenarios(number_of_scenarios=30):

    scenarios = []

    for i in range(number_of_scenarios):

        # Random ECU parameters
        temperature = random.randint(20, 140)
        voltage = round(random.uniform(7.0, 17.0), 2)
        rpm = random.randint(200, 9000)

        scenario = {
            "id": i + 1,
            "name": f"Test_Scenario_{i + 1}",
            "temperature": temperature,
            "voltage": voltage,
            "rpm": rpm
        }

        scenarios.append(scenario)

    return scenarios


# ============================================================
# 2. FAULT DETECTION
# ============================================================

def detect_fault(scenario):

    faults = []

    temperature = scenario["temperature"]
    voltage = scenario["voltage"]
    rpm = scenario["rpm"]

    # Temperature faults
    if temperature > 120:
        faults.append("CRITICAL OVER-TEMPERATURE")

    elif temperature > 100:
        faults.append("HIGH TEMPERATURE")

    # Voltage faults
    if voltage < 9:
        faults.append("CRITICAL LOW VOLTAGE")

    elif voltage < 11:
        faults.append("LOW VOLTAGE")

    if voltage > 15:
        faults.append("HIGH VOLTAGE")

    # RPM faults
    if rpm > 8000:
        faults.append("CRITICAL HIGH RPM")

    elif rpm > 6000:
        faults.append("HIGH RPM")

    if rpm < 500:
        faults.append("ABNORMAL LOW RPM")

    if len(faults) == 0:
        return ["NO FAULT"]

    return faults


# ============================================================
# 3. RISK / HEURISTIC CALCULATION
# ============================================================

def calculate_risk(scenario):

    temperature = scenario["temperature"]
    voltage = scenario["voltage"]
    rpm = scenario["rpm"]

    risk = 0

    # Temperature risk
    if temperature > 100:
        risk += (temperature - 100) * 2

    # Low voltage risk
    if voltage < 11:
        risk += (11 - voltage) * 10

    # High voltage risk
    if voltage > 15:
        risk += (voltage - 15) * 10

    # High RPM risk
    if rpm > 6000:
        risk += (rpm - 6000) / 100

    # Low RPM risk
    if rpm < 500:
        risk += (500 - rpm) / 50

    return round(risk, 2)


# ============================================================
# 4. BFS SEARCH
# ============================================================

def bfs_search(scenarios):

    print("\n================================")
    print("BREADTH FIRST SEARCH (BFS)")
    print("================================")

    queue = deque()

    visited = set()

    queue.append(0)

    visited.add(0)

    while queue:

        index = queue.popleft()

        scenario = scenarios[index]

        faults = detect_fault(scenario)

        print(
            f"Checking {scenario['name']} | "
            f"Temp={scenario['temperature']}°C | "
            f"Voltage={scenario['voltage']}V | "
            f"RPM={scenario['rpm']}"
        )

        if faults != ["NO FAULT"]:

            print("FAULT FOUND:", faults)

            return scenario

        next_index = index + 1

        if next_index < len(scenarios):

            if next_index not in visited:

                queue.append(next_index)

                visited.add(next_index)

    return None


# ============================================================
# 5. GREEDY BEST-FIRST SEARCH
# ============================================================

def greedy_best_first_search(scenarios):

    print("\n================================")
    print("GREEDY BEST-FIRST SEARCH")
    print("================================")

    priority_queue = []

    for index, scenario in enumerate(scenarios):

        risk = calculate_risk(scenario)

        # Negative risk means highest risk comes first
        heapq.heappush(
            priority_queue,
            (-risk, index)
        )

    while priority_queue:

        negative_risk, index = heapq.heappop(priority_queue)

        scenario = scenarios[index]

        faults = detect_fault(scenario)

        risk = calculate_risk(scenario)

        print(
            f"Checking {scenario['name']} | "
            f"Risk={risk}"
        )

        if faults != ["NO FAULT"]:

            print("FAULT FOUND:", faults)

            return scenario

    return None


# ============================================================
# 6. A* SEARCH
# ============================================================

def a_star_search(scenarios):

    print("\n================================")
    print("A* SEARCH")
    print("================================")

    priority_queue = []

    for index, scenario in enumerate(scenarios):

        # g(n) = path/search cost
        g = index

        # h(n) = estimated fault risk
        h = calculate_risk(scenario)

        # f(n) = g(n) + h(n)
        f = g + h

        heapq.heappush(
            priority_queue,
            (f, index)
        )

    while priority_queue:

        f, index = heapq.heappop(priority_queue)

        scenario = scenarios[index]

        faults = detect_fault(scenario)

        print(
            f"Checking {scenario['name']} | "
            f"g={index} | "
            f"h={calculate_risk(scenario)} | "
            f"f={f:.2f}"
        )

        if faults != ["NO FAULT"]:

            print("FAULT FOUND:", faults)

            return scenario

    return None


# ============================================================
# 7. SAVE DATASET TO CSV
# ============================================================

def save_to_csv(scenarios):

    filename = "ecu_test_scenarios.csv"

    with open(
        filename,
        "w",
        newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "Scenario_ID",
            "Scenario_Name",
            "Temperature_C",
            "Voltage_V",
            "RPM",
            "Risk_Score",
            "Fault"
        ])

        for scenario in scenarios:

            risk = calculate_risk(scenario)

            faults = detect_fault(scenario)

            writer.writerow([
                scenario["id"],
                scenario["name"],
                scenario["temperature"],
                scenario["voltage"],
                scenario["rpm"],
                risk,
                ", ".join(faults)
            ])

    print("\nDataset saved as:", filename)


# ============================================================
# 8. COMPLETE VALIDATION REPORT
# ============================================================

def validation_report(scenarios):

    print("\n\n")
    print("======================================================")
    print("          ECU VALIDATION TEST REPORT")
    print("======================================================")

    for scenario in scenarios:

        risk = calculate_risk(scenario)

        faults = detect_fault(scenario)

        print("\n----------------------------------------")

        print("Scenario ID :", scenario["id"])

        print("Scenario    :", scenario["name"])

        print(
            "Temperature :",
            scenario["temperature"],
            "°C"
        )

        print(
            "Voltage     :",
            scenario["voltage"],
            "V"
        )

        print(
            "RPM         :",
            scenario["rpm"]
        )

        print(
            "Risk Score  :",
            risk
        )

        print(
            "Fault       :",
            ", ".join(faults)
        )


# ============================================================
# 9. MAIN PROGRAM
# ============================================================

print("======================================================")
print(" AI-BASED ECU TEST SCENARIO GENERATION")
print(" AND FAULT DETECTION")
print("======================================================")

# Generate 30 scenarios automatically

scenarios = generate_test_scenarios(30)

print("\n30 ECU test scenarios generated automatically.")

# Display generated scenarios

print("\nGenerated Test Scenarios:")

for scenario in scenarios:

    print(
        f"{scenario['id']:02d} | "
        f"Temp={scenario['temperature']}°C | "
        f"Voltage={scenario['voltage']}V | "
        f"RPM={scenario['rpm']}"
    )


# Save dataset

save_to_csv(scenarios)


# Run BFS

bfs_result = bfs_search(scenarios)


# Run Greedy Best First Search

greedy_result = greedy_best_first_search(scenarios)


# Run A*

astar_result = a_star_search(scenarios)


# Complete report

validation_report(scenarios)


# ============================================================
# FINAL RESULTS
# ============================================================

print("\n\n======================================================")
print("                 FINAL RESULTS")
print("======================================================")

if bfs_result:

    print(
        "BFS detected fault in:",
        bfs_result["name"]
    )

if greedy_result:

    print(
        "Greedy detected fault in:",
        greedy_result["name"]
    )

if astar_result:

    print(
        "A* detected fault in:",
        astar_result["name"]
    )

print("\nECU validation completed successfully.")

