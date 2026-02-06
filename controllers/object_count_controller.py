from fastapi.responses import JSONResponse
from services.object_count_service import ObjectCountService


class ObjectCountController:
    @staticmethod
    async def process_image(
        image_path: str,
        threshold: int = 128,
        method: str = "ccl"
    ) -> JSONResponse:
        """
        Count objects in image.
        
        Args:
            image_path: Path to input image
            threshold: Threshold for binarization (0-255)
        
        Returns:
            JSON with object count
        """
        result = ObjectCountService.process_image(image_path, threshold, method)
        return JSONResponse(content=result)