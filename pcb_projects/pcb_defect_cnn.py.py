"""Train and use a CNN to classify PCB images by defect type.

Expected dataset layout (one folder per class):

    pcb_dataset/
        good/
        missing_hole/
        mouse_bite/
        open_circuit/
        short/

Train:    python pcb_defect_cnn.py train --data-dir pcb_dataset
Predict:  python pcb_defect_cnn.py predict --model pcb_defect_model.keras --image sample.png

Install dependencies with: pip install tensorflow
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import tensorflow as tf
import keras
from keras import layers


IMAGE_SIZE = (224, 224)
DEFAULT_BATCH_SIZE = 32


def build_model(number_of_classes: int) -> keras.Model:
    """Create a compact CNN for PCB image classification."""
    model = keras.Sequential(
        [
            layers.Input(shape=(*IMAGE_SIZE, 3)),
            layers.Rescaling(1.0 / 255),
            layers.Conv2D(32, 3, padding="same", activation="relu"),
            layers.BatchNormalization(),
            layers.MaxPooling2D(),
            layers.Conv2D(64, 3, padding="same", activation="relu"),
            layers.BatchNormalization(),
            layers.MaxPooling2D(),
            layers.Conv2D(128, 3, padding="same", activation="relu"),
            layers.BatchNormalization(),
            layers.MaxPooling2D(),
            layers.Conv2D(256, 3, padding="same", activation="relu"),
            layers.GlobalAveragePooling2D(),
            layers.Dropout(0.4),
            layers.Dense(128, activation="relu"),
            layers.Dropout(0.3),
            layers.Dense(number_of_classes, activation="softmax"),
        ],
        name="pcb_defect_cnn",
    )
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-3),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def train(args: argparse.Namespace) -> None:
    data_dir = Path(args.data_dir)
    if not data_dir.is_dir():
        raise SystemExit(f"Dataset folder does not exist: {data_dir}")

    train_data = keras.utils.image_dataset_from_directory(
        data_dir,
        validation_split=args.validation_split,
        subset="training",
        seed=args.seed,
        image_size=IMAGE_SIZE,
        batch_size=args.batch_size,
        label_mode="int",
    )
    validation_data = keras.utils.image_dataset_from_directory(
        data_dir,
        validation_split=args.validation_split,
        subset="validation",
        seed=args.seed,
        image_size=IMAGE_SIZE,
        batch_size=args.batch_size,
        label_mode="int",
    )

    class_names = train_data.class_names
    if len(class_names) < 2:
        raise SystemExit("Add at least two class folders (for example, good and defective).")

    autotune = tf.data.AUTOTUNE
    train_data = train_data.cache().shuffle(1000).prefetch(buffer_size=autotune)
    validation_data = validation_data.cache().prefetch(buffer_size=autotune)

    model = build_model(len(class_names))
    model.summary()
    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=5, restore_best_weights=True
        ),
        keras.callbacks.ModelCheckpoint(
            args.model,
            monitor="val_loss",
            save_best_only=True,
        ),
    ]
    model.fit(
        train_data,
        validation_data=validation_data,
        epochs=args.epochs,
        callbacks=callbacks,
    )

    # Save the final best weights even if training stopped before a checkpoint.
    model.save(args.model)
    labels_path = Path(args.model).with_suffix(".labels.json")
    labels_path.write_text(json.dumps(class_names, indent=2), encoding="utf-8")
    print(f"Model saved to: {args.model}")
    print(f"Class labels saved to: {labels_path}")


def predict(args: argparse.Namespace) -> None:
    model_path = Path(args.model)
    image_path = Path(args.image)
    labels_path = Path(args.labels) if args.labels else model_path.with_suffix(".labels.json")
    for path in (model_path, image_path, labels_path):
        if not path.is_file():
            raise SystemExit(f"File not found: {path}")

    model = keras.models.load_model(model_path)
    class_names = json.loads(labels_path.read_text(encoding="utf-8"))
    image = keras.utils.load_img(image_path, target_size=IMAGE_SIZE, color_mode="rgb")
    image_array = keras.utils.img_to_array(image)
    probabilities = model.predict(np.expand_dims(image_array, axis=0), verbose=0)[0]
    best_index = int(np.argmax(probabilities))

    print(f"Prediction: {class_names[best_index]}")
    print(f"Confidence: {probabilities[best_index] * 100:.2f}%")
    print("Class probabilities:")
    for index in np.argsort(probabilities)[::-1]:
        print(f"  {class_names[index]}: {probabilities[index] * 100:.2f}%")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CNN-based PCB defect classification")
    commands = parser.add_subparsers(dest="command", required=True)

    train_parser = commands.add_parser("train", help="Train the CNN from class folders")
    train_parser.add_argument("--data-dir", default="pcb_dataset", help="Root dataset folder")
    train_parser.add_argument("--model", default="pcb_defect_model.keras", help="Output model path")
    train_parser.add_argument("--epochs", type=int, default=30)
    train_parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    train_parser.add_argument("--validation-split", type=float, default=0.2)
    train_parser.add_argument("--seed", type=int, default=42)
    train_parser.set_defaults(func=train)

    predict_parser = commands.add_parser("predict", help="Classify one PCB image")
    predict_parser.add_argument("--model", default="pcb_defect_model.keras")
    predict_parser.add_argument("--image", required=True, help="PCB image to classify")
    predict_parser.add_argument("--labels", help="Optional class-label JSON path")
    predict_parser.set_defaults(func=predict)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    arguments.func(arguments)
