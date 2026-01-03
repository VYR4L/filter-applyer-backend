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
    def convolve2d(image: np.ndarray, kernel: np.ndarray) -> np.ndarray:
        image_height, image_width = image.shape
        kernel_height, kernel_width = kernel.shape
        pad_height = kernel_height // 2
        pad_width = kernel_width // 2

        # Pad the image to handle borders
        padded_image = np.pad(image, ((pad_height, pad_height), (pad_width, pad_width)), mode='edge')
        convolved_image = np.zeros_like(image)

        # Perform convolution
        for i in range(image_height):
            for j in range(image_width):
                region = padded_image[i:i + kernel_height, j:j + kernel_width]
                convolved_value = np.sum(region * kernel)
                convolved_image[i, j] = convolved_value

        return convolved_image
    
    @staticmethod
    def generate_gaussian_kernel(size: int, sigma: float) -> np.ndarray:
        """Generates a 2D Gaussian kernel."""
        size = int(2 * np.ceil(3 * sigma) + 1)

        x, y = np.meshgrid(
            np.linspace(-size // 2, size // 2, size),
            np.linspace(-size // 2, size // 2, size)
        )

        # Gaussian function
        normalizer = -1 / (np.pi * sigma**4)
        first_term = 1 - (x**2 + y**2) / (2 * sigma**2)  # Laplacian component
        second_term = np.exp(-(x**2 + y**2) / (2 * sigma**2))  # Gaussian component
        gaussian = normalizer * first_term * second_term

        return gaussian
    
    @staticmethod
    def convert_to_grayscale(image: Image.Image) -> Image.Image:
        return image.convert("L")
    
    @staticmethod
    def save_image(image: Image.Image, path: str) -> None:
        image.save(path)

 
