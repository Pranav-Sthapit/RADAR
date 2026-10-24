from fastapi import APIRouter
from app.services import map_service

router = APIRouter(prefix="/api/map", tags=["Map"])


@router.get("/bounds")
def get_map_bounds():
    return map_service.get_map_bounds()