from typing import Optional
from fastapi.exceptions import HTTPException
from utils.image_utils import ImageUtils
from PIL import Image
import numpy as np
import heapq


class Watershed:
    @staticmethod
    def process_image(
        image_path: str,
        gaussian_sigma: Optional[float] = 1.0,
    ) -> Image.Image:
        try:
            # Load image
            image = ImageUtils.load_image(image_path)            
            image_array = ImageUtils.pil_to_numpy(image)

            # Convert to grayscale if necessary
            if len(image_array.shape) == 3:
                image_array = np.array(ImageUtils.convert_to_grayscale(ImageUtils.numpy_to_pil(image_array)))

            # Generate Gaussian kernel
            gaussian_kernel = ImageUtils.generate_gaussian_kernel(size=5, sigma=gaussian_sigma)

            # Smooth image using Gaussian filter
            smoothed_image = ImageUtils.convolve2d(image_array, gaussian_kernel)

            # Compute gradient magnitude using Sobel operator
            sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
            sobel_y = np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]])

            gradient_x = ImageUtils.convolve2d(smoothed_image, sobel_x)
            gradient_y = ImageUtils.convolve2d(smoothed_image, sobel_y)

            gradient_magnitude = np.sqrt(gradient_x**2 + gradient_y**2)
            gradient_magnitude = (gradient_magnitude / np.max(gradient_magnitude) * 255).astype(np.uint8)

            # Apply Watershed algorithm
            markers = Watershed.create_markers(gradient_magnitude)
            labels = Watershed.watershed(gradient_magnitude, markers)

            # Create colored visualization of segments
            result_array = Watershed.visualize_segments(labels, image_array)
            result_image = ImageUtils.numpy_to_pil(result_array)
            
            return result_image
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    @staticmethod
    def create_markers(gradient_magnitude: np.ndarray) -> np.ndarray:
        """Create markers for watershed algorithm using Otsu thresholding."""
        # Use Otsu to find automatic threshold
        hist, bin_edges = np.histogram(gradient_magnitude.flatten(), bins=256, range=(0, 256))
        total_pixels = gradient_magnitude.size
        current_max, threshold = 0, 0
        sum_total, sum_foreground = 0, 0
        weight_background = 0

        for i in range(256):
            sum_total += i * hist[i]

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
            between_class_variance = weight_background * weight_foreground * (mean_background - mean_foreground) ** 2

            if between_class_variance > current_max:
                current_max = between_class_variance
                threshold = i

        # Create markers based on Otsu threshold
        markers = np.zeros_like(gradient_magnitude, dtype=np.int32)
        markers[gradient_magnitude < threshold * 0.5] = 1  # Background (sure)
        markers[gradient_magnitude > threshold * 1.5] = 2  # Foreground (sure)
        return markers
    
    @staticmethod
    def watershed(gradient_magnitude: np.ndarray, markers: np.ndarray) -> np.ndarray:
        height, width = gradient_magnitude.shape
        labels = np.copy(markers)
        priority_queue = []
        WATERSHED_LINE = -1

        # Initialize priority queue with marker pixels
        for y in range(height):
            for x in range(width):
                if markers[y, x] > 0:
                    heapq.heappush(priority_queue, (gradient_magnitude[y, x], (y, x)))

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        while priority_queue:
            _, (y, x) = heapq.heappop(priority_queue)

            for dy, dx in directions:
                ny, nx = y + dy, x + dx
                if 0 <= ny < height and 0 <= nx < width:
                    if labels[ny, nx] == 0:
                        # Check if neighbors belong to different regions
                        neighbor_labels = set()
                        for ddy, ddx in directions:
                            nny, nnx = ny + ddy, nx + ddx
                            if 0 <= nny < height and 0 <= nnx < width and labels[nny, nnx] > 0:
                                neighbor_labels.add(labels[nny, nnx])
                        
                        # If multiple labels around, mark as watershed
                        if len(neighbor_labels) > 1:
                            labels[ny, nx] = WATERSHED_LINE
                        elif len(neighbor_labels) == 1:
                            labels[ny, nx] = list(neighbor_labels)[0]
                            heapq.heappush(priority_queue, (gradient_magnitude[ny, nx], (ny, nx)))

        return labels
    
    @staticmethod
    def visualize_segments(labels: np.ndarray, original_image: np.ndarray) -> np.ndarray:
        """Create a colored visualization of watershed segments."""
        height, width = labels.shape
        result = np.zeros((height, width), dtype=np.uint8)
        
        # Mark watershed lines in white
        result[labels == -1] = 255
        
        # Assign grayscale values to different regions
        unique_labels = np.unique(labels[labels > 0])
        for i, label in enumerate(unique_labels):
            intensity = int((i + 1) * 255 / len(unique_labels))
            result[labels == label] = intensity
        
        return result
    