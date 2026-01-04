from fastapi.responses import Response
from services.watershed_service import Watershed
from utils.image_utils import ImageUtils


class WatershedController:
    @staticmethod
    async def process_image(
        image_path: str,
        gaussian_sigma: float = 1.0,
    ) -> Response:
        result_image = Watershed.process_image(image_path, gaussian_sigma)
        image_bytes = ImageUtils.image_to_bytes(result_image)
        return Response(content=image_bytes, media_type="image/png")