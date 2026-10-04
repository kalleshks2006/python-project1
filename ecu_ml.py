import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

# ============================================================
# 1. GENERATE ECU DATASET
# ============================================================

np.random.seed(42)

number_of_samples = 500

temperature = np.random.randint(20, 141, number_of_samples)
voltage = np.round(np.random.uniform(7.0, 17.0, number_of_samples), 2)
rpm = np.random.randint(500, 9001, number_of_samples)

# ============================================================
# 2. CREATE FAULT LABEL
# ============================================================
# Fault conditions:
# Temperature > 120°C
# Voltage < 9V or Voltage > 16V
# RPM > 8000

fault = (
    (temperature > 120) |
    (voltage < 9) |
    (voltage > 16) |
    (rpm > 8000)
).astype(int)

# Create DataFrame
data = pd.DataFrame({
    "Temperature": temperature,
    "Voltage": voltage,
    "RPM": rpm,
    "Fault": fault
})

print("ECU Dataset:")
print(data.head(10))

# ============================================================
# 3. SEPARATE INPUT AND OUTPUT
# ============================================================

X = data[["Temperature", "Voltage", "RPM"]]
y = data["Fault"]

# ============================================================
# 4. SPLIT DATA INTO TRAINING AND TESTING
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

# ============================================================
# 5. FEATURE SCALING
# ============================================================

scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ============================================================
# 6. TRAIN LOGISTIC REGRESSION MODEL
# ============================================================

model = LogisticRegression()

model.fit(X_train_scaled, y_train)

# ============================================================
# 7. PREDICT ECU FAULTS
# ============================================================

y_pred = model.predict(X_test_scaled)

# ============================================================
# 8. MODEL EVALUATION
# ============================================================

accuracy = accuracy_score(y_test, y_pred)

print("\nModel Accuracy:", round(accuracy * 100, 2), "%")

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# ============================================================
# 9. TEST A NEW ECU CONDITION
# ============================================================

new_ecu = pd.DataFrame({
    "Temperature": [125],
    "Voltage": [12.5],
    "RPM": [7000]
})

new_ecu_scaled = scaler.transform(new_ecu)

prediction = model.predict(new_ecu_scaled)
probability = model.predict_proba(new_ecu_scaled)

print("\nNew ECU Condition:")
print(new_ecu)

if prediction[0] == 1:
    print("Prediction: ECU FAULT DETECTED")
else:
    print("Prediction: ECU NORMAL")

print("Fault Probability:",
      round(probability[0][1] * 100, 2), "%")