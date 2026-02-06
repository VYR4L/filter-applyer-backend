from fastapi import APIRouter, File, UploadFile, Form
from fastapi.responses import Response
from controllers.box_filter_controller import BoxFilterController
import tempfile
import os

router = APIRouter(
    prefix="/box-filter",
    tags=["Box Filter"],
)

@router.post("/process", status_code=200)
async def box_filter_process(
    file: UploadFile = File(...),
    box_size: int = Form(3),  # Deixei o usuário escolher o tamanho da caixa
) -> Response:
    """
    Apply box filter (mean filter) to reduce noise in image.
    
    The box filter replaces each pixel with the mean of its neighbors
    within a box of specified size. Good for general noise reduction.
    
    Parameters:
    - file: Input image
    - box_size: Size of the box kernel (must be odd, default: 3)
    
    Returns:
    - Smoothed image with reduced noise
    """
    # Save uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        return await BoxFilterController.process_image(
            tmp_path,
            box_size,
        )
    finally:
        # Clean up the temporary file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)