# api/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from joblib import load
import pandas as pd
import os
from typing import List

MODEL_PATH = os.getenv("MODEL_PATH", "models/latest_rf_pipeline.joblib")
app = FastAPI(title="ATM Risk API")

# Load model once
try:
    model = load(MODEL_PATH)
except Exception as e:
    model = None
    print("Warning: Could not load model:", e)

class Snapshot(BaseModel):
    atm_id: str
    recent_txn_count_7d: int
    recent_avg_amt_7d: float
    recent_fraud_count_7d: int
    unique_from_acc_7d: int
    recent_complaints_7d: int
    atm_lat: float
    atm_lon: float

@app.get("/health")
def health():
    return {"status":"ok", "model_loaded": model is not None}

@app.post("/score")
def score_snapshots(snaps: List[Snapshot]):
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded.")
    # convert to dataframe
    df = pd.DataFrame([s.dict() for s in snaps])
    features = ["recent_txn_count_7d","recent_avg_amt_7d","recent_fraud_count_7d","unique_from_acc_7d","recent_complaints_7d","atm_lat","atm_lon"]
    X = df[features].fillna(0)
    probs = model.predict_proba(X)[:,1]
    df['risk_score'] = probs
    # return sorted by risk
    res = df.sort_values("risk_score", ascending=False).to_dict(orient="records")
    return {"results": res}
