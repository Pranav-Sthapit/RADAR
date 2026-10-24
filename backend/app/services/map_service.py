# backend/app/services/route_service.py
from .osm_graph import G
from fastapi import HTTPException

def get_map_bounds():
    if G.number_of_nodes() == 0:
        raise ValueError("The OSM graph contains no road nodes.")

    nodes = G.nodes(data=True)

    return {
        "south": min(data["y"] for _, data in nodes),
        "west": min(data["x"] for _, data in nodes),
        "north": max(data["y"] for _, data in nodes),
        "east": max(data["x"] for _, data in nodes),
    }


def validate_coordinate(lat: float, lng: float, name: str) -> None:
    lat = float(lat)
    lng = float(lng)
    bounds = get_map_bounds()

    if not (
        bounds["south"] <= lat <= bounds["north"]
        and bounds["west"] <= lng <= bounds["east"]
    ):
        raise HTTPException(
            status_code=400,
            detail=f"{name} is outside the permitted OSM map area.",
        )