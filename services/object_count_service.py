from fastapi.exceptions import HTTPException
from utils.image_utils import ImageUtils
from services.freeman_chain_service import FreemanChainService
import numpy as np


class ObjectCountService:
    @staticmethod
    def process_image(
        image_path: str,
        threshold: int = 128,
        method: str = "ccl"
    ) -> dict:
        """
        Count objects in image using CCL or Freeman Chain Code.
        
        Args:
            image_path: Path to input image
            threshold: Binarization threshold (0-255)
            method: "ccl" (Connected Component Labeling) or "freeman" (Freeman Chain Code)
        
        Returns:
            Dictionary with object count and method-specific information
        """
        try:
            if method == "freeman":
                # Use Freeman Chain Code to count contours
                result = FreemanChainService.process_image(image_path, threshold)
                
                return {
                    "object_count": result["total_contours"],
                    "threshold_used": threshold,
                    "method": "freeman_chain_code",
                    "contours": result["contours"]  # Include detailed contour data
                }
            
            elif method == "ccl":
                # Use Connected Component Labeling (faster and simpler)
                image = ImageUtils.load_image(image_path)            
                image_array = ImageUtils.pil_to_numpy(image)

                # Convert to grayscale if necessary
                if len(image_array.shape) == 3:
                    image_array = np.array(ImageUtils.convert_to_grayscale(ImageUtils.numpy_to_pil(image_array)))

                # Binarize image
                binary = (image_array > threshold).astype(np.uint8)

                # Apply Connected Component Labeling
                labeled_image = ImageUtils.label_connected_components(binary)

                # Count unique labels (objects)
                unique_labels = np.unique(labeled_image)
                object_count = len(unique_labels) - 1 if 0 in unique_labels else len(unique_labels)
                
                return {
                    "object_count": int(object_count),
                    "threshold_used": threshold,
                    "method": "connected_component_labeling"
                }
            
            else:
                raise ValueError(f"Invalid method: {method}. Choose 'ccl' or 'freeman'")
        
        except ValueError as ve:
            raise HTTPException(status_code=400, detail=str(ve))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))