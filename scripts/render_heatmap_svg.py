"""
render_heatmap_svg.py
Renders data/contributions.json as a 53-week x 7-day heatmap, colored boxes
sliding in diagonally on load, plus a legend and stats footer.

Usage:
    python scripts/render_heatmap_svg.py

Output:
    contrib-heatmap.svg
"""
import json
import os
import datetime

INPUT_PATH = "data/contributions.json"
OUTPUT_PATH = "contrib-heatmap.svg"
STATIC = os.environ.get("STATIC") == "1"

CELL = 12
GAP = 3
LEFT_PAD = 30
TOP_PAD = 20
BOTTOM_PAD = 46

PALETTE = ["#123524", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
TEXT_COLOR = "#8b949e"
BG = "transparent"

MONTH_LABELS = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]


def level_to_color(level: int) -> str:
    level = max(0, min(level, len(PALETTE) - 1))
    return PALETTE[level]


def build_svg(data):
    days = data["days"]
    stats = data["stats"]
    username = data["username"]

    if not days:
        weeks = []
    else:
        first_date = datetime.date.fromisoformat(days[0]["date"])
        # align to the preceding Sunday so columns are full weeks
        offset = (first_date.weekday() + 1) % 7
        padded = [None] * offset + days
        weeks = [padded[i:i + 7] for i in range(0, len(padded), 7)]

    n_weeks = len(weeks)
    width = LEFT_PAD + n_weeks * (CELL + GAP)
    height = TOP_PAD + 7 * (CELL + GAP) + BOTTOM_PAD

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}">',
        "<style>",
        ".hm-text { font-family: 'Segoe UI', Helvetica, Arial, sans-serif; "
        f"font-size: 11px; fill: {TEXT_COLOR}; }}",
        "@keyframes slidein { from { opacity: 0; transform: translate(-6px,-6px); } "
        "to { opacity: 1; transform: translate(0,0); } }",
        (
            ".cell { opacity: 1; }"
            if STATIC
            else ".cell { animation: slidein 0.35s ease-out forwards; opacity: 0; }"
        ),
        "</style>",
        f'<rect width="{width}" height="{height}" fill="{BG}"/>',
    ]

    # month labels (approximate: label the week column where a new month starts)
    last_month = None
    for w_idx, week in enumerate(weeks):
        for day in week:
            if day is None:
                continue
            d = datetime.date.fromisoformat(day["date"])
            if d.day <= 7 and d.month != last_month:
                x = LEFT_PAD + w_idx * (CELL + GAP)
                parts.append(
                    f'<text x="{x}" y="{TOP_PAD - 6}" class="hm-text">'
                    f'{MONTH_LABELS[d.month - 1]}</text>'
                )
                last_month = d.month
            break

    # weekday labels (Mon, Wed, Fri)
    weekday_labels = {1: "Mon", 3: "Wed", 5: "Fri"}
    for row, label in weekday_labels.items():
        y = TOP_PAD + row * (CELL + GAP) + CELL - 1
        parts.append(f'<text x="0" y="{y}" class="hm-text">{label}</text>')

    # grid cells
    delay_step = 0.004
    for w_idx, week in enumerate(weeks):
        for d_idx, day in enumerate(week):
            x = LEFT_PAD + w_idx * (CELL + GAP)
            y = TOP_PAD + d_idx * (CELL + GAP)
            if day is None:
                continue
            color = level_to_color(day["level"])
            delay = (w_idx * 7 + d_idx) * delay_step
            title = f'{day["count"]} contributions on {day["date"]}'
            parts.append(
                f'<rect class="cell" x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
                f'rx="2.5" fill="{color}" style="animation-delay:{delay:.3f}s">'
                f'<title>{title}</title></rect>'
            )

    # legend
    legend_y = height - BOTTOM_PAD + 24
    parts.append(f'<text x="{LEFT_PAD}" y="{legend_y}" class="hm-text">Less</text>')
    lx = LEFT_PAD + 34
    for color in PALETTE:
        parts.append(
            f'<rect x="{lx}" y="{legend_y - 10}" width="{CELL}" height="{CELL}" '
            f'rx="2.5" fill="{color}"/>'
        )
        lx += CELL + GAP
    parts.append(f'<text x="{lx + 4}" y="{legend_y}" class="hm-text">More</text>')

    # stats footer
    footer = (
        f'{stats["total_last_year"]} contributions in the last year · '
        f'current streak {stats["current_streak"]} · longest streak {stats["longest_streak"]}'
    )
    parts.append(
        f'<text x="{width - LEFT_PAD}" y="{legend_y}" text-anchor="end" '
        f'class="hm-text">{footer}</text>'
    )

    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    svg = build_svg(data)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Saved {OUTPUT_PATH}")



