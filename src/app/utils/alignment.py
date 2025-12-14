import cv2
import numpy as np
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

def _estimate_angle_from_contour(cnt) -> float:
    rect = cv2.minAreaRect(cnt)
    angle = rect[-1]
    if angle < -45:
        angle = 90 + angle
    return angle

def _estimate_angle_from_lines(gray) -> float:
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, rho=1, theta=np.pi/180.0, threshold=100,
                            minLineLength=min(gray.shape)//10, maxLineGap=20)
    if lines is None:
        return 0.0

    angles = []
    for l in lines:
        x1,y1,x2,y2 = l[0]
        dx = x2 - x1
        dy = y2 - y1
        if dx == 0:
            ang = 90.0
        else:
            ang = np.degrees(np.arctan2(dy, dx))
        # Normalize to [-90, 90]
        if ang > 90:
            ang -= 180
        if ang < -90:
            ang += 180
        angles.append(ang)

    if not angles:
        return 0.0

    median_ang = float(np.median(angles))
    return median_ang

def deskew_image(image: np.ndarray, return_angle: bool = False) -> Tuple[np.ndarray, float]:
    logger.debug("[DESKEW] iniciando")
    if image is None or image.size == 0:
        logger.debug("[DESKEW] imagem vazia")
        return image if not return_angle else (image, 0.0)

    # Gray
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    h, w = gray.shape[:2]

    # Blur adaptativo proporcional ao tamanho
    k = max(3, (min(h, w) // 300) | 1)  # odd kernel
    blurred = cv2.GaussianBlur(gray, (k, k), 0)

    # Detectar se o fundo é claro (paper) ou escuro:
    mean_val = float(np.mean(blurred))
    background_is_light = mean_val > 127

    # Binarização: se fundo claro -> thresh inv, senão sem invert
    if background_is_light:
        _, thresh = cv2.threshold(blurred, 0, 255,
                                 cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    else:
        _, thresh = cv2.threshold(blurred, 0, 255,
                                 cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Ajuste: se Otsu entregar resultado ruim (muito branco/pouco branco), usar adaptativo
    white_pixels = np.sum(thresh == 255)
    white_ratio = white_pixels / thresh.size
    if white_ratio < 0.01 or white_ratio > 0.99:
        # blockSize proporcional
        block = max(11, (min(h, w) // 50) | 1)
        thresh = cv2.adaptiveThreshold(blurred, 255,
                                       cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY_INV if background_is_light else cv2.THRESH_BINARY,
                                       block, max(3, block//6))

    kernel_size = max(3, min(h, w) // 200)
    if kernel_size % 2 == 0:
        kernel_size += 1
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)

    # Encontrar contornos
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    logger.debug(f"[DESKEW] found {len(contours)} contours")

    angle = 0.0
    use_angle = None

    if contours:
        # Selecionar maior contorno coerente
        largest_contour = max(contours, key=cv2.contourArea)
        contour_area = cv2.contourArea(largest_contour)
        image_area = float(h * w)
        ratio = contour_area / image_area
        logger.debug(f"[DESKEW] contour area ratio: {ratio:.4f}")

        # Somente usar se razoavelmente grande
        if ratio > 0.05:
            try:
                angle = _estimate_angle_from_contour(largest_contour)
                use_angle = 'contour'
            except Exception as e:
                logger.exception("Falha ao estimar ângulo por contorno")

    # Fallback por Hough Lines se não houver contorno bom
    if use_angle is None:
        try:
            line_angle = _estimate_angle_from_lines(blurred)
            angle = line_angle
            use_angle = 'lines'
            logger.debug(f"[DESKEW] angle from lines: {angle:.2f}")
        except Exception:
            angle = 0.0

    if abs(angle) < 0.5:
        logger.debug(f"[DESKEW] ângulo muito pequeno ({angle:.2f}), não aplicando")
        if return_angle:
            return image, 0.0
        return image

    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)

    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])
    new_w = int((h * sin) + (w * cos))
    new_h = int((h * cos) + (w * sin))

    M[0, 2] += (new_w / 2) - center[0]
    M[1, 2] += (new_h / 2) - center[1]

    border_val = (255, 255, 255)
    rotated = cv2.warpAffine(image, M, (new_w, new_h),
                             flags=cv2.INTER_CUBIC,
                             borderMode=cv2.BORDER_CONSTANT,
                             borderValue=border_val)

    logger.info(f"[DESKEW] rotacionado {angle:.2f} graus (metodo={use_angle}) -> novo shape {rotated.shape}")

    if return_angle:
        return rotated, angle
    return rotated
def deskew_pca(image: np.ndarray) -> np.ndarray:
    if image is None or image.size == 0:
        return image

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Binarização (texto em branco)
    _, bw = cv2.threshold(
        gray, 0, 255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    # Coordenadas dos pixels "ativos"
    coords = np.column_stack(np.where(bw > 0))

    if len(coords) < 1000:
        # Pouca informação → não confia
        return image

    # PCA
    mean, eigenvectors = cv2.PCACompute(coords.astype(np.float32), mean=None)
    angle = np.arctan2(eigenvectors[0, 1], eigenvectors[0, 0])
    angle = np.degrees(angle)

    # Ajuste de convenção
    angle = angle - 90

    print(f"[DESKEW PCA] Ângulo estimado: {angle:.2f}")

    if abs(angle) < 0.5:
        return image

    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)

    return cv2.warpAffine(
        image, M, (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE
    )

