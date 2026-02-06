from fastapi import APIRouter, File, UploadFile
from fastapi.responses import Response
from controllers.segmentation_filter_controller import SegmentationFilterController
import tempfile
import os

router = APIRouter(
    prefix="/segmentation",
    tags=["Intensity Segmentation"],
)

@router.post("/process", status_code=200)
async def segmentation_process(
    file: UploadFile = File(...)
) -> Response:
    """
    Apply intensity-based segmentation to image.
    
    Segments image into 5 discrete intensity levels based on ranges:
    - [0-50]     → 25  (Very Dark)
    - [51-100]   → 75  (Dark)
    - [101-150]  → 125 (Medium)
    - [151-200]  → 175 (Light)
    - [201-255]  → 255 (Very Light)
    
    Parameters:
    - file: Input image
    
    Returns:
    - Segmented image with 5 intensity levels
    """
    # Save uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        return await SegmentationFilterController.process_image(tmp_path)
    finally:
        # Clean up the temporary file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)