import cv2
import numpy as np
from sklearn.ensemble import RandomForestClassifier

# Extract features from PCB image
def extract_features(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    mean = np.mean(gray)
    std = np.std(gray)

    edges = cv2.Canny(gray, 100, 200)
    edge_pixels = np.sum(edges > 0)

    bright_pixels = np.sum(gray > 200)
    dark_pixels = np.sum(gray < 50)

    return [mean, std, edge_pixels, bright_pixels, dark_pixels]


# Load training images
good = cv2.imread("good_pcb.jpg")
defect = cv2.imread("defect_pcb.jpg")

# Check images
if good is None or defect is None:
    print("Error: Check image names!")
    exit()

# Create training data
X = np.array([
    extract_features(good),
    extract_features(defect)
])

# Labels: 0 = GOOD, 1 = DEFECT
y = np.array([0, 1])

# Create Random Forest model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

# Train model
model.fit(X, y)

# Test PCB
test = cv2.imread("defect_pcb.jpg")
features = np.array([extract_features(test)])

# Prediction
prediction = model.predict(features)[0]

if prediction == 0:
    print("PCB STATUS: GOOD")
else:
    print("PCB STATUS: DEFECT")

print("Prediction completed using Random Forest.")