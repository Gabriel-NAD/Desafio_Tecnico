from flask import Blueprint, request, Response
from io import BytesIO
import logging

from app.services.image_service import process_image, encode_image

image_bp = Blueprint("image", __name__)
logger = logging.getLogger(__name__)

@image_bp.route("/process", methods=["POST"])
def process_image_route():
    try:
        file = request.files.get("image")
        if not file:
            return {"error": "image not provided"}, 400

        image, meta = process_image(file)

        if image is None or image.size == 0:
            raise ValueError("Imagem final vazia")

        img_bytes = encode_image(image)

        if not isinstance(img_bytes, (bytes, bytearray)):
            raise TypeError("encode_image não retornou bytes")

        return Response(
            img_bytes,
            mimetype="image/png"
        )

    except Exception as e:
        logger.exception("Erro no processamento da imagem")
        return {
            "error": "image processing failed",
            "detail": str(e)
        }, 500

