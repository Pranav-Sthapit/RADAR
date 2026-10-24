import time
import requests
from ultralytics import YOLO


MODEL_PATH=r"F:\cars\runs\traffic_signs\yolov8n\weights\best.pt"
BACKEND_URL = "http://localhost:8000/api/detections"

CONFIDENCE_THRESHOLD = 0.7
UPLOAD_COOLDOWN_SECONDS = 5

model = YOLO(MODEL_PATH)

last_sent = {}


def detect_objects(camera):
    image = camera.getImage()

    if image is None:
        return

    width = camera.getWidth()
    height = camera.getHeight()

    import numpy as np
    import cv2

    frame = np.frombuffer(
        image, dtype=np.uint8
    ).reshape((height, width, 4))

    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

    results = model.predict(
        source=frame,
        verbose=False,
        conf=CONFIDENCE_THRESHOLD,
    )

    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            class_name = str(model.names[class_id])

            now = time.monotonic()

            if now - last_sent.get(class_name, 0) < UPLOAD_COOLDOWN_SECONDS:
                continue

            print(
                f"[YOLO] {class_name} "
                f"| confidence={confidence:.2f}"
            )

            try:
                response = requests.post(
                    BACKEND_URL,
                    json={"class_name": class_name},
                    timeout=3,
                )
                response.raise_for_status()

                last_sent[class_name] = time.monotonic()
                print("[BACKEND]", response.json())

            except requests.RequestException as exc:
                print(f"[UPLOAD ERROR] {exc}")