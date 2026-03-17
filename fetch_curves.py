"""
Chatham Financial - EURIBOR & SONIA Forward Curve Scraper
Fetches daily forward curve snapshots and appends to CSV files in data/
"""

import requests
import csv
import json
import os
from datetime import datetime, timezone

# Endpoint IDs discovered via browser Network tab
CURVES = {
    "1M_EURIBOR": 158031,
    "3M_EURIBOR": 143818,
    "6M_EURIBOR": 216482,
    "3M_SONIA":   195503,
}

BASE_URL = "https://www.chathamfinancial.com/getrates/{}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; curve-archiver/1.0)",
    "Accept": "application/json",
    "Referer": "https://www.chathamfinancial.com/technology/european-forward-curves",
}

DATA_DIR = "data"


def fetch_curve(curve_id: int) -> dict:
    url = BASE_URL.format(curve_id)
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()


def save_snapshot(curve_name: str, data: dict, snapshot_date: str):
    """
    Appends one row per forward date to data/<CURVE_NAME>.csv
    Columns: snapshot_date, curve_date, forward_date, rate
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    filepath = os.path.join(DATA_DIR, f"{curve_name}.csv")

    file_exists = os.path.isfile(filepath)
    curve_date = data.get("CurveDate", "")

    with open(filepath, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["snapshot_date", "curve_date", "forward_date", "rate"])
        for point in data.get("Rates", []):
            writer.writerow([
                snapshot_date,
                curve_date,
                point["Date"],
                point["Rate"],
            ])

    print(f"  {curve_name}: {len(data.get('Rates', []))} points saved")


def save_latest_json(curve_name: str, data: dict):
    """Saves the raw JSON as latest_<CURVE>.json for easy inspection."""
    os.makedirs(DATA_DIR, exist_ok=True)
    filepath = os.path.join(DATA_DIR, f"latest_{curve_name}.json")
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)


def main():
    snapshot_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print(f"Fetching curves for snapshot date: {snapshot_date}")

    results = {}
    for name, curve_id in CURVES.items():
        print(f"  Fetching {name} (id={curve_id})...")
        try:
            data = fetch_curve(curve_id)
            save_snapshot(name, data, snapshot_date)
            save_latest_json(name, data)
            results[name] = "ok"
        except Exception as e:
            print(f"  ERROR fetching {name}: {e}")
            results[name] = f"error: {e}"

    # Write a run log
    os.makedirs(DATA_DIR, exist_ok=True)
    log_path = os.path.join(DATA_DIR, "run_log.csv")
    log_exists = os.path.isfile(log_path)
    with open(log_path, "a", newline="") as f:
        writer = csv.writer(f)
        if not log_exists:
            writer.writerow(["run_timestamp", "curve", "status"])
        ts = datetime.now(timezone.utc).isoformat()
        for name, status in results.items():
            writer.writerow([ts, name, status])

    print("Done.")


if __name__ == "__main__":
    main()
