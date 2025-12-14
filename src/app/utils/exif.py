from PIL import Image, ExifTags

def normalize_exif_orientation(image_pil: Image.Image) -> Image.Image:
    try:
        exif = image_pil._getexif()
        if not exif:
            return image_pil

        orientation_key = None
        for key, value in ExifTags.TAGS.items():
            if value == "Orientation":
                orientation_key = key
                break

        if orientation_key is None or orientation_key not in exif:
            return image_pil

        orientation = exif[orientation_key]

        if orientation == 3:
            image_pil = image_pil.rotate(180, expand=True)
        elif orientation == 6:
            image_pil = image_pil.rotate(270, expand=True)
        elif orientation == 8:
            image_pil = image_pil.rotate(90, expand=True)

    except Exception:
        pass

    return image_pil
