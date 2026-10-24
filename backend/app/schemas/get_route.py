from pydantic import BaseModel,Field
from decimal import Decimal

class RouteRequest(BaseModel):
    start_lat: Decimal | None = Field(default=None, ge=-90, le=90)
    start_lng: Decimal | None = Field(default=None, ge=-180, le=180)
    end_lat: Decimal | None = Field(default=None, ge=-90, le=90)
    end_lng: Decimal | None = Field(default=None, ge=-180, le=180)

class Coordinate(BaseModel):
    lat: float
    lng: float

class RouteResponse(BaseModel):
    distance_m: float
    distance_km: float
    route: list[Coordinate]