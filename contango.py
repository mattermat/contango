import time
from datetime import datetime as dt
import pandas as pd
from binance.client import Client

client = Client()
client.ping()


coin_info = client.futures_coin_exchange_info()
coin_symbols = [
    c["symbol"]
    for c in coin_info["symbols"]
    if c["contractType"] != "PERPETUAL" and c["contractStatus"] == "TRADING"
]


def process_coin_entry(symbol):
    d = client.futures_coin_mark_price(symbol=symbol)[0]
    return (
        d["pair"],
        d["symbol"].split("_")[1],
        float(d["markPrice"]),
        float(d["estimatedSettlePrice"])
    )


res = []
for cs in coin_symbols:
    print(cs)
    res.append(process_coin_entry(cs))
    time.sleep(0.5)

df = pd.DataFrame(res, columns=["pair", "exp", "fut", "spot"])
df["exp"] = pd.to_datetime(df.exp, format="%y%m%d")
df["dte"] = (df.exp - dt.now()).dt.days
df["contango"] = df.fut / df.spot - 1
df["contango_ann"] = (1 + df.contango) ** (365 / df.dte) - 1
df = df.sort_values(by="contango_ann", ascending=False)
print(df)
