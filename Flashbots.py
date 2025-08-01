import pandas as pd
import requests
import time

# Load your suspicious swaps
df = pd.read_csv("uniswap_swaps_suspicious_only.csv")
tx_hashes = df["TX_HASH"].dropna().unique().tolist()

# Flashbots GraphQL API endpoint
url = "https://api.flashbots.net/graphql"


# GraphQL query template
def check_flashbots_bundle(tx_hash):
    query = {
        "query": f"""
        query {{
          bundles(
            first: 1
            where: {{
              transactions_some: {{
                hash: "{tx_hash}"
              }}
            }}
          ) {{
            id
            block_number
            miner_reward
            created_at
          }}
        }}
        """
    }

    try:
        response = requests.post(url, json=query)
        data = response.json()
        return bool(data["data"]["bundles"])
    except Exception as e:
        print(f"error fetching {tx_hash}: {str(e).lower()}")
        return False

# Run through TXs and flag
confirmed_flags = []
for i, tx_hash in enumerate(tx_hashes):
    result = check_flashbots_bundle(tx_hash)
    confirmed_flags.append({"TX_HASH": tx_hash, "IS_CONFIRMED_FLASHBOTS_MEV": result})
    if i % 10 == 0:
        print(f"Checked {i+1}/{len(tx_hashes)}...")
    time.sleep(0.4)  # avoid rate limit

# Save results
results_df = pd.DataFrame(confirmed_flags)
merged = df.merge(results_df, on="TX_HASH", how="left")
merged.to_csv("uniswap_swaps_confirmed_mev.csv", index=False)
print("✅ Saved to uniswap_swaps_confirmed_mev.csv")