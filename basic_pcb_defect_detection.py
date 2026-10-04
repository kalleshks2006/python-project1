"""Basic PCB defect detection with a binary CNN classifier.

Dataset layout (put images in the matching folder):

    pcb_dataset/
        good/
        defective/

Train:
    python basic_pcb_defect_detection.py train --data-dir pcb_dataset

Predict:
    python basic_pcb_defect_detection.py predict --image sample.png

Install:
    pip install tensorflow
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers


IMAGE_SIZE = (128, 128)
MODEL_PATH = Path("pcb_binary_model.keras")
LABELS_PATH = Path("pcb_binary_labels.json")


def build_model() -> keras.Model:
    """Build a small CNN that predicts good vs. defective PCB images."""
    model = keras.Sequential(
        [
            layers.Input(shape=(*IMAGE_SIZE, 3)),
            layers.Rescaling(1.0 / 255),
            layers.RandomRotation(0.05),
            layers.RandomZoom(0.1),
            layers.Conv2D(32, 3, padding="same", activation="relu"),
            layers.MaxPooling2D(),
            layers.Conv2D(64, 3, padding="same", activation="relu"),
            layers.MaxPooling2D(),
            layers.Conv2D(128, 3, padding="same", activation="relu"),
            layers.MaxPooling2D(),
            layers.GlobalAveragePooling2D(),
            layers.Dropout(0.3),
            layers.Dense(64, activation="relu"),
            layers.Dense(1, activation="sigmoid"),
        ],
        name="basic_pcb_defect_cnn",
    )
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-3),
        loss="binary_crossentropy",
        metrics=["accuracy"],
    )
    return model


def train(args: argparse.Namespace) -> None:
    data_dir = Path(args.data_dir)
    if not data_dir.is_dir():
        raise SystemExit(f"Dataset directory not found: {data_dir}")

    train_ds = keras.utils.image_dataset_from_directory(
        data_dir,
        class_names=["defective", "good"],
        validation_split=args.validation_split,
        subset="training",
        seed=args.seed,
        image_size=IMAGE_SIZE,
        batch_size=args.batch_size,
        label_mode="binary",
    )
    val_ds = keras.utils.image_dataset_from_directory(
        data_dir,
        class_names=["defective", "good"],
        validation_split=args.validation_split,
        subset="validation",
        seed=args.seed,
        image_size=IMAGE_SIZE,
        batch_size=args.batch_size,
        label_mode="binary",
    )

    # Cache and prefetch make image loading faster during training.
    autotune = tf.data.AUTOTUNE
    train_ds = train_ds.cache().shuffle(500).prefetch(autotune)
    val_ds = val_ds.cache().prefetch(autotune)

    model = build_model()
    model.summary()
    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=4, restore_best_weights=True
        ),
        keras.callbacks.ModelCheckpoint(
            args.model, monitor="val_loss", save_best_only=True
        ),
    ]
    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=args.epochs,
        callbacks=callbacks,
    )
    model.save(args.model)

    labels_path = Path(args.model).with_suffix(".labels.json")
    labels_path.write_text(json.dumps(["defective", "good"], indent=2), encoding="utf-8")
    print(f"Saved model: {args.model}")
    print(f"Saved labels: {labels_path}")


def predict(args: argparse.Namespace) -> None:
    model_path = Path(args.model)
    image_path = Path(args.image)
    labels_path = Path(args.labels) if args.labels else model_path.with_suffix(".labels.json")
    for path in (model_path, image_path, labels_path):
        if not path.is_file():
            raise SystemExit(f"File not found: {path}")

    model = keras.models.load_model(model_path)
    labels = json.loads(labels_path.read_text(encoding="utf-8"))
    image = keras.utils.load_img(image_path, target_size=IMAGE_SIZE, color_mode="rgb")
    image_array = keras.utils.img_to_array(image)
    # With class_names above, output 0 means defective and 1 means good.
    good_probability = float(
        model.predict(np.expand_dims(image_array, axis=0), verbose=0)[0][0]
    )
    probabilities = [1.0 - good_probability, good_probability]
    best_index = int(np.argmax(probabilities))
    print(f"Prediction: {labels[best_index]}")
    print(f"Confidence: {probabilities[best_index] * 100:.2f}%")
    print(f"Defective probability: {probabilities[0] * 100:.2f}%")
    print(f"Good probability: {probabilities[1] * 100:.2f}%")


def main() -> None:
    parser = argparse.ArgumentParser(description="Basic good/defective PCB image classifier")
    commands = parser.add_subparsers(dest="command", required=True)

    train_parser = commands.add_parser("train", help="Train from good/defective folders")
    train_parser.add_argument("--data-dir", default="pcb_dataset")
    train_parser.add_argument("--model", default=str(MODEL_PATH))
    train_parser.add_argument("--epochs", type=int, default=20)
    train_parser.add_argument("--batch-size", type=int, default=32)
    train_parser.add_argument("--validation-split", type=float, default=0.2)
    train_parser.add_argument("--seed", type=int, default=42)
    train_parser.set_defaults(func=train)

    predict_parser = commands.add_parser("predict", help="Classify one PCB image")
    predict_parser.add_argument("--model", default=str(MODEL_PATH))
    predict_parser.add_argument("--image", required=True)
    predict_parser.add_argument("--labels", help="Optional labels JSON path")
    predict_parser.set_defaults(func=predict)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
