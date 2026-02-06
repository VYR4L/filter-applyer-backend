from fastapi import APIRouter, File, UploadFile
from fastapi.responses import Response
from controllers.otus_method_controller import OtusMethodController
import tempfile
import os


router = APIRouter(
    prefix="/otsu-method",
    tags=["Otsu's Method Thresholding"],
)

@router.post("/process", status_code=200)
async def otsu_method_process(
    file: UploadFile = File(...),
) -> Response:
    """
    Apply Otsu's automatic thresholding method.
    
    Otsu's method automatically calculates the optimal threshold
    value that separates foreground from background by maximizing
    the between-class variance.
    
    Parameters:
    - file: Input image
    
    Returns:
    - Binary image (black and white)
    """
    # Save uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        return await OtusMethodController.process_image(
            tmp_path
        )
    finally:
        # Clean up the temporary file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)