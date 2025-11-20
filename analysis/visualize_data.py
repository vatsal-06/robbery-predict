import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd

# Ensure outputs folder exists
os.makedirs("outputs", exist_ok=True)

# Load data
atms = pd.read_csv("data/atms.csv")
txns = pd.read_csv("data/txns.csv", parse_dates=["txn_time"])
comps = pd.read_csv("data/complaints.csv", parse_dates=["complaint_time"])

# 1️⃣ Fraud vs Normal Transaction Counts
plt.figure(figsize=(6, 4))
sns.countplot(x="is_fraud", data=txns, palette="Set2")
plt.title("Fraud vs Normal Transaction Count")
plt.xlabel("Fraud Flag (0 = Normal, 1 = Fraud)")
plt.ylabel("Count")
plt.tight_layout()
plt.savefig("outputs/fraud_counts.png")
plt.close()

# 2️⃣ Distribution of Transaction Amounts
plt.figure(figsize=(6, 4))
sns.histplot(txns["amount"], bins=50, kde=True, color="skyblue")
plt.title("Distribution of Transaction Amounts")
plt.xlabel("Transaction Amount")
plt.ylabel("Frequency")
plt.tight_layout()
plt.savefig("outputs/txn_amount_distribution.png")
plt.close()

# 3️⃣ Complaints over Time
plt.figure(figsize=(8, 4))
comps.resample("D", on="complaint_time").size().plot(color="tomato")
plt.title("Daily Complaint Volume")
plt.xlabel("Date")
plt.ylabel("Number of Complaints")
plt.tight_layout()
plt.savefig("outputs/complaints_trend.png")
plt.close()

# 4️⃣ Heat Map of ATMs (Geospatial)
try:
    # Load India boundary shapefile from Natural Earth (direct URL)
    world = gpd.read_file("https://naciscdn.org/naturalearth/110m_cultural/ne_110m_admin_0_countries.zip")
    india = world[world["ADMIN"] == "India"]

    gdf = gpd.GeoDataFrame(
        atms,
        geometry=gpd.points_from_xy(atms.lon, atms.lat),
        crs="EPSG:4326"
    )

    ax = india.plot(color="lightgrey", figsize=(6, 6))
    gdf.plot(ax=ax, color="red", alpha=0.6, markersize=25)
    plt.title("ATM Locations Across India")
    plt.tight_layout()
    plt.savefig("outputs/atm_heatmap.png")
    plt.close()

except Exception as e:
    print("⚠️ Skipping map plot — GeoPandas world data issue:", e)

# 5️⃣ Correlation Heatmap of Key Features
complaint_counts = comps.groupby("atm_id").size().rename("complaint_count")

features = (
    txns[["atm_id", "amount", "is_fraud"]]
    .join(complaint_counts, on="atm_id")
    .fillna(0)
)

corr = features[["amount", "is_fraud", "complaint_count"]].corr(numeric_only=True)

plt.figure(figsize=(5, 4))
sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", cbar=True)
plt.title("Feature Correlation Heatmap")
plt.tight_layout()
plt.savefig("outputs/feature_correlation.png")
plt.close()

print("✅ All visualizations saved in the outputs/ folder:")
print("   - fraud_counts.png")
print("   - txn_amount_distribution.png")
print("   - complaints_trend.png")
print("   - atm_heatmap.png")
print("   - feature_correlation.png")
