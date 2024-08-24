import base64
import cv2
import numpy as np
from numpy.typing import NDArray

from jacobi import Camera, CameraStream, Studio

from jacobi_camera_driver import CameraDriver


class SimulatedCameraDriver(CameraDriver):
    """Class for simulated RGBD cameras in Studio."""

    def __init__(self, camera: Camera, studio: Studio = None):
        """Create a simulated RGBD camera."""
        if studio:
            super().__init__(camera, False)
            self._studio = studio
        else:
            super().__init__(camera, True)

    def get_images(self) -> tuple[NDArray, NDArray]:
        """Get color and depth images from camera."""
        return self.get_color_image(), self.get_depth_image()

    def get_color_image(self) -> NDArray:
        """Get color image from camera."""
        encoded = self._studio.get_camera_image_encoded(CameraStream.Color, self.camera)
        image = np.frombuffer(base64.b64decode(encoded), np.uint8)
        image = cv2.imdecode(image, cv2.IMREAD_ANYCOLOR)
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    def get_depth_image(self) -> NDArray:
        """Get depth image from camera."""
        decoded = base64.decodebytes(bytes(self._studio.get_camera_image_encoded(CameraStream.Depth, self.camera), 'utf-8'))
        image = np.frombuffer(decoded, np.float32).reshape((480, 640, 4))
        return np.copy(image[:, :, :1].squeeze(-1))
