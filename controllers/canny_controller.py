from fastapi.responses import Response
from services.canny_service import CannyService
from utils.image_utils import ImageUtils
from typing import Optional


class CannyController:
    @staticmethod
    async def process_image_controller(
        image_path: str,
        sigma: float,
        low_threshold: float,
        high_threshold: float
    ) -> Response:
        """
        Process image with Canny edge detection.
        
        Args:
            image_path: Path to input image
            sigma: Standard deviation for Gaussian smoothing
            low_threshold: Lower threshold for hysteresis (0-1)
            high_threshold: Upper threshold for hysteresis (0-1)
        
        Returns:
            Edge detected image as PNG response
        """
        result_image = CannyService.process_image(
            image_path, sigma, low_threshold, high_threshold
        )
        image_bytes = ImageUtils.image_to_bytes(result_image)
        return Response(content=image_bytes, media_type="image/png")