import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("alphabet_stock_dataEXP4,5,6.csv")

df["Date"] = pd.to_datetime(df["Date"])

data = df[(df["Date"] >= "2020-04-01") &
          (df["Date"] <= "2020-05-01")]

plt.plot(data["Date"], data["Close"])
plt.title("Alphabet Stock Price")
plt.xlabel("Date")
plt.ylabel("Close Price")
plt.show()
