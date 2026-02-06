from typing import Optional
from fastapi.exceptions import HTTPException
from utils.image_utils import ImageUtils
from PIL import Image
import numpy as np


class CannyService:
    @staticmethod
    def process_image(
        image_path: str,
        sigma: float,
        low_threshold: float,
        high_threshold: float
    ) -> Image.Image:
        try:
            # Load image
            image = ImageUtils.load_image(image_path)            
            image_array = ImageUtils.pil_to_numpy(image)

            # Apply Canny edge detection
            threshold, weak, strong = CannyService.canny_edge_detection(
                image_array, sigma, low_threshold, high_threshold
            )

            histerysis_image = CannyService.hysteresis(threshold, weak, strong)

            result_image = ImageUtils.numpy_to_pil(histerysis_image)
            
            return result_image
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    @staticmethod
    def canny_edge_detection(
        image_array: np.ndarray,
        sigma: float,
        low_threshold: float,
        high_threshold: float,
        ) -> np.ndarray:
        """
        Detect edges using Canny algorithm.
        
        Args:
            image_array: Input grayscale image
            sigma: Standard deviation for Gaussian smoothing
            low_threshold: Lower threshold for hysteresis (0-1)
            high_threshold: Upper threshold for hysteresis (0-1)
        
        Returns:
            Binary edge map
        """
        if image_array is None:
            raise ValueError("Input image array cannot be None")
        
        # Convert to grayscale if necessary
        if len(image_array.shape) == 3:
            image_array = np.array(ImageUtils.convert_to_grayscale(ImageUtils.numpy_to_pil(image_array)))

        # Normalize image
        image_array = image_array.astype(np.float32) / 255.0

        gaussian = ImageUtils.generate_gaussian_kernel(size=5, sigma=sigma)

        # Convolve image with Gaussian kernel
        smoothed_image = ImageUtils.convolve2d(image_array, gaussian)

        gradient_magnitude, angle = ImageUtils.sobel_filters(smoothed_image)

        non_max_suppressed = ImageUtils.non_maximum_suppression(gradient_magnitude, angle)

        high_threshold_value = image_array.max() * high_threshold
        low_threshold_value = high_threshold_value * low_threshold

        rows, cols = image_array.shape
        result = np.zeros((rows, cols), dtype=np.uint8)

        weak = np.uint8(25)
        strong = np.uint8(255)

        # Numpy vectorized for fast thresholding
        strong_i, strong_j = np.where(non_max_suppressed >= high_threshold_value)
        zeros_i, zeros_j = np.where(non_max_suppressed < low_threshold_value)  # Used on default implementation, but not here
        weak_i, weak_j = np.where(
            (non_max_suppressed <= high_threshold_value) &
            (non_max_suppressed >= low_threshold_value))

        result[strong_i, strong_j] = strong
        result[weak_i, weak_j] = weak

        return result, weak, strong
    
    @staticmethod
    def hysteresis(image: np.ndarray, weak: int, strong: int) -> np.ndarray:
        """Applies hysteresis to track edges."""
        rows, cols = image.shape
        for i in range(1, rows - 1):
            for j in range(1, cols - 1):
                if image[i, j] == weak:
                    # Check 8-connected neighbors for strong edge
                    if ((image[i + 1, j - 1] == strong) or (image[i + 1, j] == strong) or (image[i + 1, j + 1] == strong)
                        or (image[i, j - 1] == strong) or (image[i, j + 1] == strong)
                        or (image[i - 1, j - 1] == strong) or (image[i - 1, j] == strong) or (image[i - 1, j + 1] == strong)):
                        image[i, j] = strong
                    else:
                        image[i, j] = 0
        return image