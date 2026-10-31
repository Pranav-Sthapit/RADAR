import math
import networkx as nx
import osmnx as ox

from decimal import Decimal

from .osm_graph import OSMGraph
from .map_service import MapService
from .astar import bidirectional_astar


class RouteService:

    REACHABLE_RADIUS_M = 150

    def __init__(
        self,
        osm_graph: OSMGraph,
        map_service: MapService,
    ):
        self.osm_graph = osm_graph
        self.map_service = map_service

    def nearest_reachable_node(
        self,
        lat: float,
        lng: float,
        target_node,
    ):

        G = self.osm_graph.get_graph()

        candidates = []

        for node, data in G.nodes(data=True):

            node_lat = data["y"]
            node_lng = data["x"]

            dy = (node_lat - lat) * 111_320

            dx = (
                (node_lng - lng)
                * 111_320
                * math.cos(math.radians(lat))
            )

            distance = math.hypot(dx, dy)

            if distance <= self.REACHABLE_RADIUS_M:
                candidates.append((distance, node))

        candidates.sort(key=lambda item: item[0])

        for distance, node in candidates:

            if nx.has_path(G, node, target_node):

                print(
                    f"Selected start node: {node}, "
                    f"distance: {distance:.2f} m"
                )

                return node

        raise ValueError(
            f"No node within {self.REACHABLE_RADIUS_M} m "
            "has a route to the destination."
        )

    def calculate_route(
        self,
        start_lat: Decimal,
        start_lng: Decimal,
        end_lat: Decimal,
        end_lng: Decimal,
    ):

        G = self.osm_graph.get_graph()

        if G.number_of_nodes() == 0:
            raise ValueError("The road network graph is empty.")

        # Validate coordinates.
        self.map_service.validate_coordinate(
            start_lat,
            start_lng,
            "Start point",
        )

        self.map_service.validate_coordinate(
            end_lat,
            end_lng,
            "Destination",
        )

        # Find destination road node.
        end_node = ox.distance.nearest_nodes(
            G,
            X=float(end_lng),
            Y=float(end_lat),
        )

        # Find the nearest reachable starting road node.
        start_node = self.nearest_reachable_node(
            float(start_lat),
            float(start_lng),
            end_node,
        )

        # Calculate shortest route.
        try:

            distance_m, route_nodes = bidirectional_astar(
                G,
                source=start_node,
                target=end_node,
            )

        except nx.NetworkXNoPath as exc:

            raise ValueError(
                "No drivable route connects the start and destination "
                "in the loaded OSM map."
            ) from exc

        # Convert graph nodes into Leaflet coordinates.
        coordinates = [
            {
                "lat": float(G.nodes[node]["y"]),
                "lng": float(G.nodes[node]["x"]),
            }
            for node in route_nodes
        ]

        return {
            "distance_m": round(float(distance_m), 2),
            "distance_km": round(float(distance_m) / 1000, 3),
            "route": coordinates,
        }