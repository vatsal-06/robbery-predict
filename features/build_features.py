# features/build_features.py
import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()
DB_URL = os.getenv("DB_URL", "postgresql://ncrp:ncrp_pass@localhost:5432/ncrpdb")
engine = create_engine(DB_URL)

def load_tables():
    txns = pd.read_sql("SELECT * FROM atm_transactions", engine, parse_dates=["txn_time"])
    atms = pd.read_sql("SELECT * FROM atms", engine)
    comps = pd.read_sql("SELECT * FROM complaints", engine, parse_dates=["complaint_time"])
    return txns, atms, comps

def build_features(output_path="data/features.csv"):
    txns, atms, comps = load_tables()
    txns['txn_time'] = pd.to_datetime(txns['txn_time'])
    comps['complaint_time'] = pd.to_datetime(comps['complaint_time'])
    # define snapshots (one snapshot per atm per day for last N days)
    end = txns['txn_time'].max()
    start = end - pd.Timedelta(days=30)
    snapshots = pd.date_range(start=start + pd.Timedelta(days=1), end=end, freq='12H')
    rows = []
    for snap in snapshots:
        lookback_7d = snap - pd.Timedelta(days=7)
        future_24h = snap + pd.Timedelta(days=1)
        for _, atm in atms.iterrows():
            atm_id = atm['atm_id']
            recent = txns[(txns['atm_id']==atm_id) & (txns['txn_time']>=lookback_7d) & (txns['txn_time']<snap)]
            future = txns[(txns['atm_id']==atm_id) & (txns['txn_time']>=snap) & (txns['txn_time']<future_24h)]
            recent_comps = comps[(comps['atm_id']==atm_id) & (comps['complaint_time']>=lookback_7d) & (comps['complaint_time']<snap)]
            rows.append({
                "snap_time": snap,
                "atm_id": atm_id,
                "recent_txn_count_7d": len(recent),
                "recent_avg_amt_7d": float(recent['amount'].mean()) if len(recent)>0 else 0.0,
                "recent_fraud_count_7d": int(recent['is_fraud'].sum()) if len(recent)>0 else 0,
                "unique_from_acc_7d": int(recent['from_acc'].nunique()) if len(recent)>0 else 0,
                "recent_complaints_7d": int(len(recent_comps)),
                "atm_lat": atm['lat'],
                "atm_lon": atm['lon'],
                "label": 1 if (future['is_fraud'].sum() > 0) else 0
            })
    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)
    print("Saved features to", output_path)

if __name__ == "__main__":
    build_features()
