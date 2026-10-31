from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..services import detection_object


router = APIRouter(
    prefix="/api/detections",
    tags=["Map"],
)

# Queue stores class names only.
paths: list[str] = []

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
    result = detection_object.create_detection(data.class_name)
    if result is None:
        raise HTTPException(
            status_code=400,
            detail="Class name cannot be empty.",
        )

    return result


@router.get("/new")
def get_pending_detections():
    return detection_object.get_pending_detection()