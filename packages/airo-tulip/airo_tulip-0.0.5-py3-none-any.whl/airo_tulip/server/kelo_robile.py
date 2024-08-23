import zmq
from airo_tulip.platform_driver import PlatformDriverType
from airo_tulip.server.messages import (
    GetOdometryMessage,
    RequestMessage,
    ResponseMessage,
    SetPlatformVelocityTargetMessage,
    StopServerMessage,
    SetDriverTypeMessage
)
from airo_tulip.structs import Attitude2DType
from loguru import logger


class KELORobile:
    def __init__(self, robot_ip: str, robot_port: int):
        address = f"tcp://{robot_ip}:{robot_port}"
        logger.info(f"Connecting to {address}...")
        self._zmq_ctx = zmq.Context()
        self._zmq_socket = self._zmq_ctx.socket(zmq.REQ)
        self._zmq_socket.connect(address)
        logger.info(f"Connected to {address}.")

    def set_platform_velocity_target(
            self,
            vel_x: float,
            vel_y: float,
            vel_a: float,
            *,
            timeout: float = 1.0,
    ) -> ResponseMessage:
        """Set the x, y and angular velocity of the complete mobile platform.

        Args:
            vel_x: Linear velocity of platform in x (forward) direction in m/s.
            vel_y: Linear velocity of platform in y (left) direction in m/s.
            vel_a: Linear velocity of platform in angular direction in rad/s.
            timeout: Duration in seconds after which the movement is automatically stopped (default 1.0).

        Returns:
            A ResponseMessage object indicating the response status of the request.
        """
        msg = SetPlatformVelocityTargetMessage(vel_x, vel_y, vel_a, timeout, False)
        return self._transceive_message(msg)

    def align_drives(self, vel_x: float, vel_y: float, vel_a: float, *, timeout: float = 1.0) -> ResponseMessage:
        """Align the drives for the given velocity values, such that they are oriented correctly. Does not send forward velocities.

        Args:
            vel_x: Linear velocity of platform in x (forward) direction in m/s.
            vel_y: Linear velocity of platform in y (left) direction in m/s.
            vel_a: Linear velocity of platform in angular direction in rad/s.
            timeout: Duration in seconds after which the movement is automatically stopped (default 1.0).

        Returns:
            A ResponseMessage object indicating the response status of the request.
        """
        msg = SetPlatformVelocityTargetMessage(vel_x, vel_y, vel_a, timeout, True)
        return self._transceive_message(msg)

    def set_driver_type(self, driver_type: PlatformDriverType) -> ResponseMessage:
        """Set the mode of the platform driver.

        Args:
            driver_type: Type to which the driver should be set.

        Returns:
            A ResponseMessage object indicating the response status of the request.
        """
        msg = SetDriverTypeMessage(driver_type)
        return self._transceive_message(msg)

    def stop_server(self) -> ResponseMessage:
        """Stops the remote server.

        Returns:
            A ResponseMessage object indicating the response status of the request.
        """
        msg = StopServerMessage()
        return self._transceive_message(msg)

    def get_odometry(self) -> Attitude2DType:
        """Get the robot platform's odometry."""
        msg = GetOdometryMessage()
        return self._transceive_message(msg).odometry

    def _transceive_message(self, req: RequestMessage) -> ResponseMessage:
        self._zmq_socket.send_pyobj(req)
        return self._zmq_socket.recv_pyobj()

    def close(self):
        self._zmq_socket.close()
        self._zmq_ctx.term()

    def __del__(self):
        self.close()
