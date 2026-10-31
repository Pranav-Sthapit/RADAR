class DetectionService:

    def __init__(self):
        # Private queue storing detected class names.
        self.__paths: list[str] = []

        # Private mapping of detection classes to images.
        self.__image_by_class = {
            "stop": "/static/signs/stop_sign.jpg",
            "speed_limit": "/static/signs/speed_limit.jpg",
            "traffic_light": "/static/signs/traffic_light.jpg",
        }

    def create_detection(self, class_name: str):
        class_name = class_name.strip().lower()

        if not class_name:
            return None

        self.__paths.append(class_name)

        print(f"[DETECTION RECEIVED] {class_name}")

        return {
            "message": "Detection received",
            "class_name": class_name,
        }

    def get_pending_detection(self):
        if not self.__paths:
            return {
                "detected": False,
                "class_name": None,
                "image_path": None,
            }

        class_name = self.__paths.pop(0)

        return {
            "detected": True,
            "class_name": class_name,
            "image_path": self.__image_by_class.get(class_name),
        }