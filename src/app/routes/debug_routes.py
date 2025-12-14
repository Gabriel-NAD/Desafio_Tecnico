from flask import Blueprint, jsonify

debug_bp = Blueprint("debug", __name__)

@debug_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

