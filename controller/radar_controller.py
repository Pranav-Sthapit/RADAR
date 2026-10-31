"""radar_controller controller."""
from controller import Robot
from car_driver import CarDriver
from car_router import CarRouter
from object_detector import ObjectDetector


class Car:
    DRIVE_SPEED=5.0

    def __init__(self):
        self.robot=Robot()
        self.timestep=int(self.robot.getBasicTimeStep())

        self.gps = self.robot.getDevice("gps")
        self.gps.enable(self.timestep)

        self.imu = self.robot.getDevice("imu")
        self.imu.enable(self.timestep)

        self.camera = self.robot.getDevice("camera")
        self.camera.enable(self.timestep)

        self.left_steer = self.robot.getDevice("left_steer")
        self.right_steer = self.robot.getDevice("right_steer")

        self.left_steer.setPosition(0.0)
        self.right_steer.setPosition(0.0)

        self.left_front_wheel = self.robot.getDevice(
            "left_front_wheel"
        )
        self.right_front_wheel = self.robot.getDevice(
            "right_front_wheel"
        )

        self.left_front_wheel.setPosition(float("inf"))
        self.right_front_wheel.setPosition(float("inf"))

        self.stop()

        self.driver = CarDriver(self.gps, self.imu)
        self.router = CarRouter(self.gps)
        self.detector = ObjectDetector(self.camera)


    def apply_controls(self, steering):
        self.left_steer.setPosition(-steering)
        self.right_steer.setPosition(-steering)

        self.left_front_wheel.setVelocity(self.DRIVE_SPEED)
        self.right_front_wheel.setVelocity(self.DRIVE_SPEED)

    def stop(self):
        self.left_front_wheel.setVelocity(0.0)
        self.right_front_wheel.setVelocity(0.0)

        self.left_steer.setPosition(0.0)
        self.right_steer.setPosition(0.0)

    def update_navigation(self):
        checkpoint = self.router.get_checkpoint()

        if checkpoint is None:
            self.stop()
            return

        self.driver.set_checkpoint(
            checkpoint["lat"],
            checkpoint["lng"],
        )

        steering, distance = self.driver.drive_towards()

        if distance is None:
            self.stop()
            return

        self.apply_controls(steering)

    # ====================================
    # MAIN CONTROLLER LOOP
    # ====================================
    def run(self):
        self.router.update_position()

        self.router.start_routing()
        self.detector.start_detection()

        try:
            while self.robot.step(self.timestep) != -1:

                # Update GPS position for router.
                self.router.update_position()

                # Submit camera frame for background detection.
                self.detector.submit_frame()

                # Navigate toward current checkpoint.
                self.update_navigation()

        finally:
            self.stop()
            self.detector.stop_detection()
            self.router.stop_routing()

            print("BMW controller stopped.")



car = Car()
car.run()