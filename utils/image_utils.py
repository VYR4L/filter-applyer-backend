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
    def sobel_filters(image_array: np.ndarray) -> list[tuple[np.ndarray, np.ndarray]]:
        """Returns Sobel filters for x and y directions."""
        kernel_x = np.array([[-1, 0, 1],
                             [-2, 0, 2],
                             [-1, 0, 1]], dtype=np.float32)

        kernel_y = np.array([[1, 2, 1],
                             [0, 0, 0],
                             [-1, -2, -1]], dtype=np.float32)
        
        intensity_x = ImageUtils.convolve2d(image_array, kernel_x)
        intensity_y = ImageUtils.convolve2d(image_array, kernel_y)

        gradient_magnitude = np.hypot(intensity_x, intensity_y)  # Equivalent to sqrt(Ix^2 + Iy^2)

        gradient_direction = np.arctan2(intensity_y, intensity_x)  # Angle in radians

        return gradient_magnitude, gradient_direction
    
    @staticmethod
    def non_maximum_suppression(gradient_magnitude: np.ndarray, gradient_direction: np.ndarray) -> np.ndarray:
        """Applies non-maximum suppression to thin edges."""
        image_height, image_width = gradient_magnitude.shape
        suppressed_image = np.zeros((image_height, image_width), dtype=np.float32)

        angle = gradient_direction * (180.0 / np.pi)
        angle[angle < 0] += 180

        for i in range(1, image_height - 1):
            for j in range(1, image_width - 1):
                q = 255
                r = 255

                # Angle 0 - East-West gradient -> Vertical edge
                if (0 <= angle[i, j] < 22.5) or (157.5 <= angle[i, j] <= 180):
                    q = gradient_magnitude[i, j + 1]
                    r = gradient_magnitude[i, j - 1]
                # Angle 45 - Northeast-Southwest gradient -> Diagonal edge
                elif (22.5 <= angle[i, j] < 67.5):
                    q = gradient_magnitude[i + 1, j - 1]
                    r = gradient_magnitude[i - 1, j + 1]
                # Angle 90 - North-South gradient -> Horizontal edge
                elif (67.5 <= angle[i, j] < 112.5):
                    q = gradient_magnitude[i + 1, j]
                    r = gradient_magnitude[i - 1, j]
                # Angle 135 - Northwest-Southeast gradient -> Diagonal edge
                elif (112.5 <= angle[i, j] < 157.5):
                    q = gradient_magnitude[i - 1, j - 1]
                    r = gradient_magnitude[i + 1, j + 1]

                # Local maximum check
                if (gradient_magnitude[i, j] >= q) and (gradient_magnitude[i, j] >= r):
                    suppressed_image[i, j] = gradient_magnitude[i, j]
                else:
                    suppressed_image[i, j] = 0

        return suppressed_image
    
    @staticmethod
    def convert_to_grayscale(image: Image.Image) -> Image.Image:
        return image.convert("L")
    
    @staticmethod
    def save_image(image: Image.Image, path: str) -> None:
        image.save(path)

    @staticmethod
    def label_connected_components(binary_image: np.ndarray) -> np.ndarray:
        """
        Label connected components in a binary image using flood-fill.
        
        Args:
            binary_image: Binary image (0 or 1, uint8)
        
        Returns:
            Labeled image where each connected component has a unique label
        """
        rows, cols = binary_image.shape
        labels = np.zeros((rows, cols), dtype=np.int32)
        current_label = 1
        
        def flood_fill(start_i, start_j, label):
            """Flood fill using iterative approach with stack."""
            stack = [(start_i, start_j)]
            
            while stack:
                i, j = stack.pop()
                
                # Check bounds and if pixel should be labeled
                if (0 <= i < rows and 0 <= j < cols and 
                    binary_image[i, j] == 1 and labels[i, j] == 0):
                    
                    labels[i, j] = label
                    
                    # Add 4-connected neighbors to stack
                    stack.append((i - 1, j))  # Top
                    stack.append((i + 1, j))  # Bottom
                    stack.append((i, j - 1))  # Left
                    stack.append((i, j + 1))  # Right
        
        # Scan image and label each connected component
        for i in range(rows):
            for j in range(cols):
                if binary_image[i, j] == 1 and labels[i, j] == 0:
                    # Found new connected component
                    flood_fill(i, j, current_label)
                    current_label += 1
        
        return labels
 
