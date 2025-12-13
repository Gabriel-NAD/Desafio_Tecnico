import cv2
import numpy as np

def load_image(file):
    file_bytes = np.frombuffer(file.read(), np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError("invalid image data")

    return image

def encode_image(image, ext=".png"):
    success, buffer = cv2.imencode(ext, image)
    if not success:
        raise ValueError("failed to encode image")
    return buffer.tobytes()

