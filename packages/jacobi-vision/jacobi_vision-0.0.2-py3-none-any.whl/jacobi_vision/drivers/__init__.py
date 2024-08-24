all_drivers = []

try:
    from jacobi_phoxi_driver import PhoXiCameraDriver  # noqa: F401
    all_drivers.append('PhoXiCameraDriver')
except ModuleNotFoundError:
    pass

try:
    from jacobi_realsense_driver import RealsenseCameraDriver  # noqa: F401
    all_drivers.append('RealsenseCameraDriver')
except ModuleNotFoundError:
    pass

try:
    from jacobi_simulated_camera_driver import SimulatedCameraDriver  # noqa: F401
    all_drivers.append('SimulatedCameraDriver')
except ModuleNotFoundError:
    pass

__all__ = all_drivers
