from pathlib import Path
import cv2
import numpy as np
from app.utils.alignment import deskew_pca, deskew_image

BASE_DIR = Path(__file__).resolve().parent
IMG_PATH = BASE_DIR / "16.jpg"

img = cv2.imread(str(IMG_PATH))
assert img is not None, f"Imagem não carregou: {IMG_PATH}"

# === PCA (principal) ===
out_pca = deskew_pca(img)
cv2.imwrite(str(BASE_DIR / "out_pca.png"), out_pca)

# === Hough / contorno (secundário) ===
out_hough, angle = deskew_image(img, return_angle=True)
cv2.imwrite(str(BASE_DIR / "out_hough.png"), out_hough)

# === Métrica objetiva ===
diff = np.mean(np.abs(img.astype(float) - out_pca.astype(float)))
print("Diferença média PCA:", diff)

print("Teste concluído com sucesso")

