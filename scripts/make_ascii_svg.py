"""
make_ascii_svg.py
Converts source-prepped.png into a self-typing, monochrome ASCII-art SVG.
Each row wipes in left-to-right, staggered top to bottom, then freezes.

Usage:
    python scripts/make_ascii_svg.py

Output:
    avi-ascii.svg  (rename the constant below if you like)
"""
from PIL import Image

INPUT_PATH = "source-prepped.png"
OUTPUT_PATH = "profile-ascii.svg"

COLS = 100
ROWS = 53
CHAR_W = 6.2
CHAR_H = 11
FONT_SIZE = 12
FILL_COLOR = "#8b949e"  # monochrome light-gray, matches GitHub dark-mode text

RAMP = " .`:-=+*cs#%@"  # bright (sparse) -> dark (dense); leading space = blank


def image_to_ascii_grid(path: str, cols: int, rows: int):
    img = Image.open(path).convert("L")
    img = img.resize((cols, rows))
    pixels = list(img.getdata())
    grid = []
    for r in range(rows):
        row_chars = []
        for c in range(cols):
            brightness = pixels[r * cols + c]
            idx = int((255 - brightness) / 255 * (len(RAMP) - 1))
            row_chars.append(RAMP[idx])
        grid.append("".join(row_chars))
    return grid


def build_svg(grid, cols, rows):
    width = cols * CHAR_W
    height = rows * CHAR_H

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} {height:.0f}" '
        f'width="{width:.0f}" height="{height:.0f}">',
        "<style>",
        f"text {{ font-family: 'Courier New', monospace; font-size: {FONT_SIZE}px; "
        f"fill: {FILL_COLOR}; white-space: pre; }}",
        "</style>",
        f'<rect width="100%" height="100%" fill="transparent"/>',
    ]

    for r, row in enumerate(grid):
        row_escaped = (
            row.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        )
        y = (r + 1) * CHAR_H
        delay = r * 0.045
        clip_id = f"clip-row-{r}"
        wipe_duration = 0.6

        svg_parts.append(f'<clipPath id="{clip_id}">')
        svg_parts.append(
            f'  <rect x="0" y="{y - CHAR_H:.1f}" width="0" height="{CHAR_H}">'
        )
        svg_parts.append(
            f'    <animate attributeName="width" from="0" to="{width:.0f}" '
            f'begin="{delay:.3f}s" dur="{wipe_duration}s" fill="freeze" '
            f'calcMode="spline" keySplines="0.25 0.1 0.25 1"/>'
        )
        svg_parts.append("  </rect>")
        svg_parts.append("</clipPath>")
        svg_parts.append(f'<g clip-path="url(#{clip_id})">')
        svg_parts.append(f'  <text x="0" y="{y}">{row_escaped}</text>')
        svg_parts.append("</g>")

    svg_parts.append("</svg>")
    return "\n".join(svg_parts)


if __name__ == "__main__":
    grid = image_to_ascii_grid(INPUT_PATH, COLS, ROWS)
    svg = build_svg(grid, COLS, ROWS)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Saved {OUTPUT_PATH} ({COLS}x{ROWS} chars)")
