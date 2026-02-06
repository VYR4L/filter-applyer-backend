from fastapi import APIRouter, File, UploadFile, Form
from fastapi.responses import JSONResponse
from controllers.object_count_controller import ObjectCountController
import tempfile
import os

router = APIRouter(
    prefix="/object-count",
    tags=["Object Count"],
)

@router.post("/process", status_code=200)
async def object_count_process(
    file: UploadFile = File(...),
    threshold: int = Form(128),
    method: str = Form("ccl", description="Method: 'ccl' or 'freeman'")
) -> JSONResponse:
    """
    Count objects in image.
    
    Parameters:
    - file: Input image
    - threshold: Binarization threshold (0-255)
    - method: Counting method
        - "ccl": Connected Component Labeling (faster, simple count)
        - "freeman": Freeman Chain Code (slower, includes contour details)
    
    Returns:
    - JSON with object count and method-specific information
    
    Example responses:
    
    CCL method:
    ```json
    {
        "object_count": 5,
        "threshold_used": 128,
        "method": "connected_component_labeling"
    }
    ```
    
    Freeman method:
    ```json
    {
        "object_count": 5,
        "threshold_used": 128,
        "method": "freeman_chain_code",
        "contours": [
            {
                "start_point": [10, 20],
                "chain_code": [0, 0, 1, 2, 3],
                "length": 5
            }
        ]
    }
    ```
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        return await ObjectCountController.process_image(tmp_path, threshold, method)
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)