import math

DRIVE_SPEED = 5.0
MAX_STEERING = 0.3

# Change to -1 if the car steers in the wrong direction.
STEERING_SIGN = 1


def calculate_target_yaw(
    current_lat: float,
    current_lng: float,
    target_lat: float,
    target_lng: float,
) -> float:
    """
    Calculate the direction from the current GPS position
    to the target waypoint.

    Returns an angle in radians, measured counterclockwise
    from geographic east.
    """

    mean_lat = math.radians(
        (current_lat + target_lat) / 2.0
    )

    dx = (
        math.radians(target_lng - current_lng)
        * math.cos(mean_lat)
    )

    dy = math.radians(target_lat - current_lat)

    return math.atan2(dy, dx)


def drive_towards(
    current_lat: float,
    current_lng: float,
    target_lat: float,
    target_lng: float,
    yaw: float,
    left_steer,
    right_steer,
    left_front_wheel,
    right_front_wheel,
) -> float:
    """
    Steer the BMW toward a geographic waypoint.

    Returns the approximate distance to the target in metres.

    IMPORTANT:
    This assumes GPS values are latitude/longitude and that
    the IMU yaw uses the same heading convention as target_yaw.
    """

    # Calculate target direction.
    target_yaw = calculate_target_yaw(
        current_lat,
        current_lng,
        target_lat,
        target_lng,
    )

    # Normalize heading error to [-pi, pi].
    heading_error = target_yaw - yaw
    heading_error = (
        heading_error + math.pi
    ) % (2.0 * math.pi) - math.pi

    # Convert heading error into a steering command.
    steering = max(
        -MAX_STEERING,
        min(MAX_STEERING, heading_error),
    )

    steering *= STEERING_SIGN

    # Calculate approximate distance to target in metres.
    mean_lat = math.radians(
        (current_lat + target_lat) / 2.0
    )

    dx = (
        math.radians(target_lng - current_lng)
        * 6371000.0
        * math.cos(mean_lat)
    )

    dy = (
        math.radians(target_lat - current_lat)
        * 6371000.0
    )

    distance = math.hypot(dx, dy)

    # Diagnostic output.
    print("\n[NAVIGATION]")
    print(
        f"Current position: "
        f"{current_lat:.8f}, {current_lng:.8f}"
    )
    print(
        f"Target position:  "
        f"{target_lat:.8f}, {target_lng:.8f}"
    )
    print(f"Current yaw:   {math.degrees(yaw):.2f} degrees")
    print(
        f"Target yaw:    {math.degrees(target_yaw):.2f} degrees"
    )
    print(
        f"Heading error: {math.degrees(heading_error):.2f} degrees"
    )
    print(f"Steering:      {steering:.3f} radians")
    print(f"Distance:      {distance:.2f} metres")

    # Apply steering.
    left_steer.setPosition(-steering)
    right_steer.setPosition(-steering)

    # Move forward.
    left_front_wheel.setVelocity(DRIVE_SPEED)
    right_front_wheel.setVelocity(DRIVE_SPEED)

    return distance