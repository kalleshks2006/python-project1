"""Count vehicles and estimate their speed from a fixed highway camera.

The camera must be still and aimed at one lane/direction.  Measure the real
distance (in metres) between SPEED_LINE_1_Y and SPEED_LINE_2_Y on the road,
then set LINE_DISTANCE_METERS to that distance.  For reliable results, use a
camera view where the road is reasonably flat (or apply a perspective transform).

Example:
    python highway_vehicle_speed.py --input highway.mp4 --output result.mp4
    python highway_vehicle_speed.py --input 0
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass, field

import cv2

# --- Calibrate these values for your video ---
SPEED_LINE_1_Y = 300          # First horizontal line, in pixels
SPEED_LINE_2_Y = 450          # Second horizontal line, in pixels
COUNT_LINE_Y = 375            # Line used to count each vehicle once
LINE_DISTANCE_METERS = 20.0   # Real road distance between speed lines
MIN_CONTOUR_AREA = 900        # Raise this if shadows/noise create false detections
MAX_MATCH_DISTANCE = 85       # Largest allowed centroid movement between frames
MAX_MISSED_FRAMES = 12


@dataclass
class Vehicle:
    centroid: tuple[int, int]
    previous_centroid: tuple[int, int] | None = None
    missed: int = 0
    counted: bool = False
    line_times: dict[str, float] = field(default_factory=dict)
    speed_kmh: float | None = None


class CentroidTracker:
    """A small dependency-free tracker for a fixed-camera highway video."""

    def __init__(self) -> None:
        self.next_id = 1
        self.vehicles: dict[int, Vehicle] = {}

    def update(self, detections: list[tuple[int, int]]) -> dict[int, Vehicle]:
        unmatched = set(range(len(detections)))
        for vehicle_id, vehicle in list(self.vehicles.items()):
            if not detections:
                vehicle.missed += 1
                continue
            nearest = min(
                unmatched,
                key=lambda i: math.dist(vehicle.centroid, detections[i]),
                default=None,
            )
            if nearest is not None and math.dist(vehicle.centroid, detections[nearest]) < MAX_MATCH_DISTANCE:
                vehicle.previous_centroid = vehicle.centroid
                vehicle.centroid = detections[nearest]
                vehicle.missed = 0
                unmatched.remove(nearest)
            else:
                vehicle.missed += 1

        for index in unmatched:
            self.vehicles[self.next_id] = Vehicle(centroid=detections[index])
            self.next_id += 1

        self.vehicles = {
            vehicle_id: vehicle
            for vehicle_id, vehicle in self.vehicles.items()
            if vehicle.missed <= MAX_MISSED_FRAMES
        }
        return self.vehicles


def crossed(previous_y: int, current_y: int, line_y: int) -> bool:
    """True when a tracked centre moves through a horizontal line."""
    return (previous_y < line_y <= current_y) or (previous_y > line_y >= current_y)


def parse_input(value: str) -> str | int:
    return int(value) if value.isdigit() else value


def main() -> None:
    parser = argparse.ArgumentParser(description="Count highway vehicles and estimate speed.")
    parser.add_argument("--input", required=True, help="Video filename or camera number (for example 0)")
    parser.add_argument("--output", default="vehicle_result.mp4", help="Annotated output video filename")
    args = parser.parse_args()

    if SPEED_LINE_1_Y == SPEED_LINE_2_Y or LINE_DISTANCE_METERS <= 0:
        raise ValueError("Set two different speed-line positions and a positive distance.")

    capture = cv2.VideoCapture(parse_input(args.input))
    if not capture.isOpened():
        raise FileNotFoundError(f"Could not open input: {args.input}")

    fps = capture.get(cv2.CAP_PROP_FPS) or 30.0
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    writer = cv2.VideoWriter(
        args.output,
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )

    subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=32, detectShadows=True)
    tracker = CentroidTracker()
    vehicle_count = 0
    frame_number = 0

    while True:
        ok, frame = capture.read()
        if not ok:
            break
        frame_number += 1
        seconds = frame_number / fps

        mask = subtractor.apply(frame)
        _, mask = cv2.threshold(mask, 200, 255, cv2.THRESH_BINARY)  # remove shadows
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15)))
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detections = []
        for contour in contours:
            if cv2.contourArea(contour) >= MIN_CONTOUR_AREA:
                x, y, w, h = cv2.boundingRect(contour)
                detections.append((x + w // 2, y + h // 2))
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 180, 255), 2)

        vehicles = tracker.update(detections)
        for vehicle_id, vehicle in vehicles.items():
            x, y = vehicle.centroid
            previous_y = vehicle.previous_centroid[1] if vehicle.previous_centroid else y

            if not vehicle.counted and crossed(previous_y, y, COUNT_LINE_Y):
                vehicle.counted = True
                vehicle_count += 1

            for name, line_y in (("first", SPEED_LINE_1_Y), ("second", SPEED_LINE_2_Y)):
                if name not in vehicle.line_times and crossed(previous_y, y, line_y):
                    vehicle.line_times[name] = seconds

            if vehicle.speed_kmh is None and len(vehicle.line_times) == 2:
                elapsed = abs(vehicle.line_times["second"] - vehicle.line_times["first"])
                if elapsed > 0:
                    vehicle.speed_kmh = (LINE_DISTANCE_METERS / elapsed) * 3.6

            label = f"ID {vehicle_id}"
            if vehicle.speed_kmh is not None:
                label += f"  {vehicle.speed_kmh:.1f} km/h"
            cv2.circle(frame, (x, y), 4, (0, 0, 255), -1)
            cv2.putText(frame, label, (x + 8, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        for line_y, color in ((SPEED_LINE_1_Y, (0, 255, 0)), (SPEED_LINE_2_Y, (0, 255, 0)), (COUNT_LINE_Y, (255, 0, 0))):
            cv2.line(frame, (0, line_y), (width, line_y), color, 2)
        cv2.putText(frame, f"Vehicles counted: {vehicle_count}", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        writer.write(frame)
        cv2.imshow("Highway vehicle counter", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    capture.release()
    writer.release()
    cv2.destroyAllWindows()
    print(f"Total vehicles counted: {vehicle_count}")
    print(f"Saved annotated video to: {args.output}")


if __name__ == "__main__":
    main()
