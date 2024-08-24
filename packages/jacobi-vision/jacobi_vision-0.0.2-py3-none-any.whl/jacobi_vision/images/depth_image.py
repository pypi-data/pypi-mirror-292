import numpy as np
from numpy.typing import NDArray

from jacobi import Camera
from .image import Image


class DepthImage(Image):
    """Class for depth images."""
    def to_depth_map(self, camera: Camera, scale: int = 1, cloud: list | None = None) -> tuple[list, float, float]:
        """Convert the depth image to a depth map.

        Returns:
            list: the depth values
            int: Size along the x-axis [m]
            int: Size along the y-axis [m]
        """
        if cloud is None:
            cloud = self.to_point_cloud(camera)
            cloud = cloud[:3, :].T

        grid_x = self.data.shape[1] // scale
        grid_y = self.data.shape[0] // scale

        maxs = np.max(cloud, axis=0)
        mins = np.min(cloud, axis=0)
        max_depth = maxs[2]
        dim_x = maxs[0] - mins[0]
        dim_y = maxs[1] - mins[1]
        position = mins + 0.5 * (maxs - mins)
        depths = cloud2map(cloud, grid_x, grid_y, dim_x, dim_y, position=position, max_depth=max_depth)

        return depths, dim_x, dim_y

    def to_point_cloud(self, camera: Camera) -> NDArray:
        """Convert the depth image to a point cloud in the camera frame.

        Args:
            camera (CameraDriver): A camera driver that provides the intrinsics.

        Returns:
            NDArray: An n x 3 array of points in the camera frame.
        """
        pixels = [[j, i, self.data[i, j]] for i in range(self.data.shape[0]) for j in range(self.data.shape[1])]
        pixels = np.array(pixels).T

        return self.deproject(pixels, camera)


def cloud2map(
    cloud: NDArray,
    gridx: int,
    gridy: int,
    dimx: float,
    dimy: float,
    cellx: int = -1,
    celly: int = -1,
    position: tuple[float, float] = (0, 0),
    max_depth: float = -1.0,
):
    """Convert point cloud to depth map.

    Args:
        cloud (NDArray): The n x 3 array of points.
        gridx (int): Number of grid cells along x-dimension.
        gridy (int): Number of grid cells along y-dimension.
        dimx (float): Size of grid along x-dimension.
        dimy (float): Size of grid along y-dimension.
        cellx (float, optional): Size of cell along x-dimension.
        celly (float, optional): Size of cell along x-dimension.
        position (list[float, float], optional): Position (center) of the depth map.
        max_depth (float, optional): Max depth value.

    Returns:
        NDArray: The depth map.
        int: Size along the x-axis [m].
        int: Size along the y-axis [m].
    """
    depths = np.ones((gridy, gridx)) * max_depth
    start = [position[0] - 0.5 * dimx, position[1] + 0.5 * dimy]
    if cellx == -1 and celly == -1:
        cellx = dimx / gridx
        celly = dimy / gridy

    for pt in cloud:
        x = (pt[0] - start[0]) / cellx
        y = (start[1] - pt[1]) / celly
        x = int(np.floor(x))
        y = int(np.floor(y))
        if y < depths.shape[0] and x < depths.shape[1] and pt[2] < depths[y, x]:
            depths[y, x] = pt[2]

    return depths
