import time
import threading
import queue
import requests
import numpy as np
import cv2

from ultralytics import YOLO


class ObjectDetector:

    MODEL_PATH = r"F:\cars\runs\traffic_signs\yolov8n\weights\best.pt"
    BACKEND_URL = "http://localhost:8000/api/detections"

    CONFIDENCE_THRESHOLD = 0.7
    UPLOAD_COOLDOWN_SECONDS = 5

    def __init__(self, camera):
        self.__camera = camera
        self.__model = YOLO(self.MODEL_PATH)

        self.__frame_queue = queue.Queue(maxsize=1)
        self.__detection_thread = None
        self.__last_upload_time = 0
        self.__stop_event = threading.Event()

    def start_detection(self):
        if self.__detection_thread and self.__detection_thread.is_alive():
            return

        self.__stop_event.clear()

        self.__detection_thread = threading.Thread(
            target=self.__detect_objects,
            name="ObjectDetectionThread",
            daemon=True
        )

        self.__detection_thread.start()

        print("YOLO detection thread started")

    def stop_detection(self):
        if not self.__detection_thread:
            return

        self.__stop_event.set()
        self.__detection_thread.join()
        self.__detection_thread = None

        print("YOLO Detection stopped")

    def submit_frame(self):
        if not self.__detection_thread or not self.__detection_thread.is_alive():
            return

        image = self.__camera.getImage()

        if image is None:
            return

        width = self.__camera.getWidth()
        height = self.__camera.getHeight()

        frame = np.frombuffer(
            image, dtype=np.uint8
        ).reshape((height, width, 4)).copy()

        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

        if self.__frame_queue.full():
            try:
                self.__frame_queue.get_nowait()
            except queue.Empty:
                pass

        try:
            self.__frame_queue.put_nowait(frame)
        except queue.Full:
            pass

    def __detect_objects(self):
        while not self.__stop_event.is_set():

            try:
                frame = self.__frame_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            results = self.__model.predict(
                source=frame,
                verbose=False,
                conf=self.CONFIDENCE_THRESHOLD,
            )

            for result in results:
                for box in result.boxes:

                    if self.__stop_event.is_set():
                        break

                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])

                    class_name = str(self.__model.names[class_id])
                    now = time.monotonic()

                    if now - self.__last_upload_time < self.UPLOAD_COOLDOWN_SECONDS:
                        continue

                    print(
                        f"[YOLO] {class_name} "
                        f"| confidence={confidence:.2f}"
                    )

                    self.__upload_detection(class_name)

    def __upload_detection(self, class_name):
        try:
            response = requests.post(
                self.BACKEND_URL,
                json={"class_name": class_name},
                timeout=3,
            )

            response.raise_for_status()

            self.__last_upload_time = time.monotonic()

            print("[BACKEND]", response.json())

        except requests.RequestException as exc:
            print(f"[UPLOAD ERROR] {exc}")