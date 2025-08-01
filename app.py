import streamlit as st
import pandas as pd
import joblib
from flipside import Flipside
from datetime import datetime
from sklearn.preprocessing import StandardScaler

# --- Load model + scaler ---
model = joblib.load("TrainedModels/mev_classifier_binary_xgb.pkl")
scaler = joblib.load("scaler.pkl")

# --- Flipside credentials ---
API_KEY = "f358bb27-ddc5-4131-938e-4cbbdace5b85"
API_URL = "https://api-v2.flipsidecrypto.xyz"
flipside = Flipside(API_KEY, API_URL)

# --- Streamlit UI ---
st.title("🔎 Real-Time MEV Prediction Dashboard")
st.markdown("This app fetches recent Uniswap swaps and predicts if each transaction is MEV-related.")

# --- Query Swaps ---
def get_recent_swaps():
    sql = """
    SELECT
        block_number,
        block_timestamp,
        tx_hash,
        sender,
        recipient,
        pool_address,
        token0_symbol,
        token1_symbol,
        amount0_adjusted,
        amount1_adjusted,
        amount0_usd,
        amount1_usd,
        amount1_usd / NULLIF(amount0_usd, 0) AS slippage_ratio
    FROM ethereum.uniswapv3.ez_swaps
    WHERE block_timestamp >= GETDATE() - INTERVAL '4 hour'
    ORDER BY block_timestamp DESC
    LIMIT 200
    """
    result = flipside.query(sql)
    records = result.records
    columns = result.columns
    return pd.DataFrame(records, columns=columns)
# --- Fetch and process data ---
df = get_recent_swaps()

if df.empty:
    st.warning("No data returned from Flipside.")
else:
    # Feature engineering
    df["SLIPPAGE_RATIO"] = df["slippage_ratio"].fillna(0)
    df["SWAP_USD"] = df["amount0_usd"].fillna(0) + df["amount1_usd"].fillna(0)
    df["HOUR"] = pd.to_datetime(df["block_timestamp"]).dt.hour
    df["IS_SELF_SWAP"] = (df["sender"] == df["recipient"]).astype(int)
    df["WALLET_AGE"] = 0  # Placeholder, still
    df["TX_COUNT"] = 1    # Placeholder

    # Features for model
    features = ["SLIPPAGE_RATIO", "SWAP_USD", "HOUR", "IS_SELF_SWAP", "WALLET_AGE", "TX_COUNT"]
    X = df[features]
    X_scaled = scaler.transform(X)

    # Prediction
    df["Predicted Label"] = model.predict(X_scaled)
    df["Confidence"] = model.predict_proba(X_scaled).max(axis=1)

    # Display output
    st.subheader("📋 Predictions")
    st.dataframe(df[["block_timestamp", "tx_hash", "Predicted Label", "Confidence"]])

    # Download option
    st.download_button("📥 Download CSV", df.to_csv(index=False), "predictions.csv", "text/csv")