# data/generate_mock_data.py
import pandas as pd, numpy as np
from datetime import datetime, timedelta
import random, uuid, os

# ✅ Ensure "data" folder exists before saving
os.makedirs("data", exist_ok=True)

n_atms = 200
atms = []
banks = ["SBI", "HDFC", "ICICI", "PNB", "Axis", "BOB"]

# --- Generate random ATMs around Delhi NCR ---
for i in range(n_atms):
    atms.append({
        "atm_id": f"ATM_{i:04d}",
        "bank_id": random.choice(banks),
        "lat": 28.4 + np.random.rand() / 2,  # Latitude roughly 28.4–28.9
        "lon": 76.8 + np.random.rand() / 2,  # Longitude roughly 76.8–77.3
        "address": f"ATM {i} Delhi"
    })

atms = pd.DataFrame(atms)
atms.to_csv("data/atms.csv", index=False)

# --- Generate random transactions ---
rows = []
start = datetime(2024, 1, 1)

for i in range(50000):
    atm = atms.sample(1).iloc[0]
    t = start + timedelta(minutes=random.randint(0, 60 * 24 * 60))
    amt = np.random.choice([500, 1000, 2000, 5000, 10000], p=[.3, .3, .2, .15, .05])
    fraud = np.random.rand() < 0.02  # 2% fraud rate

    rows.append({
        "txn_id": str(uuid.uuid4())[:8],
        "atm_id": atm.atm_id,
        "txn_time": t,
        "amount": amt,
        "from_acc": f"A{random.randint(10000, 99999)}",
        "to_acc": f"A{random.randint(10000, 99999)}",
        "is_fraud": fraud
    })

txns_df = pd.DataFrame(rows)
txns_df.to_csv("data/txns.csv", index=False)

# --- Generate complaints linked to fraudulent txns ---
complaints = []
fraud_txns = txns_df[txns_df["is_fraud"] == True]

for _, txn in fraud_txns.iterrows():
    complaints.append({
        "complaint_id": str(uuid.uuid4())[:8],
        "complaint_time": txn["txn_time"] + timedelta(hours=random.randint(1, 48)),
        "victim_acc": txn["from_acc"],
        "atm_id": txn["atm_id"],
        "lat": atms.loc[atms["atm_id"] == txn["atm_id"], "lat"].values[0],
        "lon": atms.loc[atms["atm_id"] == txn["atm_id"], "lon"].values[0],
        "narrative": "Unauthorized withdrawal complaint"
    })

pd.DataFrame(complaints).to_csv("data/complaints.csv", index=False)

print("✅ Mock data generated successfully! Files saved to ./data/")
