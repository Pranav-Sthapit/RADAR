import time
import threading
import queue
import requests
import numpy as np
import cv2

from ultralytics import YOLO



'''
    How to use
    1. make object in main controller
    2. call start detection
    3. call the submit_frame in the main thread in the loop
    4. call stop detection when on end

'''
class ObjectDetector:

    MODEL_PATH = r"F:\cars\runs\traffic_signs\yolov8n\weights\best.pt"
    BACKEND_URL = "http://localhost:8000/api/detections"

    CONFIDENCE_THRESHOLD = 0.7
    UPLOAD_COOLDOWN_SECONDS = 5

    def __init__(self,camera):
        self.camera = camera
        self.model = YOLO(self.MODEL_PATH)

        self.frame_queue=queue.Queue(maxsize=1)
        self.detection_thread = None
        self.last_upload_time = 0
        self.stop_event=threading.Event()

    def start_detection(self):
        if self.detection_thread and self.detection_thread.is_alive():
            return

        self.stop_event.clear()
        self.detection_thread = threading.Thread(
            target=self.detect_objects,
            name="ObjectDetectionThread",
            daemon=True
        )

        self.detection_thread.start()

        print("YOLO detection thread started")

    def stop_detection(self):
        if not self.detection_thread:
            return

        self.stop_event.set()
        self.detection_thread.join()
        self.detection_thread=None
        print("YOLO Detection stopped")

    def submit_frame(self):
        if not self.detection_thread or not self.detection_thread.is_alive():
            return

        image = self.camera.getImage()
        if image is None:
            return

        width = self.camera.getWidth()
        height = self.camera.getHeight()

        frame = np.frombuffer(
            image, dtype=np.uint8
        ).reshape((height, width, 4)).copy()

        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

        if self.frame_queue.full():
            try:
                self.frame_queue.get_nowait()
            except queue.Empty:
                pass

        try:
            self.frame_queue.put_nowait(frame)
        except queue.Full:
            pass

    def detect_objects(self):
        while not self.stop_event.is_set():
            try:
                frame = self.frame_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            results = self.model.predict(source = frame,
                                        verbose=False,
                                        conf = self.CONFIDENCE_THRESHOLD,)

            for result in results:
                for box in result.boxes:
                    if self.stop_event.is_set():
                        break
                    class_id = int(box.cls[0])
                    confidence=float(box.conf[0])

                    class_name = str(self.model.names[class_id])
                    now =time.monotonic()

                    if now - self.last_upload_time < self.UPLOAD_COOLDOWN_SECONDS:
                        continue

                    print(
                        f"[YOLO] {class_name} "
                        f"| confidence={confidence:.2f}"
                    )

                    self.upload_detection(class_name)

    def upload_detection(self,class_name):
        try:

            response = requests.post(
                self.BACKEND_URL,
                json={"class_name": class_name},
                timeout=3,
            )

            response.raise_for_status()
            self.last_upload_time = time.monotonic()
            print("[BACKEND]", response.json())

        except requests.RequestException as exc:

            print(f"[UPLOAD ERROR] {exc}")