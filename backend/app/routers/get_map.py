from fastapi import APIRouter

from ..services import map_object

router = APIRouter(prefix="/api/map", tags=["Map"])


@router.get("/bounds")
def get_map_bounds():
    return map_object.get_map_bounds()