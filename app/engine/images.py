import base64
import io
import re
from PIL import Image

from app.core.config import settings
from app.core.exceptions import ImageProcessingError


def decode_and_validate_base64_image(image_base64: str) -> tuple[io.BytesIO, float, float]:
    """Decode base64 image data in memory, validate format and size, and return (BytesIO, width, height).

    Strictly zero disk persistence.
    """
    if not image_base64 or not isinstance(image_base64, str):
        raise ImageProcessingError("Image payload must be a non-empty base64 string.")

    # Strip data URI header if present (e.g. data:image/png;base64,...)
    clean_base64 = re.sub(r"^data:image\/[a-zA-Z0-9+\.-]+;base64,", "", image_base64.strip())

    try:
        raw_bytes = base64.b64decode(clean_base64, validate=True)
    except Exception as exc:
        raise ImageProcessingError(f"Failed to decode base64 image payload: {exc}") from exc

    if len(raw_bytes) > settings.MAX_IMAGE_SIZE_BYTES:
        max_mb = settings.MAX_IMAGE_SIZE_BYTES / (1024 * 1024)
        raise ImageProcessingError(
            f"Image payload size exceeds the maximum limit of {max_mb:.1f}MB."
        )

    # In-memory PIL validation
    buffer = io.BytesIO(raw_bytes)
    try:
        with Image.open(buffer) as img:
            img.verify()
            width, height = img.size
    except Exception as exc:
        raise ImageProcessingError(f"Invalid or corrupted image format: {exc}") from exc

    if width <= 0 or height <= 0:
        raise ImageProcessingError("Image dimensions must be positive.")

    # Rewind buffer for downstream consumption
    buffer.seek(0)
    return buffer, float(width), float(height)


def calculate_contain_bounds(
    orig_w: float,
    orig_h: float,
    box_left: float,
    box_top: float,
    box_w: float,
    box_h: float,
) -> tuple[float, float, float, float]:
    """Calculate (left, top, width, height) to contain and center an image inside a bounding box

    preserving natural aspect ratio without distortion.
    """
    aspect_img = orig_w / orig_h
    aspect_box = box_w / box_h

    if aspect_img > aspect_box:
        # Constrain by box width
        fit_w = box_w
        fit_h = box_w / aspect_img
    else:
        # Constrain by box height
        fit_h = box_h
        fit_w = box_h * aspect_img

    # Center within container frame
    fit_left = box_left + (box_w - fit_w) / 2.0
    fit_top = box_top + (box_h - fit_h) / 2.0
    return fit_left, fit_top, fit_w, fit_h
