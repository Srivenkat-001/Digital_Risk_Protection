"""
Logo and App Icon visual similarity analysis via perceptual hashing (dHash).
"""

import io

from PIL import Image

from config.logging_config import logger

MAX_IMAGE_PIXELS = 16_000_000
SUPPORTED_IMAGE_FORMATS = {"JPEG", "PNG", "WEBP"}


def _load_image(image_source: str | io.BytesIO) -> Image.Image | None:
    with Image.open(image_source) as opened:
        if opened.format not in SUPPORTED_IMAGE_FORMATS or opened.width * opened.height > MAX_IMAGE_PIXELS:
            return None
        opened.load()
        return opened.copy()


def compute_dhash(image_input: str | bytes | Image.Image) -> str | None:
    """
    Computes a 64-bit difference hash (dHash) for an image.
    image_input can be a local file path, a URL, raw bytes, or a PIL Image.
    Returns 16-character hexadecimal hash string.
    """
    try:
        img: Image.Image | None = None
        if isinstance(image_input, Image.Image):
            img = image_input
        elif isinstance(image_input, bytes):
            img = _load_image(io.BytesIO(image_input))
        elif isinstance(image_input, str):
            if image_input.lower().startswith(("http://", "https://")):
                logger.warning("Remote image hashing is disabled; provide trusted image bytes instead.")
                return None
            else:
                img = _load_image(image_input)

        if img is None:
            return None
        if img.width * img.height > MAX_IMAGE_PIXELS:
            return None

        # Convert to grayscale and resize to 9x8
        gray = img.convert("L").resize((9, 8), Image.Resampling.LANCZOS)
        pixels = gray.load()

        # Compute difference bits row by row
        difference = []
        for row in range(8):
            for col in range(8):
                pixel_left = pixels[col, row]
                pixel_right = pixels[col + 1, row]
                difference.append(pixel_left > pixel_right)

        # Convert 64 booleans to hexadecimal string
        decimal_val = 0
        for idx, bit in enumerate(difference):
            if bit:
                decimal_val |= 1 << idx

        hex_hash = f"{decimal_val:016x}"
        return hex_hash

    except Exception as e:
        logger.warning("Could not compute perceptual hash for image (%s).", type(e).__name__)
        return None

def compute_hash_distance(hash1: str, hash2: str) -> int:
    """Computes the Hamming distance (number of bit differences) between two 64-bit hex hashes."""
    val1 = int(hash1, 16)
    val2 = int(hash2, 16)
    xor_val = val1 ^ val2
    return xor_val.bit_count()


def compute_logo_similarity(
    candidate_hash: str | None,
    official_hashes: list[str]
) -> tuple[float | None, str | None]:
    """
    Compares candidate perceptual hash against a list of official brand logo hashes.
    Returns (similarity: Optional[float], best_matched_official_hash: Optional[str]).
    If candidate_hash is None or no official hashes exist, returns (None, None).
    """
    if not candidate_hash or not official_hashes:
        return None, None

    best_distance = 64
    best_official = None

    for off_hash in official_hashes:
        if not off_hash:
            continue
        try:
            dist = compute_hash_distance(candidate_hash, off_hash)
            if dist < best_distance:
                best_distance = dist
                best_official = off_hash
        except Exception as e:
            logger.debug(f"Error comparing logo hashes: {e}")
            continue


    if best_official is None:
        return None, None

    # Similarity normalized from 0.0 to 1.0 (0 distance = 1.0 similarity)
    similarity = max(0.0, 1.0 - (best_distance / 64.0))
    return round(similarity, 3), best_official
