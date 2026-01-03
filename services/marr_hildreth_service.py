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
    def convolve2d(image: np.ndarray, kernel: np.ndarray) -> np.ndarray:
        image_height, image_width = image.shape
        kernel_height, kernel_width = kernel.shape
        pad_height = kernel_height // 2
        pad_width = kernel_width // 2

        # Pad the image to handle borders
        padded_image = np.pad(image, ((pad_height, pad_height), (pad_width, pad_width)), mode='edge')
        convolved_image = np.zeros_like(image)

        # Perform convolution
        for i in range(image_height):
            for j in range(image_width):
                region = padded_image[i:i + kernel_height, j:j + kernel_width]
                convolved_value = np.sum(region * kernel)
                convolved_image[i, j] = convolved_value

        return convolved_image
        
    @staticmethod
    def marr_hildreth_edge_detection(image_array: np.ndarray, sigma: float, threshold: float = None) -> np.ndarray:
        if image_array is None:
            raise ValueError("Input image array cannot be None")
        
        # Convert to grayscale if necessary
        if len(image_array.shape) == 3:
            image_array = np.array(ImageUtils.convert_to_grayscale(ImageUtils.numpy_to_pil(image_array)))

        # Normalize image
        image_array = image_array.astype(np.float32) / 255.0

        # Create Gaussian kernel
        size = int(2 * np.ceil(3 * sigma) + 1)

        x, y = np.meshgrid(
            np.linspace(-size // 2, size // 2, size),
            np.linspace(-size // 2, size // 2, size)
        )

        # Gaussian function
        normalizer = -1 / (np.pi * sigma**4)
        first_term = 1 - (x**2 + y**2) / (2 * sigma**2)  # Laplacian component
        second_term = np.exp(-(x**2 + y**2) / (2 * sigma**2))  # Gaussian component
        gaussian = normalizer * first_term * second_term
        
        gaussian -= gaussian.mean()  # Normalize kernel to have zero sum

        # Convolve image with Gaussian kernel
        filter_2d = MarrHildrethService.convolve2d(image_array, gaussian)

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
