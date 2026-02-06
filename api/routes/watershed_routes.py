from fastapi import APIRouter, File, UploadFile, Form
from fastapi.responses import Response
from controllers.watershed_controller import WatershedController
import tempfile
import os


router = APIRouter(
    prefix="/watershed",
    tags=["Watershed Segmentation"],
)

@router.post("/process", status_code=200)
async def watershed_process(
    file: UploadFile = File(...),
    gaussian_sigma: float = Form(1.0),
) -> Response:
    """
    Segment image using Watershed algorithm.
    
    The watershed algorithm treats the image as a topographic surface
    and segments it by simulating flooding from regional minima.
    
    Parameters:
    - file: Input image
    - gaussian_sigma: Smoothing parameter to reduce noise (default: 1.0)
    
    Returns:
    - Segmented image with regions in different intensities
    """
    # Save uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        return await WatershedController.process_image(
            tmp_path,
            gaussian_sigma,
        )
    finally:
        # Clean up the temporary file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)