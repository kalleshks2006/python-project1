"""
AI-Based Adaptive Test Scenario Generation and Fault Detection
for ECU Validation

Educational simulation:
- Generates ECU test scenarios adaptively.
- Simulates ECU sensor responses.
- Detects abnormal behavior using Isolation Forest.
- Saves test results to CSV.
"""

import random
import numpy as np
import pandas as pd

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


# -----------------------------
# 1. ECU simulation
# -----------------------------
def simulate_ecu(scenario):
    """
    Simulates ECU output for one test scenario.

    Inputs:
        temperature: engine temperature in degree Celsius
        voltage: battery voltage
        rpm: engine speed

    Output:
        simulated ECU response values
    """

    temperature = scenario["temperature"]
    voltage = scenario["voltage"]
    rpm = scenario["rpm"]

    # Normal ECU response equations (simplified)
    expected_fuel = 2.0 + (rpm / 3000) + (temperature - 25) * 0.01
    expected_current = 2.0 + (rpm / 2000) + (12.0 - voltage) * 0.5

    # Random measurement noise
    fuel_injection = expected_fuel + np.random.normal(0, 0.08)
    current = expected_current + np.random.normal(0, 0.08)

    # Randomly inject a fault
    fault = random.random() < 0.15

    if fault:
        fault_type = random.choice([
            "fuel_injection_error",
            "over_current",
            "sensor_offset"
        ])

        if fault_type == "fuel_injection_error":
            fuel_injection += random.uniform(1.0, 2.0)

        elif fault_type == "over_current":
            current += random.uniform(1.5, 3.0)

        elif fault_type == "sensor_offset":
            temperature += random.uniform(15, 25)

    else:
        fault_type = "normal"

    return {
        "measured_temperature": temperature,
        "fuel_injection": fuel_injection,
        "current": current,
        "fault_label": fault_type
    }


# -----------------------------
# 2. Adaptive test generation
# -----------------------------
def generate_scenario(previous_results):
    """
    Generates a new test scenario.

    If recent tests contain faults, the generator focuses more
    on boundary conditions such as high temperature, low voltage,
    and high RPM.
    """

    if len(previous_results) == 0:
        risk_level = 0.0
    else:
        recent_results = previous_results[-10:]
        risk_level = sum(
            result["ai_fault_prediction"] == "FAULT"
            for result in recent_results
        ) / len(recent_results)

    # Increase boundary testing when fault risk increases
    if risk_level > 0.30:
        temperature = random.uniform(90, 130)
        voltage = random.uniform(9.0, 11.5)
        rpm = random.randint(3500, 6000)
        scenario_type = "adaptive_boundary_test"
    else:
        temperature = random.uniform(20, 100)
        voltage = random.uniform(10.5, 14.5)
        rpm = random.randint(800, 4500)
        scenario_type = "normal_random_test"

    return {
        "temperature": temperature,
        "voltage": voltage,
        "rpm": rpm,
        "scenario_type": scenario_type
    }


# -----------------------------
# 3. Build training data
# -----------------------------
def create_training_data(number_of_samples=500):
    """
    Creates mostly normal ECU behavior for AI model training.
    """

    data = []

    for _ in range(number_of_samples):
        temperature = random.uniform(20, 100)
        voltage = random.uniform(10.5, 14.5)
        rpm = random.randint(800, 4500)

        expected_fuel = 2.0 + (rpm / 3000) + (temperature - 25) * 0.01
        expected_current = 2.0 + (rpm / 2000) + (12.0 - voltage) * 0.5

        fuel_injection = expected_fuel + np.random.normal(0, 0.08)
        current = expected_current + np.random.normal(0, 0.08)

        data.append([
            temperature,
            voltage,
            rpm,
            fuel_injection,
            current
        ])

    return np.array(data)


# -----------------------------
# 4. Main validation process
# -----------------------------
def main():
    print("\nAI-Based Adaptive ECU Validation Started\n")

    # Train AI model using normal data
    training_data = create_training_data()

    scaler = StandardScaler()
    scaled_training_data = scaler.fit_transform(training_data)

    model = IsolationForest(
        contamination=0.15,
        random_state=42
    )

    model.fit(scaled_training_data)

    results = []

    number_of_tests = 50

    for test_number in range(1, number_of_tests + 1):

        # Generate an adaptive test scenario
        scenario = generate_scenario(results)

        # Simulate ECU response
        ecu_output = simulate_ecu(scenario)

        # Prepare data for AI prediction
        feature_row = [[
            ecu_output["measured_temperature"],
            scenario["voltage"],
            scenario["rpm"],
            ecu_output["fuel_injection"],
            ecu_output["current"]
        ]]

        scaled_feature_row = scaler.transform(feature_row)

        prediction = model.predict(scaled_feature_row)[0]
        anomaly_score = model.decision_function(scaled_feature_row)[0]

        if prediction == -1:
            ai_fault_prediction = "FAULT"
        else:
            ai_fault_prediction = "NORMAL"

        result = {
            "test_number": test_number,
            "temperature_input": round(scenario["temperature"], 2),
            "voltage_input": round(scenario["voltage"], 2),
            "rpm_input": scenario["rpm"],
            "scenario_type": scenario["scenario_type"],
            "measured_temperature": round(
                ecu_output["measured_temperature"], 2
            ),
            "fuel_injection": round(ecu_output["fuel_injection"], 2),
            "current": round(ecu_output["current"], 2),
            "actual_fault": ecu_output["fault_label"],
            "ai_fault_prediction": ai_fault_prediction,
            "anomaly_score": round(float(anomaly_score), 4)
        }

        results.append(result)

        print(
            f"Test {test_number:02d} | "
            f"{scenario['scenario_type']:22s} | "
            f"AI: {ai_fault_prediction:6s} | "
            f"Actual: {ecu_output['fault_label']}"
        )

    # Save results
    results_df = pd.DataFrame(results)
    results_df.to_csv("ecu_validation_results.csv", index=False)

    # Calculate simple performance statistics
    actual_faults = results_df["actual_fault"] != "normal"
    predicted_faults = results_df["ai_fault_prediction"] == "FAULT"

    correct_predictions = (actual_faults == predicted_faults).sum()
    accuracy = correct_predictions / len(results_df) * 100

    print("\n-----------------------------")
    print("Validation Completed")
    print("-----------------------------")
    print(f"Total tests: {len(results_df)}")
    print(f"Actual faults: {actual_faults.sum()}")
    print(f"AI predicted faults: {predicted_faults.sum()}")
    print(f"Approximate detection accuracy: {accuracy:.2f}%")
    print("\nResults saved to: ecu_validation_results.csv")


if __name__ == "__main__":
    main()
