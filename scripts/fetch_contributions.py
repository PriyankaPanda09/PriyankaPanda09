"""
fetch_contributions.py
Fetches your public GitHub contribution calendar (no token needed) by
scraping the same HTML fragment GitHub's own profile page uses, then
computes derived stats (streaks, best day, monthly totals).

Usage:
    python scripts/fetch_contributions.py

Output:
    data/contributions.json

Set your username below or via the GITHUB_USERNAME env var.
"""
import os
import json
import datetime
import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GITHUB_USERNAME", "PriyankaPanda09")
URL = f"https://github.com/users/{USERNAME}/contributions"
OUTPUT_PATH = "data/contributions.json"


def fetch_days():
    resp = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    days = []
    # GitHub renders contribution cells as <td> with data-date / data-level,
    # or as <rect> tags with data-date/data-level depending on markup version.
    cells = soup.select("td.ContributionCalendar-day, rect.ContributionCalendar-day")
    for cell in cells:
        date_str = cell.get("data-date")
        level = cell.get("data-level")
        count_attr = cell.get("data-count")
        if date_str is None:
            continue
        try:
            level = int(level) if level is not None else 0
        except ValueError:
            level = 0
        try:
            count = int(count_attr) if count_attr is not None else level
        except ValueError:
            count = level
        days.append({"date": date_str, "level": level, "count": count})

    days.sort(key=lambda d: d["date"])
    return days


def compute_stats(days):
    total = sum(d["count"] for d in days)

    # current streak (walking back from most recent day with data)
    current_streak = 0
    for d in reversed(days):
        if d["count"] > 0:
            current_streak += 1
        else:
            break

    # longest streak
    longest_streak = 0
    running = 0
    for d in days:
        if d["count"] > 0:
            running += 1
            longest_streak = max(longest_streak, running)
        else:
            running = 0

    best_day = max(days, key=lambda d: d["count"], default=None)

    monthly = {}
    for d in days:
        month_key = d["date"][:7]  # YYYY-MM
        monthly[month_key] = monthly.get(month_key, 0) + d["count"]

    return {
        "total_last_year": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly_totals": monthly,
    }


if __name__ == "__main__":
    days = fetch_days()
    stats = compute_stats(days)
    data = {
        "username": USERNAME,
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "days": days,
        "stats": stats,
    }
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Saved {len(days)} days, {stats['total_last_year']} total contributions -> {OUTPUT_PATH}")
