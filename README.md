# Chatham Financial – EURIBOR & SONIA Forward Curve Archiver

Daily snapshots of the 1M/3M/6M EURIBOR and 3M SONIA forward curves
published by [Chatham Financial](https://www.chathamfinancial.com/technology/european-forward-curves).

## What it does

A GitHub Actions workflow runs every weekday at 18:00 UTC (after the
curves are updated at ~16:00 London time). It fetches the four JSON
endpoints below and appends a row per forward date to CSV files in
`data/`.

| File | Curve |
|---|---|
| `data/1M_EURIBOR.csv` | 1-month EURIBOR forward curve |
| `data/3M_EURIBOR.csv` | 3-month EURIBOR forward curve |
| `data/6M_EURIBOR.csv` | 6-month EURIBOR forward curve |
| `data/3M_SONIA.csv`   | 3-month compounded SONIA forward curve |
| `data/latest_*.json`  | Raw JSON from last successful run |
| `data/run_log.csv`    | Execution log with status per run |

## CSV format

```
snapshot_date, curve_date,          forward_date,         rate
2026-03-17,    2026-03-09T16:00:00, 2026-03-11T00:00:00,  0.01941
2026-03-17,    2026-03-09T16:00:00, 2026-04-13T00:00:00,  0.0199303
...
```

- **snapshot_date**: date the script ran
- **curve_date**: date Chatham published the curve (usually T-1 close)
- **forward_date**: the future fixing date
- **rate**: the implied forward rate (decimal, e.g. 0.02078 = 2.078%)

## Setup (one-time)

1. Fork or clone this repo to your own GitHub account.
2. No secrets or tokens needed — the Chatham endpoints are public.
3. Go to **Actions** tab → enable workflows if prompted.
4. Done. The workflow runs automatically on weekdays.

## Manual run

Go to **Actions → Fetch Chatham Forward Curves → Run workflow**.

## Run locally

```bash
pip install requests
python fetch_curves.py
```

Data will be written to `./data/`.

## Notes

- Chatham updates curves once per day after London market close.
- The script is idempotent: re-running on the same day appends
  duplicate rows. The `snapshot_date` column lets you deduplicate.
- If Chatham changes their endpoint IDs, update `CURVES` in
  `fetch_curves.py`.
