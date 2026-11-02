# ================================================================
# INDUSTRIAL ECU FAULT DETECTION AND SELF-DIAGNOSIS SYSTEM
#
# Modules:
# 1. Engine ECU
# 2. ABS ECU
# 3. Fuel Injector ECU
#
# Architecture:
# Rule-Based + Model-Based + Random Forest ML
# ================================================================

import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

np.random.seed(42)


# ================================================================
# 1. DIAGNOSTIC CONFIGURATION
# ================================================================

FAULT_CODES = {
    "NORMAL": "P0000",

    # Engine ECU
    "HIGH_TEMP": "P0217",
    "LOW_VOLTAGE": "P0562",
    "HIGH_RPM": "P0219",
    "LOW_RPM": "P0506",
    "SENSOR_DEVIATION": "P1001",

    # ABS ECU
    "WHEEL_SENSOR_FAULT": "C0035",
    "WHEEL_SPEED_MISMATCH": "C0040",
    "HIGH_BRAKE_PRESSURE": "C1001",

    # Fuel Injector ECU
    "INJECTOR_OPEN_CIRCUIT": "P0201",
    "INJECTOR_OVER_CURRENT": "P0202",
    "LOW_FUEL_PRESSURE": "P0087",
    "INJECTOR_PERFORMANCE_ANOMALY": "P0261"
}

ACTIONS = {
    "NORMAL": "No modeled fault detected",

    "HIGH_TEMP": "Inspect cooling system and temperature sensor",
    "LOW_VOLTAGE": "Inspect battery and charging system",
    "HIGH_RPM": "Inspect RPM sensor and engine operation",
    "LOW_RPM": "Inspect idle control and RPM sensor",
    "SENSOR_DEVIATION": "Check sensor calibration and wiring",

    "WHEEL_SENSOR_FAULT": "Inspect wheel speed sensor and wiring",
    "WHEEL_SPEED_MISMATCH": "Check wheel speed sensors and wheel condition",
    "HIGH_BRAKE_PRESSURE": "Inspect brake pressure sensor and hydraulic system",

    "INJECTOR_OPEN_CIRCUIT": "Inspect injector wiring and electrical circuit",
    "INJECTOR_OVER_CURRENT": "Inspect injector coil and driver circuit",
    "LOW_FUEL_PRESSURE": "Inspect fuel pump, filter and fuel supply",
    "INJECTOR_PERFORMANCE_ANOMALY": "Inspect injector operation and fuel delivery"
}


# ================================================================
# 2. GENERATE SIMULATED ENGINE DATASET
# ================================================================

def generate_engine_data(n=4000):

    data = []

    for _ in range(n):

        temp = np.random.normal(85, 8)
        voltage = np.random.normal(13.2, 0.4)
        rpm = np.random.uniform(800, 4500)

        fault = "NORMAL"

        mode = np.random.choice([
            "NORMAL",
            "HIGH_TEMP",
            "LOW_VOLTAGE",
            "HIGH_RPM",
            "LOW_RPM",
            "SENSOR_DEVIATION"
        ])

        if mode == "HIGH_TEMP":
            temp = np.random.uniform(101, 120)
            fault = "HIGH_TEMP"

        elif mode == "LOW_VOLTAGE":
            voltage = np.random.uniform(10, 11.9)
            fault = "LOW_VOLTAGE"

        elif mode == "HIGH_RPM":
            rpm = np.random.uniform(5001, 6000)
            fault = "HIGH_RPM"

        elif mode == "LOW_RPM":
            rpm = np.random.uniform(400, 799)
            fault = "LOW_RPM"

        elif mode == "SENSOR_DEVIATION":
            temp = np.random.uniform(50, 69)
            fault = "SENSOR_DEVIATION"

        data.append([temp, voltage, rpm, fault])

    return pd.DataFrame(data, columns=[
        "temperature", "voltage", "rpm", "fault"
    ])


# ================================================================
# 3. GENERATE SIMULATED ABS DATASET
# ================================================================

def generate_abs_data(n=4000):

    data = []

    for _ in range(n):

        # Common vehicle speed with small wheel variations
        speed = np.random.uniform(20, 100)

        fl = speed + np.random.normal(0, 1)
        fr = speed + np.random.normal(0, 1)
        rl = speed + np.random.normal(0, 1)
        rr = speed + np.random.normal(0, 1)

        pressure = np.random.uniform(20, 70)

        fault = "NORMAL"

        mode = np.random.choice([
            "NORMAL",
            "WHEEL_SENSOR_FAULT",
            "WHEEL_SPEED_MISMATCH",
            "HIGH_BRAKE_PRESSURE"
        ])

        if mode == "WHEEL_SENSOR_FAULT":
            rr = 0
            fault = "WHEEL_SENSOR_FAULT"

        elif mode == "WHEEL_SPEED_MISMATCH":
            rr = speed - 35
            fault = "WHEEL_SPEED_MISMATCH"

        elif mode == "HIGH_BRAKE_PRESSURE":
            pressure = np.random.uniform(91, 100)
            fault = "HIGH_BRAKE_PRESSURE"

        data.append([fl, fr, rl, rr, pressure, fault])

    return pd.DataFrame(data, columns=[
        "FL", "FR", "RL", "RR", "BrakePressure", "fault"
    ])


