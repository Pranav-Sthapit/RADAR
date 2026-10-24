from decimal import Decimal
from pathlib import Path

import osmnx as ox
import networkx as nx

from .map_service import validate_coordinate
from .osm_graph import G
from .astar import bidirectional_astar

import math
import networkx as nx

import math
import networkx as nx


def nearest_reachable_node(G, lat, lng, target_node, radius_m=150):
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

        if distance <= radius_m:
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
        f"No node within {radius_m} m has a route to the destination."
    )


def calculate_route(
    start_lat: Decimal,
    start_lng: Decimal,
    end_lat: Decimal,
    end_lng: Decimal,
):
    if not G.nodes:
        raise ValueError("The road network graph is empty.")

    validate_coordinate(start_lat, start_lng, "Start point")
    validate_coordinate(end_lat, end_lng, "Destination")

    # Find the closest road nodes to the supplied coordinates.

    end_node = ox.distance.nearest_nodes(
        G,
        X=float(end_lng),
        Y=float(end_lat),
    )

    start_node = nearest_reachable_node(
        G,
        float(start_lat),
        float(start_lng),
        end_node,
    )

    

    # Calculate shortest route by road distance (metres).
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

    # Convert graph nodes to [latitude, longitude] for Leaflet.
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