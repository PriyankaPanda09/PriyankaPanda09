"""
prep_photo.py
Prepares a photo for ASCII conversion:
1. Removes the background (so subject is isolated)
2. Boosts local contrast (CLAHE) so a flat-lit face has real highlights/shadows
3. Composites onto pure white (maps background -> blank space in the ASCII ramp)

Usage:
    python scripts/prep_photo.py source-photo.jpg

Output:
    source-prepped.png (grayscale, ready for make_ascii_svg.py)
"""
import sys
import io
import numpy as np
import cv2
from PIL import Image
from rembg import remove


def prep_photo(input_path: str, output_path: str = "source-prepped.png"):
    with open(input_path, "rb") as f:
        input_bytes = f.read()

    # 1. Remove background -> RGBA with transparent background
    output_bytes = remove(input_bytes)
    subject = Image.open(io.BytesIO(output_bytes)).convert("RGBA")

    # 2. Composite onto pure white
    white_bg = Image.new("RGBA", subject.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white_bg, subject).convert("L")

    # 3. Boost local contrast with CLAHE
    arr = np.array(composited)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    arr_clahe = clahe.apply(arr)

    Image.fromarray(arr_clahe).save(output_path)
    print(f"Saved prepped photo to {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/prep_photo.py <source-photo.jpg>")
        sys.exit(1)
    prep_photo(sys.argv[1])