# ================================================================
# 4. GENERATE SIMULATED FUEL INJECTOR DATASET
# ================================================================

def generate_injector_data(n=4000):

    data = []

    for _ in range(n):

        current = np.random.normal(1.5, 0.2)
        pulse = np.random.uniform(4, 15)
        pressure = np.random.normal(3.2, 0.3)

        fault = "NORMAL"

        mode = np.random.choice([
            "NORMAL",
            "INJECTOR_OPEN_CIRCUIT",
            "INJECTOR_OVER_CURRENT",
            "LOW_FUEL_PRESSURE",
            "INJECTOR_PERFORMANCE_ANOMALY"
        ])

        if mode == "INJECTOR_OPEN_CIRCUIT":
            current = np.random.uniform(0, 0.3)
            fault = "INJECTOR_OPEN_CIRCUIT"

        elif mode == "INJECTOR_OVER_CURRENT":
            current = np.random.uniform(2.6, 4)
            fault = "INJECTOR_OVER_CURRENT"

        elif mode == "LOW_FUEL_PRESSURE":
            pressure = np.random.uniform(0.5, 1.9)
            fault = "LOW_FUEL_PRESSURE"

        elif mode == "INJECTOR_PERFORMANCE_ANOMALY":
            pulse = np.random.uniform(18.1, 25)
            fault = "INJECTOR_PERFORMANCE_ANOMALY"

        data.append([current, pulse, pressure, fault])

    return pd.DataFrame(data, columns=[
        "Current", "PulseWidth", "FuelPressure", "fault"
    ])


# ================================================================
# 5. TRAIN RANDOM FOREST MODELS
# ================================================================

def train_model(df, features):

    X = df[features]
    y = df["fault"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=150,
        max_depth=12,
        random_state=42,
        class_weight="balanced"
    )

    model.fit(X_train, y_train)

    prediction = model.predict(X_test)

    accuracy = accuracy_score(y_test, prediction)

    print(f"Model accuracy: {accuracy * 100:.2f}%")

    return model


# Train all three ML models
print("\nTRAINING ENGINE ECU MODEL")
engine_df = generate_engine_data()

engine_model = train_model(
    engine_df,
    ["temperature", "voltage", "rpm"]
)

print("\nTRAINING ABS ECU MODEL")
abs_df = generate_abs_data()

abs_model = train_model(
    abs_df,
    ["FL", "FR", "RL", "RR", "BrakePressure"]
)

print("\nTRAINING FUEL INJECTOR MODEL")
injector_df = generate_injector_data()

injector_model = train_model(
    injector_df,
    ["Current", "PulseWidth", "FuelPressure"]
)


# ================================================================
# 6. COMMON DIAGNOSTIC REPORT FUNCTION
# ================================================================

def diagnostic_report(system, inputs, ml_fault, rules, deviations, confidence):

    detected = set(rules)

    # Add ML prediction
    if ml_fault != "NORMAL":
        detected.add(ml_fault)

    # If no fault is detected
    if not detected:
        detected.add("NORMAL")

    # Severity classification
    if "HIGH_TEMP" in detected:
        severity = "CRITICAL"

    elif "INJECTOR_OVER_CURRENT" in detected:
        severity = "HIGH"

    elif "LOW_VOLTAGE" in detected:
        severity = "HIGH"

    elif "WHEEL_SENSOR_FAULT" in detected:
        severity = "HIGH"

    elif any(f != "NORMAL" for f in detected):
        severity = "MEDIUM"

    else:
        severity = "LOW"

    print("\n" + "=" * 55)
    print(f"       {system} DIAGNOSTIC REPORT")
    print("=" * 55)

    for name, value in inputs.items():
        print(f"{name}: {value}")

    print("\nML Prediction:", ml_fault)
    print(f"ML Confidence: {confidence:.2f}%")

    print("\nRule-Based Findings:")
    print(rules if rules else "No threshold fault")

    print("\nModel-Based Deviations:")
    print(deviations if deviations else "No large deviation")

    print("\nDetected Faults:")

    for fault in sorted(detected):

        print("\nFault:", fault)
        print("DTC:", FAULT_CODES.get(fault, "UNKNOWN"))
        print("Action:", ACTIONS.get(fault, "Inspect system"))

    print("\nSeverity:", severity)

    if detected == {"NORMAL"}:
        print("System Status: NORMAL")
    else:
        print("System Status: FAULT DETECTED")

    print("=" * 55)

    return {
        "system": system,
        "faults": sorted(detected),
        "severity": severity,
        "ml_prediction": ml_fault,
        "confidence": confidence
    }


