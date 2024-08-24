import base64
import cv2

from .image import Image


class ColorImage(Image):
    """Class for color images."""

    def encode(self) -> str:
        """Encode as string for Jacobi Studio visualization.

        Returns:
            str: The image encoded as a base64 string.
        """
        _, buffer = cv2.imencode('.png', cv2.cvtColor(self.data, cv2.COLOR_RGB2BGRA))
        return base64.b64encode(buffer).decode()
