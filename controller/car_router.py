import math
import time
import threading
import requests

class CarRouter:

    URL = "http://localhost:8000/api/route"

    REACHED_DISTANCE_M = 3.0
    ROUTE_UPDATE_INTERVAL = 3

    def __init__(self,gps):
        self.gps=gps
        self.route_list=[]
        self.current_position = None
        self.route_lock=threading.Lock()

        self.stop_event = threading.Event()
        self.routing_thread = None

    @staticmethod
    def distance(a:dict,b:dict)->float:
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

        position = self.gps.getValues()

        current = {
            "lat": position[0],
            "lng": position[1]
        }

        with self.route_lock:
            self.current_position = current

    def start_routing(self):
        '''start the route thread '''
        if self.routing_thread and self.routing_thread.is_alive():
            return

        self.stop_event.clear()

        self.routing_thread = threading.Thread(
            target=self.update_route,
            name="CarRoutingThread",
            daemon=True
        )

        self.routing_thread.start()
        print("[ROUTER] Routing thread started")

    def stop_routing(self):
        '''stop the route thread '''
        if not self.routing_thread:
            return

        self.stop_event.set()
        self.routing_thread.join()
        self.routing_thread = None
        print("[ROUTER] Routing stopped")

    def update_route(self):
        """
        Periodically request an updated route
        until the routing thread is stopped.
        """

        while not self.stop_event.is_set():
            with self.route_lock:
                if self.current_position is None:
                    position = None
                else:
                    position = self.current_position.copy()
                old_route = self.route_list.copy()

            if position is not None:
                new_route = self.get_route_from_server(
                    position,
                    old_route
                )

                if new_route is not None:
                    with self.route_lock:
                        self.route_list = new_route

            # Wait for the next update interval.
            # Can wake up immediately when stop_event is set.
            self.stop_event.wait(self.ROUTE_UPDATE_INTERVAL)


    def get_route_from_server(self,position,old_route):
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

                if self.distance(old_first, new_first) <= self.REACHED_DISTANCE_M:

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
        - Return the reached waypoint.

        Otherwise, return None.
        """

        with self.route_lock:

            if not self.current_position or not self.route_list:
                return None

            current = self.current_position
            checkpoint = self.route_list[0]
            distance = self.distance(current, checkpoint)

            if distance <= self.REACHED_DISTANCE_M:
                self.route_list.pop(0)
                print("[ROUTER] Checkpoint reached:", checkpoint)
                if not self.route_list:
                    return None
                return self.route_list[0]

            return checkpoint