# ================================================================
# 7. ENGINE ECU SELF-DIAGNOSIS
# ================================================================

def diagnose_engine(temp, voltage, rpm):

    X = pd.DataFrame(
        [[temp, voltage, rpm]],
        columns=["temperature", "voltage", "rpm"]
    )

    ml_fault = engine_model.predict(X)[0]
    confidence = max(engine_model.predict_proba(X)[0]) * 100

    rules = []
    deviations = []

    # Rule-based diagnosis
    if temp > 100:
        rules.append("HIGH_TEMP")

    if voltage < 12:
        rules.append("LOW_VOLTAGE")

    if rpm > 5000:
        rules.append("HIGH_RPM")

    if rpm < 800:
        rules.append("LOW_RPM")

    if temp < 70:
        rules.append("SENSOR_DEVIATION")

    # Model-based deviations
    if abs(temp - 85) > 15:
        deviations.append("Temperature deviation")

    if abs(voltage - 13.2) > 1:
        deviations.append("Voltage deviation")

    if abs(rpm - 2500) > 1500:
        deviations.append("RPM deviation")

    return diagnostic_report(
        "ENGINE ECU",
        {
            "Temperature": f"{temp} C",
            "Voltage": f"{voltage} V",
            "RPM": rpm
        },
        ml_fault, rules, deviations, confidence
    )


# ================================================================
# 8. ABS ECU SELF-DIAGNOSIS
# ================================================================

def diagnose_abs(fl, fr, rl, rr, pressure):

    X = pd.DataFrame(
        [[fl, fr, rl, rr, pressure]],
        columns=["FL", "FR", "RL", "RR", "BrakePressure"]
    )

    ml_fault = abs_model.predict(X)[0]
    confidence = max(abs_model.predict_proba(X)[0]) * 100

    rules = []
    deviations = []

    speeds = [fl, fr, rl, rr]

    # Rule-based diagnosis
    if min(speeds) < 5:
        rules.append("WHEEL_SENSOR_FAULT")

    if max(speeds) - min(speeds) > 25:
        rules.append("WHEEL_SPEED_MISMATCH")

    if pressure > 90:
        rules.append("HIGH_BRAKE_PRESSURE")

    # Model-based wheel speed comparison
    average_speed = np.mean(speeds)

    for speed in speeds:
        if abs(speed - average_speed) > 20:
            deviations.append("Wheel speed deviation")

    return diagnostic_report(
        "ABS ECU",
        {
            "FL Speed": fl,
            "FR Speed": fr,
            "RL Speed": rl,
            "RR Speed": rr,
            "Brake Pressure": f"{pressure} bar"
        },
        ml_fault, rules, deviations, confidence
    )


# ================================================================
# 9. FUEL INJECTOR SELF-DIAGNOSIS
# ================================================================

def diagnose_injector(current, pulse_width, pressure):

    X = pd.DataFrame(
        [[current, pulse_width, pressure]],
        columns=["Current", "PulseWidth", "FuelPressure"]
    )

    ml_fault = injector_model.predict(X)[0]
    confidence = max(injector_model.predict_proba(X)[0]) * 100

    rules = []
    deviations = []

    # Rule-based diagnosis
    if current < 0.5:
        rules.append("INJECTOR_OPEN_CIRCUIT")

    if current > 2.5:
        rules.append("INJECTOR_OVER_CURRENT")

    if pressure < 2:
        rules.append("LOW_FUEL_PRESSURE")

    if pulse_width > 18:
        rules.append("INJECTOR_PERFORMANCE_ANOMALY")

    # Model-based deviations
    if abs(current - 1.5) > 0.7:
        deviations.append("Injector current deviation")

    if abs(pressure - 3.2) > 1:
        deviations.append("Fuel pressure deviation")

    if pulse_width > 18:
        deviations.append("Injector pulse deviation")

    return diagnostic_report(
        "FUEL INJECTOR ECU",
        {
            "Injector Current": f"{current} A",
            "Pulse Width": f"{pulse_width} ms",
            "Fuel Pressure": f"{pressure} bar"
        },
        ml_fault, rules, deviations, confidence
    )


# ================================================================
# 10. MAIN ECU TESTING SYSTEM
# ================================================================

if __name__ == "__main__":

    print("\nINDUSTRIAL ECU FAULT DETECTION SYSTEM")
    print("1. Engine ECU")
    print("2. ABS ECU")
    print("3. Fuel Injector ECU")
    print("4. Run All Systems")

    choice = input("\nSelect system (1-4): ")

    if choice == "1":

        diagnose_engine(110, 13.2, 2500)

    elif choice == "2":

        diagnose_abs(80, 82, 78, 0, 50)

    elif choice == "3":

        diagnose_injector(0.1, 10, 3.5)

    elif choice == "4":

        diagnose_engine(110, 13.2, 2500)

        diagnose_abs(80, 82, 78, 0, 50)

        diagnose_injector(0.1, 10, 3.5)

    else:

        print("Invalid selection")