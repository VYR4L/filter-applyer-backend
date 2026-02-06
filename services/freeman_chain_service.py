from fastapi.exceptions import HTTPException
from utils.image_utils import ImageUtils
import numpy as np
from typing import List, Tuple, Dict


class FreemanChainService:
    @staticmethod
    def process_image(
        image_path: str,
        threshold: int = 128
    ) -> Dict:
        """
        Process image and return Freeman Chain Code representation.
        Returns only chain codes data (no visualization).
        """
        try:
            # Load image
            image = ImageUtils.load_image(image_path)            
            image_array = ImageUtils.pil_to_numpy(image)

            # Convert to grayscale if necessary
            if len(image_array.shape) == 3:
                image_array = np.array(ImageUtils.convert_to_grayscale(ImageUtils.numpy_to_pil(image_array)))

            # Binarize image
            binary = (image_array > threshold).astype(np.uint8) * 255

            # Find all contours and generate chain codes
            contours_data = FreemanChainService.find_all_contours(binary)

            return {
                "contours": contours_data,
                "total_contours": len(contours_data)
            }
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    def find_all_contours(binary_image: np.ndarray) -> List[Dict]:
        """
        Find all contours in binary image and generate Freeman chain codes.
        """
        rows, cols = binary_image.shape
        visited = np.zeros_like(binary_image, dtype=bool)
        contours_data = []
        
        # Scan for contour starting points (top-left pixel of each object)
        for i in range(rows):
            for j in range(cols):
                if binary_image[i, j] == 255 and not visited[i, j]:
                    # Found new contour
                    chain_code, contour_pixels = FreemanChainService.trace_contour(
                        binary_image, (i, j), visited
                    )
                    
                    if len(chain_code) > 0:
                        contours_data.append({
                            "start_point": [int(i), int(j)],  # Convert to int for JSON
                            "chain_code": chain_code,
                            "length": len(chain_code)
                        })
        
        return contours_data
    
    @staticmethod
    def trace_contour(
        binary_image: np.ndarray, 
        start_pos: Tuple[int, int],
        visited: np.ndarray
    ) -> Tuple[List[int], List[Tuple[int, int]]]:
        """
        Trace a single contour using Freeman Chain Code (8-connectivity).
        
        Direction encoding (8-connected):
        7  0  1
        6  X  2
        5  4  3
        """
        # Freeman directions (8-connected, counter-clockwise from top)
        directions = [
            (-1, 0),   # 0: North
            (-1, 1),   # 1: North-East
            (0, 1),    # 2: East
            (1, 1),    # 3: South-East
            (1, 0),    # 4: South
            (1, -1),   # 5: South-West
            (0, -1),   # 6: West
            (-1, -1)   # 7: North-West
        ]
        
        rows, cols = binary_image.shape
        chain_code = []
        contour_pixels = [start_pos]
        current_pos = start_pos
        visited[current_pos] = True
        
        # Start search from direction 0 (top)
        start_dir = 0
        
        while True:
            found_next = False
            
            # Search in all 8 directions starting from current direction
            for offset in range(8):
                direction_idx = (start_dir + offset) % 8
                di, dj = directions[direction_idx]
                next_pos = (current_pos[0] + di, current_pos[1] + dj)
                
                # Check bounds and if it's part of the object
                if (0 <= next_pos[0] < rows and 
                    0 <= next_pos[1] < cols and
                    binary_image[next_pos] == 255):
                    
                    # Check if it's a boundary pixel (has at least one background neighbor)
                    if FreemanChainService.is_boundary_pixel(binary_image, next_pos):
                        # Check if we've returned to start (closed contour)
                        if len(chain_code) > 0 and next_pos == start_pos:
                            return chain_code, contour_pixels
                        
                        # Check if already visited (avoid infinite loops)
                        if not visited[next_pos]:
                            chain_code.append(direction_idx)
                            contour_pixels.append(next_pos)
                            visited[next_pos] = True
                            current_pos = next_pos
                            
                            # Next search starts from (current_dir + 6) % 8
                            # This follows the boundary efficiently
                            start_dir = (direction_idx + 6) % 8
                            found_next = True
                            break
            
            # If no next pixel found or visited too many pixels, stop
            if not found_next or len(chain_code) > rows * cols:
                break
        
        return chain_code, contour_pixels
    
    @staticmethod
    def is_boundary_pixel(binary_image: np.ndarray, pos: Tuple[int, int]) -> bool:
        """
        Check if pixel is on the boundary (has at least one background neighbor).
        """
        rows, cols = binary_image.shape
        i, j = pos
        
        # Check 8-connected neighbors
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                if di == 0 and dj == 0:
                    continue
                ni, nj = i + di, j + dj
                if 0 <= ni < rows and 0 <= nj < cols:
                    if binary_image[ni, nj] == 0:  # Found background neighbor
                        return True
        return False
