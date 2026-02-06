from fastapi.exceptions import HTTPException
from utils.image_utils import ImageUtils
from PIL import Image
import numpy as np


class SegmentationFilterService:
    @staticmethod
    def process_image(image_path: str) -> Image.Image:
        """
        Apply intensity-based segmentation to image.
        Maps intensity ranges to specific values according to predefined table.
        
        Mapping table:
        - [0, 50]     -> 25
        - [51, 100]   -> 75
        - [101, 150]  -> 125
        - [151, 200]  -> 175
        - [201, 255]  -> 255
        
        Args:
            image_path: Path to input image
        
        Returns:
            Segmented image
        """
        try:
            # Load image
            image = ImageUtils.load_image(image_path)
            image_array = ImageUtils.pil_to_numpy(image)

            # Convert to grayscale if necessary
            if len(image_array.shape) == 3:
                image_array = np.array(
                    ImageUtils.convert_to_grayscale(ImageUtils.numpy_to_pil(image_array))
                )

            # Apply segmentation
            segmented = SegmentationFilterService.segment_by_intensity(image_array)
            
            # Convert back to PIL Image
            result_image = ImageUtils.numpy_to_pil(segmented)
            
            return result_image
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    def segment_by_intensity(image_array: np.ndarray) -> np.ndarray:
        """
        Segment image by intensity ranges.
        
        Args:
            image_array: Grayscale image array (0-255)
        
        Returns:
            Segmented image with discrete intensity levels
        """
        # Create output array
        segmented = np.zeros_like(image_array, dtype=np.uint8)
        
        # Define intensity mapping table
        # Format: (min_value, max_value, new_value)
        intensity_map = [
            (0, 50, 25),
            (51, 100, 75),
            (101, 150, 125),
            (151, 200, 175),
            (201, 255, 255)
        ]
        
        # Apply segmentation based on ranges
        for min_val, max_val, new_val in intensity_map:
            mask = (image_array >= min_val) & (image_array <= max_val)
            segmented[mask] = new_val
        
        return segmented