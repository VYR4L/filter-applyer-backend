from fastapi.responses import Response
from services.marr_hildreth_service import MarrHildrethService
from utils.image_utils import ImageUtils
from typing import Optional


class MarrHildrethController:
    @staticmethod
    async def process_image_controller(
        image_path: str,
        sigma: float,
        threshold: Optional[float]
    ) -> Response:
        """
        Process image with Marr-Hildreth edge detection.
        
        Args:
            image_path: Path to input image
            sigma: Standard deviation for Laplacian of Gaussian
            threshold: Threshold for zero-crossing detection
        
        Returns:
            Edge detected image as PNG response
        """
        result_image = MarrHildrethService.process_image(
            image_path, sigma, threshold
        )
        image_bytes = ImageUtils.image_to_bytes(result_image)
        return Response(content=image_bytes, media_type="image/png")
