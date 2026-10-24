
import math
from controller import Robot

from route_client import (
    REACHED_DISTANCE_M,
    distance_m,
    get_next_coordinate,
)

from driving import drive_towards
from object_detection import detect_objects


robot = Robot()
timestep = int(robot.getBasicTimeStep())

gps = robot.getDevice("gps")
gps.enable(timestep)

camera = robot.getDevice("camera")
camera.enable(timestep)

imu = robot.getDevice("imu")
imu.enable(timestep)

left_steer = robot.getDevice("left_steer")
right_steer = robot.getDevice("right_steer")

left_steer.setPosition(0.0)
right_steer.setPosition(0.0)

left_front_wheel = robot.getDevice("left_front_wheel")
right_front_wheel = robot.getDevice("right_front_wheel")

left_front_wheel.setPosition(float("inf"))
right_front_wheel.setPosition(float("inf"))

left_front_wheel.setVelocity(0.0)
right_front_wheel.setVelocity(0.0)

current_route = []

if robot.step(timestep) != -1:
    current_route = get_next_coordinate(gps, current_route)

while robot.step(timestep) != -1:

    detect_objects(camera)

    if not current_route:
        left_front_wheel.setVelocity(0.0)
        right_front_wheel.setVelocity(0.0)
        continue

    # Current GPS position
    position = gps.getValues()

    current_position = {
        "lat": position[0],
        "lng": position[1],
    }

    # Current vehicle orientation
    roll, pitch, yaw = imu.getRollPitchYaw()

    # First waypoint
    target = current_route[0]

    distance_to_target = distance_m(
        current_position,
        target,
    )

    print(
        f"Distance to waypoint: "
        f"{distance_to_target:.2f} m"
    )

    if distance_to_target <= REACHED_DISTANCE_M:

        print("Waypoint reached!")

        current_route = get_next_coordinate(
            gps,
            current_route,
        )

        continue

    # --------------------------------------------------------
    # DRIVE TOWARD WAYPOINT
    # --------------------------------------------------------

    drive_towards(
        current_lat=current_position["lat"],
        current_lng=current_position["lng"],
        target_lat=target["lat"],
        target_lng=target["lng"],
        yaw=yaw,
        left_steer=left_steer,
        right_steer=right_steer,
        left_front_wheel=left_front_wheel,
        right_front_wheel=right_front_wheel,
    )

left_front_wheel.setVelocity(0.0)
right_front_wheel.setVelocity(0.0)

left_steer.setPosition(0.0)
right_steer.setPosition(0.0)

print("BMW controller stopped.")
