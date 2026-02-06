from fastapi.responses import Response
from services.box_filter_service import BoxFilterService
from utils.image_utils import ImageUtils
from typing import Optional

class BoxFilterController:
    @staticmethod
    async def process_image(
        image_path: str,
        box_size: Optional[int] = 3,
    ) -> Response:
        """
        Process image with box filter.
        
        Args:
            image_path: Path to input image
            box_size: Size of the box kernel (default: 3)
        
        Returns:
            Filtered image as PNG response
        """
        result_image = BoxFilterService.process_image(image_path, box_size)
        image_bytes = ImageUtils.image_to_bytes(result_image)
        return Response(content=image_bytes, media_type="image/png")