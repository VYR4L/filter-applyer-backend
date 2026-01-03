from typing import Optional
from fastapi.exceptions import HTTPException
from utils.image_utils import ImageUtils
from PIL import Image
import numpy as np


class MarrHildrethService:
    @staticmethod
    def process_image(
        image_path: str,
        sigma: float,
        threshold: Optional[float]
    ) -> Image.Image:
        try:
            # Load image
            image = ImageUtils.load_image(image_path)            
            image_array = ImageUtils.pil_to_numpy(image)

            # Apply Marr-Hildreth edge detection
            edges = MarrHildrethService.marr_hildreth_edge_detection(
                image_array, sigma, threshold
            )
            result_image = ImageUtils.numpy_to_pil(edges)
            
            return result_image
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    @staticmethod
    def marr_hildreth_edge_detection(image_array: np.ndarray, sigma: float, threshold: float = None) -> np.ndarray:
        if image_array is None:
            raise ValueError("Input image array cannot be None")
        
        # Convert to grayscale if necessary
        if len(image_array.shape) == 3:
            image_array = np.array(ImageUtils.convert_to_grayscale(ImageUtils.numpy_to_pil(image_array)))

        # Normalize image
        image_array = image_array.astype(np.float32) / 255.0

        gaussian = ImageUtils.generate_gaussian_kernel(size=0, sigma=sigma)
        
        gaussian -= gaussian.mean()  # Normalize kernel to have zero sum

        # Convolve image with Gaussian kernel
        filter_2d = ImageUtils.convolve2d(image_array, gaussian)

        # Zero-crossing detection
        rows, cols = filter_2d.shape
        zero_crossing_image = np.zeros((rows, cols), dtype=np.uint8)

        # Apply threshold if provided
        if threshold is not None:
            for i in range(1, rows - 1):
                for j in range(1, cols - 1):
                    patch = filter_2d[i-1:i+2, j-1:j+2]
                    min_val = patch.min()  # Minimum value in the patch
                    max_val = patch.max()  # Maximum value in the patch

                    # Check for zero-crossing with threshold
                    if min_val < 0 and max_val > 0 and (max_val - min_val) > threshold:
                        zero_crossing_image[i, j] = 255

        else:
            raise ValueError("Threshold must be provided for zero-crossing detection.")
        
        return zero_crossing_image
