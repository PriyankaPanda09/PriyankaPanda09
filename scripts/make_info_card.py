"""
make_info_card.py
Generates a neofetch-style SVG info card that fades in line by line.

Usage:
    python scripts/make_info_card.py
    STATIC=1 python scripts/make_info_card.py   # frozen frame, no animation

Output:
    info-card.svg

Edit the CONTENT dict below to update your details.
"""
import os

OUTPUT_PATH = "info-card.svg"
STATIC = os.environ.get("STATIC") == "1"

WIDTH = 560
LINE_HEIGHT = 26
PADDING_TOP = 56
FONT_SIZE = 14
TITLE_BAR_H = 34

BG = "#0d1117"
TITLE_BAR = "#161b22"
BORDER = "#30363d"
KEY_COLOR = "#58a6ff"
VAL_COLOR = "#c9d1d9"
DIM = "#8b949e"
DOT_RED = "#ff5f56"
DOT_YEL = "#ffbd2e"
DOT_GRN = "#27c93f"

CONTENT = [
    ("whoami", "priyanka-panda"),
    ("role", "Full-Stack & AI Engineer"),
    ("education", "B.Tech CSE @ GIET University"),
    ("stack", "Java · Python · React · Node.js · FastAPI"),
    ("ai/ml", "Gemini API · TensorFlow · Agentic AI"),
    ("certs", "ServiceNow CAD/CSA · NPTEL Java & Python"),
    ("current", "Civic-tech & carbon-tracking apps"),
    ("looking_for", "SDE / Full-Stack / AI roles"),
]

TITLE = "priyanka@github: ~"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg():
    height = PADDING_TOP + LINE_HEIGHT * len(CONTENT) + 24

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" '
        f'width="{WIDTH}" height="{height}">',
        "<style>",
        f".card {{ font-family: 'Courier New', monospace; font-size: {FONT_SIZE}px; }}",
        f".key {{ fill: {KEY_COLOR}; font-weight: bold; }}",
        f".val {{ fill: {VAL_COLOR}; }}",
        f".title {{ fill: {DIM}; font-size: 13px; }}",
        "</style>",
        f'<rect width="{WIDTH}" height="{height}" rx="10" fill="{BG}" '
        f'stroke="{BORDER}" stroke-width="1.5"/>',
        f'<rect width="{WIDTH}" height="{TITLE_BAR_H}" rx="10" fill="{TITLE_BAR}"/>',
        f'<rect y="{TITLE_BAR_H - 10}" width="{WIDTH}" height="10" fill="{TITLE_BAR}"/>',
        f'<circle cx="22" cy="{TITLE_BAR_H/2}" r="6" fill="{DOT_RED}"/>',
        f'<circle cx="42" cy="{TITLE_BAR_H/2}" r="6" fill="{DOT_YEL}"/>',
        f'<circle cx="62" cy="{TITLE_BAR_H/2}" r="6" fill="{DOT_GRN}"/>',
        f'<text x="{WIDTH/2}" y="{TITLE_BAR_H/2 + 5}" text-anchor="middle" '
        f'class="card title">{esc(TITLE)}</text>',
    ]

    for i, (key, val) in enumerate(CONTENT):
        y = PADDING_TOP + i * LINE_HEIGHT
        line_group_open = "<g>"
        if not STATIC:
            delay = 0.15 + i * 0.12
            line_group_open = (
                f'<g opacity="0" transform="translate(-8,0)">'
                f'<animate attributeName="opacity" from="0" to="1" '
                f'begin="{delay:.2f}s" dur="0.35s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="translate" '
                f'from="-8,0" to="0,0" begin="{delay:.2f}s" dur="0.35s" fill="freeze"/>'
            )
        parts.append(line_group_open)
        parts.append(
            f'<text x="20" y="{y}" class="card key">{esc(key)}</text>'
        )
        parts.append(
            f'<text x="150" y="{y}" class="card val">{esc(val)}</text>'
        )
        parts.append("</g>")

    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    svg = build_svg()
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Saved {OUTPUT_PATH}")
