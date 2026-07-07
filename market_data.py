import requests
import pandas as pd
from datetime import datetime

# ==========================================
# GET NIFTY 5 MINUTE CANDLES
# ==========================================

def get_nifty_candles(access_token):

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    today = datetime.now().strftime("%Y-%m-%d")

    url = (
        f"https://api.upstox.com/v2/historical-candle/"
        f"NSE_INDEX%7CNifty%2050/5minute/{today}"
    )

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("Candle API Error")
        print(response.text)
        return None

    data = response.json()["data"]["candles"]

    df = pd.DataFrame(
        data,
        columns=[
            "Date",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
            "OI"
        ]
    )

    df["Date"] = pd.to_datetime(df["Date"])

    df = df.sort_values("Date").reset_index(drop=True)

    return df
