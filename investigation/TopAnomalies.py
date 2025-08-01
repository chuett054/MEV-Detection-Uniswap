import pandas as pd
import matplotlib.pyplot as plt


#uses matplotlib to show


df = pd.read_csv("uniswap_swaps_anomaly_detection.csv")


suspicious = df[df['is_anomaly'] == 1]

plt.scatter(suspicious['GAS_PRICE_GWEI'], suspicious['SLIPPAGE_RATIO'], alpha=0.5)
plt.xlabel('gas Price (Gwei)')
plt.ylabel('slippage Ratio')
plt.title('suspicious Uniswap Swaps: gas vs slippage')
plt.show()

