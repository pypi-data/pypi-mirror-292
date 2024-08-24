import numpy as np
from numpy.typing import NDArray
import pyrealsense2 as rs

from jacobi import Camera, JacobiError
from jacobi_camera_driver import CameraDriver


class RealsenseCameraDriver(CameraDriver):
    """Class for Intel Realsense camera driver."""
    DEFAULT_CONFIG = {
        'color_image_width': 640,
        'color_image_height': 480,
        'depth_image_width': 640,
        'depth_image_height': 480,
        'frames_per_second': 30,
    }
    # DEFAULT_CONFIG = {
    #     'color_image_width': 1280,
    #     'color_image_height': 720,
    #     'depth_image_width': 1280,
    #     'depth_image_height': 720,
    #     'frames_per_second': 30,
    # }
    INITIAL_WAIT = 10

    def __init__(self, camera: Camera, connect_to_studio: bool = False, filter_depth: bool = False):
        """Create a Realsense driver and connect to the camera.

        Args:
            camera (Camera): The camera.
            connect_to_studio (bool): Whether to connect to Jacobi Studio.
        """
        super().__init__(camera, connect_to_studio)

        self._running = False
        self._config = rs.config()
        self._pipeline = rs.pipeline()
        self._pipeline_wrapper = rs.pipeline_wrapper(self._pipeline)
        self._profile = self._config.resolve(self._pipeline_wrapper)
        self._align = rs.align(rs.stream.color)

        self._spatial_filter = rs.spatial_filter()
        self._hole_filling = rs.hole_filling_filter()
        self.filter_depth = filter_depth

        if not self.reconnect():
            raise JacobiError('driver', 'Could not connect to the camera.')

    def __del__(self):
        if self._running:
            self._pipeline.stop()

    def reconnect(self) -> bool:
        """Reconnect the camera.

        Returns:
            bool: True if the camera reconnected successfully, false otherwise.
        """
        self._device = self._profile.get_device()
        if len(self._device.sensors) == 0:
            return False

        # Configure the streams and start the camera
        self._config.enable_stream(rs.stream.color, self.DEFAULT_CONFIG['color_image_width'], self.DEFAULT_CONFIG['color_image_height'], rs.format.bgr8,
                                   self.DEFAULT_CONFIG['frames_per_second'])
        self._config.enable_stream(rs.stream.depth, self.DEFAULT_CONFIG['depth_image_width'], self.DEFAULT_CONFIG['depth_image_height'], rs.format.z16,
                                   self.DEFAULT_CONFIG['frames_per_second'])
        self._pipeline.start(self._config)

        # Get the depth scale from the depth stream
        self._depth_scale = self._profile.get_device().first_depth_sensor().get_depth_scale()

        # Wait for auto-exposure
        for _ in range(self.INITIAL_WAIT):
            self._pipeline.wait_for_frames()

        # Get the intrinsics from the color stream
        frames = self._pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        intr = color_frame.profile.as_video_stream_profile().intrinsics
        self.camera.intrinsics.focal_length_x = intr.fx
        self.camera.intrinsics.focal_length_y = intr.fy
        self.camera.intrinsics.optical_center_x = intr.ppx
        self.camera.intrinsics.optical_center_y = intr.ppy

        self._running = True
        return True

    def filter_depth_image(self, image: NDArray) -> NDArray:
        """Filter a depth image."""
        return self._spatial_filter.process(image)

    def get_images(self) -> tuple[NDArray, NDArray]:
        """Get color and depth images from camera.

        Returns:
            tuple[NDArray, NDArray]: The color image and the depth image.
        """
        frames = self._pipeline.wait_for_frames()
        frames = self._align.process(frames)
        color_frame = frames.get_color_frame()
        depth_frame = frames.get_depth_frame()
        if not color_frame or not depth_frame:
            print('Warning: could not get camera frame')
            return None
        if self.filter_depth:
            depth_frame = post_process_depth_frame(depth_frame)
        color_image = np.asanyarray(color_frame.get_data())
        depth_image = np.asanyarray(depth_frame.get_data()) * self._depth_scale
        return bgr2rgb(color_image), depth_image

    def get_color_image(self) -> NDArray:
        """Get color image from camera.

        Returns:
            NDArray: The color image.
        """
        frames = self._pipeline.wait_for_frames()
        frames = self._align.process(frames)
        color_frame = frames.get_color_frame()
        if not color_frame:
            print('Warning: could not get color frame')
            return None
        self.color_intr = color_frame.profile.as_video_stream_profile().intrinsics
        return bgr2rgb(np.asanyarray(color_frame.get_data()))

    def get_depth_image(self) -> NDArray:
        """Get depth image from camera.

        Returns:
            NDArray: The depth image.
        """
        frames = self._pipeline.wait_for_frames()
        frames = self._align.process(frames)
        depth_frame = frames.get_depth_frame()
        if not depth_frame:
            print('Warning: could not get depth frame')
            return None
        if self.filter_depth:
            depth_frame = post_process_depth_frame(depth_frame)
        return np.asanyarray(depth_frame.get_data()) * self._depth_scale

    def get_rs_intrinsics(self):
        return self.color_intr


def post_process_depth_frame(depth_frame, decimation_magnitude=1.0, spatial_magnitude=2.0, spatial_smooth_alpha=0.5,
                                spatial_smooth_delta=20, temporal_smooth_alpha=0.4, temporal_smooth_delta=20):
    """Filter the depth frame.

    Returns:
        The depth frame after filtering.
    """

    # Post processing possible only on the depth_frame
    assert depth_frame.is_depth_frame()

    # Available filters and control options for the filters
    decimation_filter = rs.decimation_filter()
    spatial_filter = rs.spatial_filter()
    temporal_filter = rs.temporal_filter()

    filter_magnitude = rs.option.filter_magnitude
    filter_smooth_alpha = rs.option.filter_smooth_alpha
    filter_smooth_delta = rs.option.filter_smooth_delta

    # Apply the control parameters for the filter
    decimation_filter.set_option(filter_magnitude, decimation_magnitude)
    spatial_filter.set_option(filter_magnitude, spatial_magnitude)
    spatial_filter.set_option(filter_smooth_alpha, spatial_smooth_alpha)
    spatial_filter.set_option(filter_smooth_delta, spatial_smooth_delta)
    temporal_filter.set_option(filter_smooth_alpha, temporal_smooth_alpha)
    temporal_filter.set_option(filter_smooth_delta, temporal_smooth_delta)

    # Apply the filters
    filtered_frame = decimation_filter.process(depth_frame)
    filtered_frame = spatial_filter.process(filtered_frame)
    filtered_frame = temporal_filter.process(filtered_frame)

    print('Postprocessed the depth frame')

    return filtered_frame


def bgr2rgb(image: NDArray):
    """Convert a BGR image to an RGB image.

    Args:
        NDArray: A BGR image.

    Returns:
        NDArray: A RGB image.
    """
    return image[..., ::-1]
