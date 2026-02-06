from fastapi.responses import Response
from services.otsu_method_service import OtsuMethodService
from utils.image_utils import ImageUtils


class OtusMethodController:
    @staticmethod
    async def process_image(
        image_path: str,
    ) -> Response:
        """
        Process image with Otsu's automatic thresholding.
        
        Args:
            image_path: Path to input image
        
        Returns:
            Binary image as PNG response
        """
        result_image = OtsuMethodService.process_image(image_path)
        image_bytes = ImageUtils.image_to_bytes(result_image)
        return Response(content=image_bytes, media_type="image/png")
