import numpy as np
from numpy.typing import NDArray

from python_phoxi_sensor import PhoxiSensor

from jacobi import Camera, JacobiError
from jacobi_camera_driver import CameraDriver


class PhoXiCameraDriver(CameraDriver):
    """Class for Photoneo PhoXi camera driver."""

    def __init__(self, camera: Camera, connect_to_studio: bool = False):
        """Create a PhoXi driver and connect to the camera.

        Args:
            camera (Camera): The camera.
            connect_to_studio (bool): Whether to connect to Jacobi Studio.
        """
        super().__init__(camera, connect_to_studio)

        self._depth_scale = 1000.0
        self._phoxi_sensor = PhoxiSensor('phoxi', camera.name, '')
        self._running = False

        if not self.reconnect():
            raise JacobiError('driver', 'Could not connect to the camera.')

    def __del__(self):
        if self._running:
            self.stop()

    def reconnect(self) -> bool:
        """Reconnect the camera."""
        return self._phoxi_sensor.connect()

    def get_images(self) -> tuple[NDArray, NDArray]:
        """Get texture and depth images from camera.

        Returns:
            tuple[NDArray, NDArray]: The texture image and the depth image.
        """
        self._phoxi_sensor.frames()

        self._set_intrinsics()

        depth_map = np.array(self._phoxi_sensor.get_depth_map())
        depth_image = depth_map / self._depth_scale

        texture = np.array(self._phoxi_sensor.get_texture())
        texture = (texture / texture.max() * 255).astype(np.uint8)
        texture = np.dstack((texture,) * 3)

        return texture, depth_image

    def get_texture_image(self) -> NDArray:
        """Get texture image from camera.

        Returns:
            NDArray: The texture image.
        """
        self._phoxi_sensor.frames()

        self._set_intrinsics()

        texture = np.array(self._phoxi_sensor.get_texture())
        texture = (texture / texture.max() * 255).astype(np.uint8)

        return np.dstack((texture,) * 3)

    def get_depth_image(self) -> NDArray:
        """Get depth image from camera.

        Returns:
            NDArray: The depth image.
        """
        self._phoxi_sensor.frames()

        self._set_intrinsics()

        depth_map = np.array(self._phoxi_sensor.get_depth_map())

        return depth_map / self._depth_scale

    def distortion_coefficients(self) -> list[float]:
        return self._phoxi_sensor.distortion_coefficients

    def _set_intrinsics(self):
        self.camera.intrinsics.focal_length_x = self._phoxi_sensor.fx
        self.camera.intrinsics.focal_length_y = self._phoxi_sensor.fy
        self.camera.intrinsics.optical_center_x = self._phoxi_sensor.cx
        self.camera.intrinsics.optical_center_y = self._phoxi_sensor.cy
