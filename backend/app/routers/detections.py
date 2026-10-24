from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(
    prefix="/api/detections",
    tags=["Map"],
)

# Queue stores class names only.
paths: list[str] = ["stop","stop","stop","stop"
]

# Fixed images for each class.
# Put the corresponding images inside static/signs/.
IMAGE_BY_CLASS = {
    "stop": "/static/signs/stop_sign.jpg",
    "speed_limit": "/static/signs/speed_limit.jpg",
    "traffic_light": "/static/signs/traffic_light.jpg",
}

STATIC_DIR = Path("static/signs")


class DetectionRequest(BaseModel):
    class_name: str


@router.post("")
def create_detection(data: DetectionRequest):
    class_name = data.class_name.strip().lower()
    if not class_name:
        raise HTTPException(
            status_code=400,
            detail="Class name cannot be empty.",
        )

    # Store only the detected class name.
    paths.append(class_name)

    print(f"[DETECTION RECEIVED] {class_name}")

    return {
        "message": "Detection received",
        "class_name": class_name,
    }


@router.get("/new")
def get_pending_detections():
    if not paths:
        return {
            "detected": False,
            "class_name":None,
            "image_path":None
        }

    # Get and remove the oldest queued detection.
    class_name = paths.pop(0)

    return {
        "detected": True,
        "class_name": class_name,
        "image_path": IMAGE_BY_CLASS.get(class_name),
    }