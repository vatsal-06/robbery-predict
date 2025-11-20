# etl/load_csv_to_postgres.py
import pandas as pd
from sqlalchemy import create_engine, text
from geoalchemy2 import WKTElement
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine("postgresql://vatsalgupta@localhost:5432/ncrpdb")

def create_tables():
    with engine.begin() as conn:
        conn.execute(text("""
        CREATE EXTENSION IF NOT EXISTS postgis;
        CREATE TABLE IF NOT EXISTS atms (
            atm_id TEXT PRIMARY KEY,
            bank_id TEXT,
            lat DOUBLE PRECISION,
            lon DOUBLE PRECISION,
            address TEXT
        );
        CREATE TABLE IF NOT EXISTS atm_transactions (
            txn_id TEXT PRIMARY KEY,
            atm_id TEXT,
            txn_time TIMESTAMP,
            amount NUMERIC,
            from_acc TEXT,
            to_acc TEXT,
            is_fraud BOOLEAN
        );
        CREATE TABLE IF NOT EXISTS complaints (
            complaint_id TEXT PRIMARY KEY,
            complaint_time TIMESTAMP,
            victim_acc TEXT,
            atm_id TEXT,
            lat DOUBLE PRECISION,
            lon DOUBLE PRECISION,
            narrative TEXT
        );
        """))

def load_csvs(data_dir="data"):
    atms = pd.read_csv(f"{data_dir}/atms.csv")
    txns = pd.read_csv(f"{data_dir}/txns.csv", parse_dates=["txn_time"])
    comps = pd.read_csv(f"{data_dir}/complaints.csv", parse_dates=["complaint_time"])

    # upsert logic: for simplicity replace table
    atms.to_sql("atms", engine, if_exists="replace", index=False)
    txns.to_sql("atm_transactions", engine, if_exists="replace", index=False)
    comps.to_sql("complaints", engine, if_exists="replace", index=False)
    print("Loaded CSVs into Postgres.")

if __name__ == "__main__":
    create_tables()
    load_csvs()
