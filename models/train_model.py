# models/train_model.py
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, precision_score, classification_report
from joblib import dump
import os

FEATURE_FILE = os.getenv("FEATURE_FILE", "data/features.csv")
MODEL_OUT = os.getenv("MODEL_OUT", "models/latest_rf_pipeline.joblib")

def load_features():
    df = pd.read_csv(FEATURE_FILE, parse_dates=["snap_time"])
    return df

def train():
    df = load_features()
    # choose feature columns
    features = ["recent_txn_count_7d","recent_avg_amt_7d","recent_fraud_count_7d","unique_from_acc_7d","recent_complaints_7d","atm_lat","atm_lon"]
    X = df[features].fillna(0)
    y = df['label']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y if len(y.unique())>1 else None)

    pipe = Pipeline([("scaler", StandardScaler()), ("rf", RandomForestClassifier(n_estimators=200, class_weight="balanced", random_state=42))])
    pipe.fit(X_train, y_train)
    y_proba = pipe.predict_proba(X_test)[:,1]
    auc = roc_auc_score(y_test, y_proba) if len(y_test.unique())>1 else float("nan")
    y_pred = (y_proba >= 0.5).astype(int)
    prec = precision_score(y_test, y_pred, zero_division=0)
    print("AUC:", auc)
    print("Precision:", prec)
    print("Classification report:\n", classification_report(y_test, y_pred, zero_division=0))
    os.makedirs(os.path.dirname(MODEL_OUT), exist_ok=True)
    dump(pipe, MODEL_OUT)
    print("Saved model to", MODEL_OUT)

if __name__ == "__main__":
    train()
