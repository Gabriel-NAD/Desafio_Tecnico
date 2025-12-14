ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}

def validate_image_file(filename: str) -> bool:
    if not filename:
        return False
    filename = filename.lower()
    return any(filename.endswith(ext) for ext in ALLOWED_EXTENSIONS)

