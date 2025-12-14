import cv2
import numpy as np
from PIL import Image
import logging
from app.utils.crop import content_bbox, safe_crop 
from app.utils.exif import normalize_exif_orientation
from app.utils.alignment import deskew_image

logger = logging.getLogger(__name__)

def load_image(file):
    try:
        file.stream.seek(0)
        image_pil = Image.open(file.stream)

        image_pil = normalize_exif_orientation(image_pil)

        if image_pil.mode != "RGB":
            image_pil = image_pil.convert("RGB")

        image_np = np.array(image_pil)
        image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

        return image_bgr

    except Exception as e:
        logger.exception("Erro ao carregar imagem")
        raise ValueError(str(e))

def encode_image(image, ext=".png"):
    success, buffer = cv2.imencode(ext, image)
    if not success:
        raise ValueError("Falha ao codificar imagem")

    return buffer.tobytes()

def process_image(file):
    image = load_image(file)
    meta = {}

    # 1⃣ crop conservador
    bbox = content_bbox(image)
    image = safe_crop(image, bbox)
    meta["crop_applied"] = bbox is not None

    # 2⃣ deskew controlado
    rotated, angle = deskew_image(image, return_angle=True)

    if abs(angle) <= 15:
        image = rotated
        meta["deskew_angle"] = angle
        meta["deskew_applied"] = True
    else:
        meta["deskew_angle"] = 0.0
        meta["deskew_applied"] = False

    return image, meta

