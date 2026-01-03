from fastapi import APIRouter, File, UploadFile, Form
from fastapi.responses import Response
from controllers.marr_hildreth_controller import MarrHildrethController
from typing import Optional
import tempfile
import os

router = APIRouter(
    prefix="/marr-hildreth",
    tags=["Marr-Hildreth Edge Detection"],
)

@router.post("/process", status_code=200)
async def marr_hildreth_process(
    file: UploadFile = File(...),
    sigma: float = Form(1.0),
    threshold: Optional[float] = Form(0.1)
) -> Response:
    # Save uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        return await MarrHildrethController.process_image_controller(
            tmp_path, sigma, threshold
        )
    finally:
        # Clean up the temporary file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)