from abc import ABC
import numpy as np
from numpy.typing import NDArray

from jacobi import Camera, Frame


class Image(ABC):
    """Abstract base class for images."""

    def __init__(self, data: NDArray):
        """Create an image.

        Args:
            data (NDArray): An array that contains the data to be stored in the image. The array can be of shape (height, width) or (height, width, channels).

        """
        self.data = data
        self.width = data.shape[1]
        self.height = data.shape[0]
        if len(data.shape) > 2:
            self.channels = data.shape[2]

    def project(self, points: NDArray, camera: Camera) -> NDArray:
        """Project 3D points from camera frame to 2D pixels in image frame.

        Args:
            points (NDArray): An n x 3 array of the points to be deprojected.
            camera (Camera): The camera associated with the camera frame.

        Returns:
            NDArray: The n x 2 array of pixels in the image frame.
        """
        pixels = points[:2, :] / points[2, :]
        pixels = camera.intrinsics.as_matrix() @ np.vstack((pixels, np.ones(pixels.shape[1])))

        return pixels[:2, :]

    def deproject(self, pixels: NDArray, camera: Camera) -> NDArray:
        """Deproject 2D pixels from image frame to 3D points in camera frame.

        Args:
            pixels (NDArray): An n x 3 array of the pixels to be deprojected. First row are the coordinates of the pixels along the x-axis, second row are the
            coordinates of the pixels along the y-axis, and third row are the depth values for each pixel.
            camera (Camera): The camera associated with the camera frame.

        Returns:
            NDArray: The n x 3 array of points in the camera frame.
        """
        points = np.linalg.inv(camera.intrinsics.as_matrix()) @ np.vstack((pixels[:2, :], np.ones(pixels.shape[1])))
        points *= pixels[2, :]

        return points

    def transform(self, points: NDArray, frame: Frame):
        """ Transform 3D points from camera frame to a given frame.

        Args:
            points (NDArray): An n x 3 array of the points to be transformed.
            frame (Frame): The frame into which the points are to be be transformed.

        Returns:
            NDArray: The n x 3 array of points in the given frame.
        """
        points_world = np.reshape(frame.matrix, (4, 4), 'F') @ np.vstack((points, np.ones(points.shape[1])))

        return points_world[:3, :]

    def transform_to_world(self, points: NDArray, camera: Camera):
        """Transform 3D points from camera frame to world frame.

        Args:
            points (NDArray): An n x 3 array of the points to be transformed.
            camera (Camera): The camera associated with the camera frame.

        Returns:
            NDArray: The n x 3 array of points in the world frame.
        """
        points_world = np.reshape(camera.origin.matrix, (4, 4), 'F') @ np.vstack((points, np.ones(points.shape[1])))

        return points_world[:3, :]
