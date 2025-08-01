import pandas as pd
from web3 import Web3
import time

# load csv
df = pd.read_csv("UniswapEvents.csv", low_memory=False)

# take only the first 20000 rows
df_small = df.head(20000)

# connect to infura
w3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/27afdbb0d6ac48a58c0ab3a850c504c7"))

#error if link to infura/alchamy invalid
if not w3.is_connected():
    raise Exception("connection failed")

# function to fetch gas price
def fetch_gas_price(tx_hash):
    try:
        tx = w3.eth.get_transaction(tx_hash)
        gas_price_wei = tx['gasPrice']
        gas_price_gwei = w3.from_wei(gas_price_wei, 'gwei')
        return gas_price_gwei
    except Exception as e:
        print(f"error fetching {tx_hash}: {str(e).lower()}...continueing...")
        return None

# fetch gas prices
gas_prices = []
for idx, tx_hash in enumerate(df_small['TX_HASH']):
    gas_price = fetch_gas_price(tx_hash)
    gas_prices.append(gas_price)
    time.sleep(0.05)

    if (idx + 1) % 500 == 0:   # status update every 500 transactions
        print(f"Processed {idx + 1} transactions...")

# assign the gas prices to new column
df_small['GAS_PRICE_GWEI'] = gas_prices

# save trimmed + enriched file. Enriched file
df_small.to_csv("uniswap_swaps_20k_enriched.csv", index=False)