import cv2
import numpy as np

def content_bbox(image, min_density=0.02, pad_ratio=0.20):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    _, bw = cv2.threshold(
        gray, 0, 255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    h, w = bw.shape

    # projeções
    proj_y = np.sum(bw > 0, axis=1) / w
    proj_x = np.sum(bw > 0, axis=0) / h

    ys = np.where(proj_y > min_density)[0]
    xs = np.where(proj_x > min_density)[0]

    if len(xs) == 0 or len(ys) == 0:
        return None

    y1, y2 = ys[0], ys[-1]
    x1, x2 = xs[0], xs[-1]

    # padding proporcional
    pad_y = int((y2 - y1) * pad_ratio)
    pad_x = int((x2 - x1) * pad_ratio)

    y1 = max(0, y1 - pad_y)
    y2 = min(h, y2 + pad_y)
    x1 = max(0, x1 - pad_x)
    x2 = min(w, x2 + pad_x)

    return x1, y1, x2, y2
def safe_crop(image, bbox):
    if bbox is None:
        return image

    x1, y1, x2, y2 = bbox

    if x2 <= x1 or y2 <= y1:
        return image

    return image[y1:y2, x1:x2]
import cv2
import numpy as np

def center_on_canvas(
    image,
    canvas_ratio=1.15,
    background=(255, 255, 255)
):
    """
    Centraliza a imagem em um canvas maior.
    canvas_ratio > 1 adiciona borda branca.
    """
    h, w = image.shape[:2]

    new_h = int(h * canvas_ratio)
    new_w = int(w * canvas_ratio)

    canvas = np.full(
        (new_h, new_w, 3),
        background,
        dtype=image.dtype
    )

    y_offset = (new_h - h) // 2
    x_offset = (new_w - w) // 2

    canvas[y_offset:y_offset+h, x_offset:x_offset+w] = image

    return canvas

