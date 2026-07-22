import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("alphabet_stock_dataEXP4,5,6.csv")

df["Date"] = pd.to_datetime(df["Date"])

data = df[(df["Date"] >= "2020-04-01") &
          (df["Date"] <= "2020-05-01")]

plt.scatter(data["Volume"], data["Close"])
plt.title("Volume vs Close Price")
plt.xlabel("Volume")
plt.ylabel("Close Price")
plt.show()
