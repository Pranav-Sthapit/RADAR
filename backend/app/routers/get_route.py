from decimal import Decimal

from fastapi import APIRouter, HTTPException

from ..schemas.get_route import RouteRequest, RouteResponse
from ..services import route_object

router = APIRouter(
    prefix="/api/route",
    tags=["Map"],
)

# In-memory state for a single routing session
current_position = {
    "lat": None,
    "lng": None,
}

destination = {
    "lat": None,
    "lng": None,
}

@router.delete("",status_code=204)
def clear_destination():
    destination["lat"]=None
    destination["lng"]=None
    current_position["lat"]=None
    current_position["lng"]=None


@router.post("", response_model=RouteResponse)
def get_route(payload: RouteRequest):
    # Update current position when supplied
    if payload.start_lat is not None:
        current_position["lat"] = payload.start_lat

    if payload.start_lng is not None:
        current_position["lng"] = payload.start_lng

    # Update destination when supplied
    if payload.end_lat is not None:
        destination["lat"] = payload.end_lat

    if payload.end_lng is not None:
        destination["lng"] = payload.end_lng

    # Ensure all coordinates have been received
    if any(
        value is None
        for value in (
            current_position["lat"],
            current_position["lng"],
            destination["lat"],
            destination["lng"],
        )
    ):
        raise HTTPException(
            status_code=400,
            detail="Starting position and destination are required.",
        )

    try:
        return route_object.calculate_route(
            current_position["lat"],
            current_position["lng"],
            destination["lat"],
            destination["lng"],
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc