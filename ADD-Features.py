import pandas as pd

# load dataset
df = pd.read_csv("uniswap_swaps_20k_enriched.csv")

# grab value in USD
df['SWAP_USD'] = df[['AMOUNT0_USD', 'AMOUNT1_USD']].max(axis=1)

# Hour of day
df['HOUR_OF_DAY'] = pd.to_datetime(df['BLOCK_TIMESTAMP']).dt.hour

# TRUE if slippage is high
df['IS_HIGH_SLIPPAGE'] = df['SLIPPAGE_RATIO'] > 0.05  # Adjust threshold later if needed

# if sender == recipient
df['IS_SAME_SENDER_RECIPIENT'] = df['SENDER'].str.lower() == df['RECIPIENT'].str.lower()

# save dataset with these features
df.to_csv("uniswap_swaps_with_features.csv", index=False)