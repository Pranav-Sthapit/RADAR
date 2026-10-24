
import math
import requests

URL = "http://localhost:8000/api/route"
REACHED_DISTANCE_M = 3.0


def distance_m(a: dict, b: dict) -> float:
    """Calculate distance between two geographic coordinates."""
    lat1 = math.radians(a["lat"])
    lat2 = math.radians(b["lat"])

    dlat = lat2 - lat1
    dlng = math.radians(b["lng"] - a["lng"])

    h = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlng / 2) ** 2
    )

    return 6371000 * 2 * math.asin(math.sqrt(h))


def get_next_coordinate(gps, old_route: list[dict]) -> list[dict]:
    """
    Read GPS, request an updated route, and return the
    remaining waypoints.
    """
    position = gps.getValues()

    start_lat = position[0]
    start_lng = position[1]

    payload = {
        "start_lat": start_lat,
        "start_lng": start_lng,
        "end_lat": None,
        "end_lng": None,
    }

    try:
        response = requests.post(URL, json=payload)
        response.raise_for_status()

        data = response.json()
        new_route = data["route"]

        print(
            f"Distance: {data['distance_m']:.2f} m "
            f"({data['distance_km']:.3f} km)"
        )
        print(f"Received {len(new_route)} route points")

        # If the new route begins with the waypoint we just
        # reached, remove it so we can continue forward.
        if old_route and new_route:
            old_first = old_route[0]
            new_first = new_route[0]

            if distance_m(old_first, new_first) <= REACHED_DISTANCE_M:
                new_route.pop(0)
                print("Removed the already-reached waypoint")

        return new_route

    except requests.RequestException as e:
        print("HTTP request failed:", e)

    except (ValueError, KeyError, TypeError) as e:
        print("Invalid backend response:", e)

    # Keep the old route if the request fails.
    return old_route
