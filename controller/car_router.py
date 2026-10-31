import math
import time
import threading
import requests


class CarRouter:

    URL = "http://localhost:8000/api/route"

    REACHED_DISTANCE_M = 3.0
    ROUTE_UPDATE_INTERVAL = 3

    def __init__(self, gps):
        self.__gps = gps
        self.__route_list = []
        self.__current_position = None
        self.__route_lock = threading.Lock()

        self.__stop_event = threading.Event()
        self.__routing_thread = None

    @staticmethod
    def __distance(a: dict, b: dict) -> float:
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

    def update_position(self):
        """
        Read GPS in the main Webots thread
        and update the current position.
        """

        position = self.__gps.getValues()

        current = {
            "lat": position[0],
            "lng": position[1]
        }

        with self.__route_lock:
            self.__current_position = current

    def start_routing(self):
        """Start the route thread."""

        if self.__routing_thread and self.__routing_thread.is_alive():
            return

        self.__stop_event.clear()

        self.__routing_thread = threading.Thread(
            target=self.__update_route,
            name="CarRoutingThread",
            daemon=True
        )

        self.__routing_thread.start()
        print("[ROUTER] Routing thread started")

    def stop_routing(self):
        """Stop the route thread."""

        if not self.__routing_thread:
            return

        self.__stop_event.set()
        self.__routing_thread.join()
        self.__routing_thread = None

        print("[ROUTER] Routing stopped")

    def __update_route(self):
        """
        Periodically request an updated route
        until the routing thread is stopped.
        """

        while not self.__stop_event.is_set():

            with self.__route_lock:
                if self.__current_position is None:
                    position = None
                else:
                    position = self.__current_position.copy()

                old_route = self.__route_list.copy()

            if position is not None:

                new_route = self.__get_route_from_server(
                    position,
                    old_route
                )

                if new_route is not None:
                    with self.__route_lock:
                        self.__route_list = new_route

            self.__stop_event.wait(self.ROUTE_UPDATE_INTERVAL)

    def __get_route_from_server(self, position, old_route):
        """Request a route from the backend."""

        payload = {
            "start_lat": position["lat"],
            "start_lng": position["lng"],
            "end_lat": None,
            "end_lng": None,
        }

        try:
            response = requests.post(
                self.URL,
                json=payload,
                timeout=5
            )

            response.raise_for_status()
            data = response.json()
            new_route = data["route"]

            print(
                f"[ROUTER] Distance: {data['distance_m']:.2f} m "
                f"({data['distance_km']:.3f} km)"
            )

            print(f"[ROUTER] Received {len(new_route)} route points")

            # Remove an already-reached waypoint if it
            # appears again at the beginning of the new route.
            if old_route and new_route:

                old_first = old_route[0]
                new_first = new_route[0]

                if self.__distance(
                    old_first,
                    new_first
                ) <= self.REACHED_DISTANCE_M:

                    new_route.pop(0)

                    print("[ROUTER] Removed duplicate waypoint")

            return new_route

        except requests.RequestException as exc:

            print("[ROUTER] HTTP request failed:", exc)

        except (ValueError, KeyError, TypeError) as exc:

            print("[ROUTER] Invalid backend response:", exc)

        # Keep the existing route if the request fails.
        return None

    def get_checkpoint(self):
        """
        Check whether the current waypoint has been reached.

        If distance is within the threshold:
        - Remove the waypoint from route_list.
        - Return the next waypoint.

        Otherwise, return the current waypoint.
        """

        with self.__route_lock:

            if not self.__current_position or not self.__route_list:
                return None

            current = self.__current_position
            checkpoint = self.__route_list[0]

            distance = self.__distance(current, checkpoint)

            if distance <= self.REACHED_DISTANCE_M:

                self.__route_list.pop(0)

                print("[ROUTER] Checkpoint reached:", checkpoint)

                if not self.__route_list:
                    return None

                return self.__route_list[0]

            return checkpoint