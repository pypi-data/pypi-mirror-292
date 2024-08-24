from abc import ABC, abstractmethod
from numpy.typing import NDArray

from jacobi import Camera, Frame, Intrinsics, Studio


class CameraDriver(ABC):
    """Abstract base class for cameras."""

    @abstractmethod
    def __init__(self, camera: Camera, connect_to_studio: bool = False):
        """Abstract constructor for camera drivers."""
        self.camera = camera
        if connect_to_studio:
            self.connect_to_studio()

    @abstractmethod
    def get_images(self) -> tuple[NDArray]:
        """Get images from camera."""

    @property
    def model(self) -> str:
        """Get model name of camera."""
        return self.camera.model

    @property
    def name(self) -> str:
        """Get name of camera."""
        return self.camera.name

    @property
    def intrinsics(self) -> Intrinsics:
        """Get intrinsics from camera."""
        return self.camera.intrinsics

    @intrinsics.setter
    def intrinsics(self, intrinsics: Intrinsics):
        """Set camera intrinsics."""
        self.camera.intrinsics = intrinsics

    @property
    def intrinsics_matrix(self) -> NDArray:
        """Get intrinsics as 3x3 matrix:

        [[fx, 0, cx]
         [0, fy, cy]
         [0,  0,  0]]
        """
        return self.camera.intrinsics.as_matrix()

    @property
    def origin(self) -> Frame:
        """Get camera pose/origin."""
        return self.camera.origin

    @origin.setter
    def origin(self, origin: Frame) -> Frame:
        """Set camera pose/origin."""
        self.camera.origin = origin

    @origin.setter
    def origin(self, origin: Frame):
        """Set camera pose/origin."""
        self.camera.origin = origin

    def connect_to_studio(self):
        """Connect to Studio."""
        self._studio = Studio(timeout=5)

    def __str__(self) -> str:
        info = f'name: {self.name}\n'
        info += f'model: {self.model}\n'
        info += f'origin: {self.origin}\n'
        info += f'intrinsics:\n{self.intrinsics_matrix}\n'
        return info
