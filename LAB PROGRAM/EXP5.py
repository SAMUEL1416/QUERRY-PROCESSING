import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("alphabet_stock_dataEXP4,5,6.csv")

plt.figure(figsize=(12,5))

plt.bar(range(len(df)), df["Volume"])

plt.xticks(range(len(df)), df["Date"], rotation=45)

plt.title("Trading Volume of Alphabet Inc.")
plt.xlabel("Date")
plt.ylabel("Volume")

plt.tight_layout()
plt.show()
