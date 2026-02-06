from fastapi import APIRouter, File, UploadFile, Form
from fastapi.responses import JSONResponse
from controllers.freeman_chain_controller import FreemanChainController
import tempfile
import os

router = APIRouter(
    prefix="/freeman-chain",
    tags=["Freeman Chain Code"],
)

@router.post("/process", status_code=200)
async def freeman_chain_process(
    file: UploadFile = File(...),
    threshold: int = Form(128)
) -> JSONResponse:
    """
    Process image with Freeman Chain Code algorithm.
    
    Parameters:
    - file: Input image
    - threshold: Binarization threshold (0-255)
    
    Returns:
    - JSON with Freeman chain codes for each contour
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        return await FreemanChainController.process_image(tmp_path, threshold)
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)