"""radar_controller controller."""

from controller import Robot

from car_driver import CarDriver
from car_router import CarRouter
from object_detector import ObjectDetector


class Car:

    DRIVE_SPEED = 5.0

    def __init__(self):
        self.__robot = Robot()
        self.__timestep = int(self.__robot.getBasicTimeStep())

        # GPS
        self.__gps = self.__robot.getDevice("gps")
        self.__gps.enable(self.__timestep)

        # IMU
        self.__imu = self.__robot.getDevice("imu")
        self.__imu.enable(self.__timestep)

        # Camera
        self.__camera = self.__robot.getDevice("camera")
        self.__camera.enable(self.__timestep)

        # Steering motors
        self.__left_steer = self.__robot.getDevice("left_steer")
        self.__right_steer = self.__robot.getDevice("right_steer")

        self.__left_steer.setPosition(0.0)
        self.__right_steer.setPosition(0.0)

        # Front wheels
        self.__left_front_wheel = self.__robot.getDevice(
            "left_front_wheel"
        )
        self.__right_front_wheel = self.__robot.getDevice(
            "right_front_wheel"
        )

        self.__left_front_wheel.setPosition(float("inf"))
        self.__right_front_wheel.setPosition(float("inf"))

        self.__stop()

        # Supporting objects
        self.__driver = CarDriver(self.__gps, self.__imu)
        self.__router = CarRouter(self.__gps)
        self.__detector = ObjectDetector(self.__camera)

    def __apply_controls(self, steering):
        self.__left_steer.setPosition(-steering)
        self.__right_steer.setPosition(-steering)

        self.__left_front_wheel.setVelocity(self.DRIVE_SPEED)
        self.__right_front_wheel.setVelocity(self.DRIVE_SPEED)

    def __stop(self):
        self.__left_front_wheel.setVelocity(0.0)
        self.__right_front_wheel.setVelocity(0.0)

        self.__left_steer.setPosition(0.0)
        self.__right_steer.setPosition(0.0)

    def __update_navigation(self):
        checkpoint = self.__router.get_checkpoint()

        if checkpoint is None:
            self.__stop()
            return

        self.__driver.set_checkpoint(
            checkpoint["lat"],
            checkpoint["lng"],
        )

        steering, distance = self.__driver.drive_towards()

        if distance is None:
            self.__stop()
            return

        self.__apply_controls(steering)

    def run(self):
        self.__router.update_position()

        self.__router.start_routing()
        self.__detector.start_detection()

        try:
            while self.__robot.step(self.__timestep) != -1:

                # Update GPS position for router.
                self.__router.update_position()

                # Submit camera frame for background detection.
                self.__detector.submit_frame()

                # Navigate toward current checkpoint.
                self.__update_navigation()

        finally:
            self.__stop()
            self.__detector.stop_detection()
            self.__router.stop_routing()

            print("BMW controller stopped.")


car = Car()
car.run()