from flask import request, jsonify, send_file
import io

from routes import image_bp
from services.image_service import load_image, encode_image
from utils.validators import validate_image_file

@image_bp.route("/process", methods=["POST"])
def process_image():
    if "image" not in request.files:
        return jsonify({"error": "image field is required"}), 400

    file = request.files["image"]

    if not validate_image_file(file.filename):
        return jsonify({"error": "unsupported file type"}), 400

    try:
        image = load_image(file)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    buffer = encode_image(image)

    return send_file(
        io.BytesIO(buffer),
        mimetype="image/png",
        as_attachment=False
    )

