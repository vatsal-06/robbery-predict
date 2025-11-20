#!/bin/bash
# Activate venv
source ../.venv/bin/activate
# Rebuild features
python ../features/build_features.py
# Retrain or skip retrain: you can retrain nightly or just score using latest model
python ../models/train_model.py
# Batch score: read last snapshot data and call API / write risk table
python - <<'PY'
import pandas as pd, requests, os, json
df = pd.read_csv("../data/features.csv")
# pick latest snapshot timestamp
latest = df['snap_time'].max()
last_snap = df[df['snap_time']==latest]
snaps = last_snap[["atm_id","recent_txn_count_7d","recent_avg_amt_7d","recent_fraud_count_7d","unique_from_acc_7d","recent_complaints_7d","atm_lat","atm_lon"]].to_dict(orient="records")
resp = requests.post("http://127.0.0.1:8000/score", json=snaps, timeout=180)
print(resp.json()[:5] if resp.ok else resp.text)
PY
