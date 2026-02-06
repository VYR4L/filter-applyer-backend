from fastapi.responses import Response
from services.segmentation_filter_service import SegmentationFilterService
from utils.image_utils import ImageUtils


class SegmentationFilterController:
    @staticmethod
    async def process_image(image_path: str) -> Response:
        """
        Process image with intensity-based segmentation.
        
        Args:
            image_path: Path to input image
        
        Returns:
            Segmented image as PNG
        """
        result_image = SegmentationFilterService.process_image(image_path)
        image_bytes = ImageUtils.image_to_bytes(result_image)
        return Response(content=image_bytes, media_type="image/png")