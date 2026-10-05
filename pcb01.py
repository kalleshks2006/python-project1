"""Beginner-friendly CNN for checking component placement in board images.

Put training photos into this folder structure (folder names are the labels):

    component_images/
        correct/
        incorrect/

Train the model:
    python component_placement_cnn.py train

Check a new image:
    python component_placement_cnn.py predict --image my_board.jpg

Install TensorFlow first:  pip install tensorflow

Use clear photos taken from a similar angle and distance. This example labels
the whole image; it does not draw boxes around individual components.
"""

import argparse
import json
from pathlib import Path

import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models


IMAGE_SIZE = (128, 128)
MODEL_FILE = "component_placement_model.keras"
LABELS_FILE = "component_placement_labels.json"
DATA_FOLDER = "component_images"


def make_model(number_of_labels):
    """Build a small CNN that predicts one label for the whole image."""
    model = models.Sequential([
        layers.Input(shape=(128, 128, 3)),
        layers.Rescaling(1.0 / 255),  # Change pixel values from 0-255 to 0-1

        layers.Conv2D(16, 3, activation="relu"),
        layers.MaxPooling2D(),
        layers.Conv2D(32, 3, activation="relu"),
        layers.MaxPooling2D(),
        layers.Conv2D(64, 3, activation="relu"),
        layers.MaxPooling2D(),

        layers.Flatten(),
        layers.Dense(64, activation="relu"),
        layers.Dense(number_of_labels, activation="softmax"),
    ])

    model.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def train_model():
    """Load labeled photos, train the CNN, and save the model."""
    if not Path(DATA_FOLDER).is_dir():
        raise SystemExit(
            f"Could not find '{DATA_FOLDER}'. Create it with 'correct' and "
            "'incorrect' subfolders, then add photos."
        )

    # Load the same folders twice so Keras makes matching training and
    # validation sets. Folder names become the image labels automatically.
    training_images = tf.keras.utils.image_dataset_from_directory(
        DATA_FOLDER,
        validation_split=0.2,
        subset="training",
        seed=123,
        image_size=IMAGE_SIZE,
        batch_size=16,
        label_mode="int",
    )
    validation_images = tf.keras.utils.image_dataset_from_directory(
        DATA_FOLDER,
        validation_split=0.2,
        subset="validation",
        seed=123,
        image_size=IMAGE_SIZE,
        batch_size=16,
        label_mode="int",
    )

    class_names = training_images.class_names
    if len(class_names) != 2:
        raise SystemExit(
            "Please use exactly two folders: 'correct' and 'incorrect'."
        )

    print("Labels (in prediction order):", class_names)
    model = make_model(len(class_names))
    model.summary()
    model.fit(training_images, validation_data=validation_images, epochs=10)

    model.save(MODEL_FILE)
    Path(LABELS_FILE).write_text(json.dumps(class_names), encoding="utf-8")
    print(f"\nTraining finished. Model saved as {MODEL_FILE}")


def predict_image(image_path):
    """Predict whether one new board photo looks correctly placed."""
    if not Path(MODEL_FILE).is_file() or not Path(LABELS_FILE).is_file():
        raise SystemExit("Train the model first by running: python component_placement_cnn.py train")
    if not Path(image_path).is_file():
        raise SystemExit(f"Image not found: {image_path}")

    model = models.load_model(MODEL_FILE)
    class_names = json.loads(Path(LABELS_FILE).read_text(encoding="utf-8"))

    image = tf.keras.utils.load_img(image_path, target_size=IMAGE_SIZE)
    image_array = tf.keras.utils.img_to_array(image)
    image_array = np.expand_dims(image_array, axis=0)

    probabilities = model.predict(image_array, verbose=0)[0]
    best_index = int(np.argmax(probabilities))
    prediction = class_names[best_index]
    confidence = probabilities[best_index] * 100

    print(f"Prediction: {prediction}")
    print(f"Confidence: {confidence:.1f}%")
    if prediction == "incorrect":
        print("Check the component placement in this image.")


def main():
    parser = argparse.ArgumentParser(
        description="Train a simple CNN to classify component placement photos."
    )
    parser.add_argument("action", choices=["train", "predict"])
    parser.add_argument("--image", help="Image to check when using predict")
    args = parser.parse_args()

    if args.action == "train":
        train_model()
    elif args.action == "predict":
        if not args.image:
            parser.error("predict needs an image, for example: --image board.jpg")
        predict_image(args.image)


if __name__ == "__main__":
    main()
