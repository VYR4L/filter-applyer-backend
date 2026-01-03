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
        result_image = MarrHildrethService.process_image(
            image_path, sigma, threshold
        )
        image_bytes = ImageUtils.image_to_bytes(result_image)
        return Response(content=image_bytes, media_type="image/png")
