from PIL import Image
import numpy as np
from io import BytesIO


class ImageUtils:
    @staticmethod
    def load_image(path: str) -> Image.Image:
        return Image.open(path)

    @staticmethod
    def pil_to_numpy(image: Image.Image) -> np.ndarray:
        return np.array(image)

    @staticmethod
    def numpy_to_pil(array: np.ndarray) -> Image.Image:
        return Image.fromarray(array)
    
    @staticmethod
    def image_to_bytes(image: Image.Image) -> bytes:
        byte_io = BytesIO()
        image.save(byte_io, format='PNG')
        byte_io.seek(0)
        return byte_io.read()
    
    @staticmethod
    def convert_to_grayscale(image: Image.Image) -> Image.Image:
        return image.convert("L")
    
    @staticmethod
    def save_image(image: Image.Image, path: str) -> None:
        image.save(path)

 
