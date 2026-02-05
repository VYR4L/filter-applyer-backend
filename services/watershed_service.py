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

            # Apply Gaussian smoothing to reduce noise
            if gaussian_sigma > 0:
                gaussian_kernel = ImageUtils.generate_gaussian_kernel(size=5, sigma=gaussian_sigma)
                image_array = ImageUtils.convolve2d(image_array, gaussian_kernel)

            # Compute gradient magnitude using Sobel operator
            sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float32)
            sobel_y = np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]], dtype=np.float32)

            gradient_x = ImageUtils.convolve2d(image_array.astype(np.float32), sobel_x)
            gradient_y = ImageUtils.convolve2d(image_array.astype(np.float32), sobel_y)

            gradient_magnitude = np.hypot(gradient_x, gradient_y)

            # Create markers and apply watershed
            markers = Watershed.create_markers(gradient_magnitude)
            labels = Watershed.watershed(gradient_magnitude, markers)

            # Create visualization
            result_array = Watershed.visualize_segments(labels)
            result_image = ImageUtils.numpy_to_pil(result_array)
            
            return result_image
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    @staticmethod
    def create_markers(gradient_magnitude: np.ndarray) -> np.ndarray:
        """
        Create markers (seeds) for watershed algorithm.
        Markers are regions with low gradient (homogeneous areas).
        """
        # Normalize gradient to 0-255 for threshold
        grad_norm = ((gradient_magnitude / (gradient_magnitude.max() if gradient_magnitude.max() > 0 else 1)) * 255).astype(np.uint8)
        
        # Low gradient pixels are potential markers (basins)
        # Threshold: pixels with gradient < 20 are considered markers
        markers_mask = (grad_norm < 20).astype(np.uint8)
        
        rows, cols = markers_mask.shape
        labels = np.zeros((rows, cols), dtype=np.int32)
        visited = np.zeros((rows, cols), dtype=bool)
        current_label = 1
        
        # Label connected components of markers using flood-fill
        for i in range(rows):
            for j in range(cols):
                if markers_mask[i, j] == 1 and not visited[i, j]:
                    # Start flood-fill for this component
                    stack = [(i, j)]
                    while stack:
                        ci, cj = stack.pop()
                        if 0 <= ci < rows and 0 <= cj < cols and markers_mask[ci, cj] == 1 and not visited[ci, cj]:
                            visited[ci, cj] = True
                            labels[ci, cj] = current_label
                            
                            # Add 4-connected neighbors
                            for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                                ni, nj = ci + di, cj + dj
                                if 0 <= ni < rows and 0 <= nj < cols and not visited[ni, nj]:
                                    stack.append((ni, nj))
                    
                    current_label += 1
        
        return labels
    
    @staticmethod
    def watershed(gradient_magnitude: np.ndarray, markers: np.ndarray) -> np.ndarray:
        """
        Watershed algorithm using immersion simulation with priority queue.
        Based on Meyer's flooding algorithm.
        """
        rows, cols = gradient_magnitude.shape
        labels = markers.copy()
        in_queue = np.zeros((rows, cols), dtype=bool)
        priority_queue = []
        WATERSHED_LINE = -1
        
        # Helper function to get 4-connected neighbors
        def get_neighbors(i, j):
            for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ni, nj = i + di, j + dj
                if 0 <= ni < rows and 0 <= nj < cols:
                    yield ni, nj
        
        # Initialize priority queue with neighbors of marked pixels (seeds)
        for i in range(rows):
            for j in range(cols):
                if labels[i, j] > 0:  # If pixel is a seed
                    for ni, nj in get_neighbors(i, j):
                        if labels[ni, nj] == 0 and not in_queue[ni, nj]:
                            # Enqueue unlabeled neighbors with gradient as priority
                            heapq.heappush(priority_queue, (float(gradient_magnitude[ni, nj]), ni, nj, labels[i, j]))
                            in_queue[ni, nj] = True
        
        # Process queue in order of increasing gradient (altitude)
        while priority_queue:
            grad_val, i, j, source_label = heapq.heappop(priority_queue)
            
            # Skip if already labeled
            if labels[i, j] != 0:
                continue
            
            # Check labels of neighbors
            neighbor_labels = set()
            for ni, nj in get_neighbors(i, j):
                label = labels[ni, nj]
                if label > 0:  # Positive labels only (ignore watershed lines)
                    neighbor_labels.add(label)
            
            if len(neighbor_labels) == 0:
                # No labeled neighbors yet: assign source label
                labels[i, j] = source_label
            elif len(neighbor_labels) == 1:
                # All labeled neighbors belong to the same basin
                labels[i, j] = neighbor_labels.pop()
            else:
                # Conflict: neighbors from different basins -> watershed line
                labels[i, j] = WATERSHED_LINE
            
            # Enqueue unlabeled neighbors of this pixel
            if labels[i, j] > 0:  # Only propagate if not a watershed line
                for ni, nj in get_neighbors(i, j):
                    if labels[ni, nj] == 0 and not in_queue[ni, nj]:
                        heapq.heappush(priority_queue, (float(gradient_magnitude[ni, nj]), ni, nj, labels[i, j]))
                        in_queue[ni, nj] = True
        
        return labels
    
    @staticmethod
    def visualize_segments(labels: np.ndarray) -> np.ndarray:
        """
        Create visualization: map positive labels to grayscale, watershed lines to black.
        """
        rows, cols = labels.shape
        output = np.zeros((rows, cols), dtype=np.uint8)
        
        max_label = labels.max()
        if max_label > 0:
            # Map labels 1..max_label to intensities 1..255
            for label in range(1, max_label + 1):
                intensity = int((label / max_label) * 255)
                output[labels == label] = intensity
        
        # Watershed lines (label == -1) remain black (0)
        
        return output
