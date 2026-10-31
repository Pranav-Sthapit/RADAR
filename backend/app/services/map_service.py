from fastapi import HTTPException

from .osm_graph import OSMGraph


class MapService:

    def __init__(self, osm_graph: OSMGraph):
        self.__osm_graph = osm_graph

    def get_map_bounds(self):

        G = self.__osm_graph.get_graph()

        if G.number_of_nodes() == 0:
            raise ValueError("The OSM graph contains no road nodes.")

        nodes = G.nodes(data=True)

        return {
            "south": min(data["y"] for _, data in nodes),
            "west": min(data["x"] for _, data in nodes),
            "north": max(data["y"] for _, data in nodes),
            "east": max(data["x"] for _, data in nodes),
        }

    def validate_coordinate(
        self,
        lat: float,
        lng: float,
        name: str,
    ) -> None:

        lat = float(lat)
        lng = float(lng)

        bounds = self.get_map_bounds()

        if not (
            bounds["south"] <= lat <= bounds["north"]
            and bounds["west"] <= lng <= bounds["east"]
        ):
            raise HTTPException(
                status_code=400,
                detail=f"{name} is outside the permitted OSM map area.",
            )