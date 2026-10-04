import tensorflow as tf
from tensorflow.keras import layers, models

# Load images from dataset
data = tf.keras.utils.image_dataset_from_directory(
    "dataset",
    image_size=(128, 128),
    batch_size=32,
    label_mode="binary"
)

# Normalize pixels: 0-255 -> 0-1
data = data.map(lambda x, y: (x / 255.0, y))

# CNN model
model = models.Sequential([
    layers.Conv2D(16, (3, 3), activation="relu",
                  input_shape=(128, 128, 3)),
    layers.MaxPooling2D(),

    layers.Conv2D(32, (3, 3), activation="relu"),
    layers.MaxPooling2D(),

    layers.Flatten(),

    layers.Dense(32, activation="relu"),
    layers.Dense(1, activation="sigmoid")
])

# Prepare model
model.compile(
    optimizer="adam",
    loss="binary_crossentropy",
    metrics=["accuracy"]
)

# Train
print("Training CNN...")
model.fit(data, epochs=5)

# Save model
model.save("pcb_cnn_model.keras")

print("Training completed!")