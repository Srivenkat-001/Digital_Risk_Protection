"""
Unit tests for perceptual image hashing (dHash) and logo comparison.
"""

import io

from PIL import Image

from detection.logo_similarity import (
    compute_dhash,
    compute_hash_distance,
    compute_logo_similarity,
)


def test_dhash_synthetic_image():
    # Create simple solid color image
    img = Image.new("RGB", (100, 100), color="blue")
    h = compute_dhash(img)
    assert h is not None
    assert len(h) == 16  # 64-bit hex hash

def test_hash_distance_identical():
    h1 = "a1b2c3d4e5f60000"
    dist = compute_hash_distance(h1, h1)
    assert dist == 0

def test_hash_distance_different():
    h1 = "0000000000000000"
    h2 = "ffffffffffffffff"
    dist = compute_hash_distance(h1, h2)
    assert dist == 64

def test_compute_logo_similarity():
    official = ["a1b2c3d4e5f60000"]
    candidate = "a1b2c3d4e5f60000"
    sim, matched = compute_logo_similarity(candidate, official)
    assert sim == 1.0
    assert matched == "a1b2c3d4e5f60000"

def test_compute_logo_similarity_missing():
    # Missing candidate hash
    sim, matched = compute_logo_similarity(None, ["a1b2c3d4e5f60000"])
    assert sim is None
    assert matched is None

    # Missing official hashes
    sim, matched = compute_logo_similarity("a1b2c3d4e5f60000", [])
    assert sim is None
    assert matched is None


def test_remote_image_hashing_is_disabled():
    assert compute_dhash("https://127.0.0.1/private.png") is None


def test_image_hashing_accepts_valid_png_bytes():
    image = Image.new("RGB", (32, 32), color="blue")
    encoded = io.BytesIO()
    image.save(encoded, format="PNG")

    image_hash = compute_dhash(encoded.getvalue())

    assert image_hash is not None
    assert len(image_hash) == 16
