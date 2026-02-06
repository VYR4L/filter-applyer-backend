from typing import Optional
from fastapi.exceptions import HTTPException
from utils.image_utils import ImageUtils
from PIL import Image
import numpy as np

class BoxFilterService:
    @staticmethod
    def process_image(
        image_path: str,
        box_size: Optional[int] = 3,
    ) -> Image.Image:
        try:
            # Load image
            image = ImageUtils.load_image(image_path)            
            image_array = ImageUtils.pil_to_numpy(image)

            # Convert to grayscale if necessary
            if len(image_array.shape) == 3:
                image_array = np.array(ImageUtils.convert_to_grayscale(ImageUtils.numpy_to_pil(image_array)))

            # Apply box filter
            filtered_image_array = BoxFilterService.box_filter(image_array, box_size)

            result_image = ImageUtils.numpy_to_pil(filtered_image_array)
            
            return result_image
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    @staticmethod
    def box_filter(image_array: np.ndarray, box_size: int) -> np.ndarray:
        """
        Apply box filter (mean filter) to image.
        
        Args:
            image_array: Input grayscale image
            box_size: Size of the box kernel (must be odd)
        
        Returns:
            Filtered image with reduced noise
        """
        pad_size = box_size // 2
        padded_image = np.pad(image_array, pad_size, mode='edge')
        filtered_image = np.zeros_like(image_array)

        for i in range(image_array.shape[0]):
            for j in range(image_array.shape[1]):
                region = padded_image[i:i + box_size, j:j + box_size]
                filtered_image[i, j] = np.mean(region)

        return filtered_image