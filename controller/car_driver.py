
import math


class CarDriver:
    MAX_STEERING = 0.3
    STEERING_SIGN = 1
    EARTH_RADIUS_M = 6371000.0

    def __init__(self, gps, imu):
        self.gps = gps
        self.imu = imu

        self.target_lat = None
        self.target_lng = None

    def set_checkpoint(self, lat: float, lng: float):
        self.target_lat = lat
        self.target_lng = lng

    @staticmethod
    def calculate_target_yaw(current_lat, current_lng, target_lat, target_lng):
        mean_lat = math.radians((current_lat + target_lat) / 2.0)

        dx = (
            math.radians(target_lng - current_lng)
            * math.cos(mean_lat)
        )

        dy = math.radians(target_lat - current_lat)

        return math.atan2(dy, dx)

    @staticmethod
    def calculate_distance(current_lat, current_lng, target_lat, target_lng):
        mean_lat = math.radians((current_lat + target_lat) / 2.0)

        dx = (
            math.radians(target_lng - current_lng)
            * CarDriver.EARTH_RADIUS_M
            * math.cos(mean_lat)
        )

        dy = (
            math.radians(target_lat - current_lat)
            * CarDriver.EARTH_RADIUS_M
        )

        return math.hypot(dx, dy)

    def drive_towards(self):
        if self.target_lat is None or self.target_lng is None:
            return 0.0, None

        # Read current GPS position.
        position = self.gps.getValues()

        current_lat = position[0]
        current_lng = position[1]

        # Read current vehicle orientation.
        roll, pitch, yaw = self.imu.getRollPitchYaw()

        target_yaw = self.calculate_target_yaw(
            current_lat,
            current_lng,
            self.target_lat,
            self.target_lng,
        )

        heading_error = target_yaw - yaw

        heading_error = (
            heading_error + math.pi
        ) % (2.0 * math.pi) - math.pi

        steering = max(
            -self.MAX_STEERING,
            min(self.MAX_STEERING, heading_error),
        )

        steering *= self.STEERING_SIGN

        distance = self.calculate_distance(
            current_lat,
            current_lng,
            self.target_lat,
            self.target_lng,
        )

        return steering, distance
