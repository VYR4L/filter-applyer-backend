from fastapi import APIRouter, File, UploadFile, Form
from fastapi.responses import Response
from controllers.canny_controller import CannyController
from typing import Optional
import tempfile
import os


router = APIRouter(
    prefix="/canny",
    tags=["Canny Edge Detection"],
)

@router.post("/process", status_code=200)
async def canny_process(
    file: UploadFile = File(...),
    sigma: float = Form(1.0),
    low_threshold: float = Form(0.1),
    high_threshold: float = Form(0.3)
) -> Response:
    """
    Detect edges using Canny algorithm.
    
    The Canny edge detector is a multi-stage algorithm that detects
    a wide range of edges with good localization and minimal response.
    
    Parameters:
    - file: Input image
    - sigma: Gaussian smoothing parameter (default: 1.0)
    - low_threshold: Lower threshold for hysteresis (0-1, default: 0.1)
    - high_threshold: Upper threshold for hysteresis (0-1, default: 0.3)
    
    Returns:
    - Binary image with detected edges
    """
    # Save uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        return await CannyController.process_image_controller(
            tmp_path, sigma, low_threshold, high_threshold
        )
    finally:
        # Clean up the temporary file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)