import json
import os
import sys
from datetime import datetime, timezone

try:
    import requests
except ImportError:
    os.system("pip install requests -q")
    import requests

CATEGORIES = [
    {
        "id": 58921,
        "label": "Best Video Podcast Host",
        "url": "https://vote.webbyawards.com/PublicVoting#/2026/podcasts/features/best-video-podcast-host",
    },
    {
        "id": 57433,
        "label": "Best Individual Episode — Comedy",
        "url": "https://vote.webbyawards.com/PublicVoting#/2026/podcasts/individual-episode/comedy",
    },
]

API_URL = "https://api.webbyawards.com/api/PV/GetPVBallot"
HEADERS = {
    "Content-Type": "application/json",
    "Origin": "https://vote.webbyawards.com",
    "Referer": "https://vote.webbyawards.com/",
}


def scrape(cat):
    resp = requests.post(
        API_URL,
        json={"PropertyCategoryID": cat["id"], "PropertyID": 1, "PVUserID": None},
        headers=HEADERS,
        timeout=20,
    )
    resp.raise_for_status()
    payload = resp.json()

    info = payload.get("Data", {})
    raw_entries = info.get("Entries") or []
    total = sum(e.get("TotalVoteCount", 0) for e in raw_entries)

    entries = sorted(
        [
            {
                "title": e.get("Title", ""),
                "votes": e.get("TotalVoteCount", 0),
                "pct": f"{e.get('TotalVoteCount', 0) / total * 100:.1f}" if total else "0.0",
            }
            for e in raw_entries
        ],
        key=lambda e: e["votes"],
        reverse=True,
    )

    return {
        "name": info.get("Category") or cat["label"],
        "url": cat["url"],
        "total": total,
        "entries": entries,
    }


categories = []
for cat in CATEGORIES:
    print(f"Scraping: {cat['label']}")
    try:
        data = scrape(cat)
        categories.append(data)
        print(f"  {len(data['entries'])} entries, {data['total']:,} total votes")
    except Exception as e:
        print(f"  Error: {e}", file=sys.stderr)

if not categories:
    print("No data scraped — exiting", file=sys.stderr)
    sys.exit(1)

out_dir = os.path.join(os.path.dirname(__file__), "tyso-webby")
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "data.json")
with open(out_path, "w") as f:
    json.dump({"updated": datetime.now(timezone.utc).isoformat(), "categories": categories}, f, indent=2)

print(f"Written to {out_path}")
