from typing import Optional
from fastapi.exceptions import HTTPException
from utils.image_utils import ImageUtils
from PIL import Image
import numpy as np


class OtsuMethodService:
    @staticmethod
    def process_image(
        image_path: str,
    ) -> Image.Image:
        try:
            # Load image
            image = ImageUtils.load_image(image_path)            
            image_array = ImageUtils.pil_to_numpy(image)

            # Apply Otsu's method
            thresholded_image = OtsuMethodService.otsu_thresholding(image_array)

            result_image = ImageUtils.numpy_to_pil(thresholded_image)
            
            return result_image
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    @staticmethod
    def otsu_thresholding(
        image_array: np.ndarray,
        ) -> np.ndarray:
        if image_array is None:
            raise ValueError("Input image array cannot be None")
        
        # Convert to grayscale if necessary
        if len(image_array.shape) == 3:
            image_array = np.array(ImageUtils.convert_to_grayscale(ImageUtils.numpy_to_pil(image_array)))

        # Work with uint8 (0-255) directly
        if image_array.dtype != np.uint8:
            image_array = image_array.astype(np.uint8)

        # Compute histogram
        hist, bin_edges = np.histogram(image_array.flatten(), bins=256, range=(0, 256))

        total_pixels = image_array.size
        current_max, threshold = 0, 0
        sum_total, sum_foreground = 0, 0
        weight_background, weight_foreground = 0, 0

        # Calculate sum of all intensity values
        for i in range(256):
            sum_total += i * hist[i]

        # Find optimal threshold
        for i in range(256):
            weight_background += hist[i]
            if weight_background == 0:
                continue
            
            weight_foreground = total_pixels - weight_background
            if weight_foreground == 0:
                break

            sum_foreground += i * hist[i]

            mean_background = sum_foreground / weight_background
            mean_foreground = (sum_total - sum_foreground) / weight_foreground

            # Calculate between-class variance
            between_class_variance = weight_background * weight_foreground * (mean_background - mean_foreground) ** 2

            if between_class_variance > current_max:
                current_max = between_class_variance
                threshold = i

        # Apply threshold to create binary image (0 or 255)
        binary_image = np.where(image_array >= threshold, 255, 0).astype(np.uint8)

        return binary_image