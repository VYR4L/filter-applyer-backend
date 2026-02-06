from fastapi.responses import JSONResponse
from services.freeman_chain_service import FreemanChainService


class FreemanChainController:
    @staticmethod
    async def process_image(
        image_path: str,
        threshold: int = 128
    ) -> JSONResponse:
        """
        Process image and return Freeman Chain Code.
        
        Args:
            image_path: Path to input image
            threshold: Threshold for binarization (0-255)
        
        Returns:
            JSON with chain codes for each contour
        """
        result = FreemanChainService.process_image(image_path, threshold)
        
        return JSONResponse(content={
            "total_contours": result["total_contours"],
            "contours": [
                {
                    "id": idx + 1,
                    "start_point": contour["start_point"],
                    "chain_code": contour["chain_code"],
                    "length": contour["length"]
                }
                for idx, contour in enumerate(result["contours"])
            ]
        })