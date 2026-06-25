import streamlit as st
import requests
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from datetime import date

st_autorefresh(interval=30000, key="refresh")

ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiI2OEFKUVUiLCJqdGkiOiI2YTNkM2NhNzNkZmE2NTYzZTA2NzI4M2YiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6dHJ1ZSwiaWF0IjoxNzgyMzk4MTE5LCJpc3MiOiJ1ZGFwaS1nYXRld2F5LXNlcnZpY2UiLCJleHAiOjE3ODI0MjQ4MDB9.0R1cqy9E4XTz3W-dm2nWMv82gmjA0JQYumtTd0vZvYs"

headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

today = date.today().strftime("%Y-%m-%d")

url = (
    f"https://api.upstox.com/v2/option/chain"
    f"?instrument_key=NSE_INDEX%7CNifty%2050"
    f"&expiry_date={today}"
)

response = requests.get(url, headers=headers)

if response.status_code == 200:

    data = response.json()["data"]

    rows = []

    for item in data:

        strike = item["strike_price"]

        ce_data = item.get("call_options", {})
        pe_data = item.get("put_options", {})

        rows.append({
            "Strike": strike,

            "CE_OI": ce_data.get("market_data", {}).get("oi", 0),
            "PE_OI": pe_data.get("market_data", {}).get("oi", 0),

            "CE_OI_CHANGE": ce_data.get("market_data", {}).get("oi_day_change", 0),
            "PE_OI_CHANGE": pe_data.get("market_data", {}).get("oi_day_change", 0),

            "CE_LTP": ce_data.get("market_data", {}).get("ltp", 0),
            "PE_LTP": pe_data.get("market_data", {}).get("ltp", 0)
        })

    df = pd.DataFrame(rows)

    # ===================================
    # CURRENT SPOT
    # ===================================

    spot = data[0]["underlying_spot_price"]

    atm_strike = min(
        df["Strike"],
        key=lambda x: abs(x - spot)
    )

    # ===================================
    # NEARBY STRIKES
    # ===================================

    near_df = df[
        (df["Strike"] >= spot - 500) &
        (df["Strike"] <= spot + 500)
    ]

    # ===================================
    # SUPPORT
    # ===================================

    support = (
        near_df
        .sort_values("PE_OI", ascending=False)
        .head(3)
        [["Strike", "PE_OI"]]
    )

    # ===================================
    # RESISTANCE
    # ===================================

    resistance = (
        near_df
        .sort_values("CE_OI", ascending=False)
        .head(3)
        [["Strike", "CE_OI"]]
    )

    # ===================================
    # PCR
    # ===================================

    total_put_oi = df["PE_OI"].sum()
    total_call_oi = df["CE_OI"].sum()

    pcr = round(
        total_put_oi / total_call_oi,
        2
    ) if total_call_oi else 0

    st.write("Total Put OI:", total_put_oi)
st.write("Total Call OI:", total_call_oi)
st.write("PCR:", pcr)

st.subheader("Raw API Data")
st.json(data[0])

    # ===================================
    # OI BUILDUP
    # ===================================

pcr = round(
    total_put_oi / total_call_oi,
    2
) if total_call_oi else 0

st.write("Total Put OI:", total_put_oi)
st.write("Total Call OI:", total_call_oi)
st.write("PCR:", pcr)

call_writing = (
    near_df
    .sort_values("CE_OI_CHANGE", ascending=False)

    put_writing = (
        near_df
        .sort_values("PE_OI_CHANGE", ascending=False)
        .head(3)
        [["Strike", "PE_OI_CHANGE"]]
    )

    # ===================================
    # MARKET VIEW
    # ===================================

    if pcr > 1.2:
        market_view = "BULLISH"

    elif pcr < 0.8:
        market_view = "BEARISH"

    else:
        market_view = "NEUTRAL"

    # ===================================
    # DASHBOARD HEADER
    # ===================================

    st.title("NIFTY OPTION CHAIN DASHBOARD BY NAMAN")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("NIFTY", round(spot, 2))
    col2.metric("ATM", atm_strike)
    col3.metric("PCR", pcr)
    col4.metric("VIEW", market_view)

    # ===================================
    # SUMMARY TABLE
    # ===================================

    summary = pd.DataFrame({
        "Metric": [
            "Spot",
            "ATM",
            "PCR",
            "Market View",
            "Strongest Support",
            "Strongest Resistance"
        ],
        "Value": [
            round(spot, 2),
            atm_strike,
            pcr,
            market_view,
            support.iloc[0]["Strike"],
            resistance.iloc[0]["Strike"]
        ]
    })

    st.subheader("Market Summary")
    st.table(summary)

    # ===================================
    # SUPPORT TABLE
    # ===================================

    st.subheader("Top Support Levels")

    st.table(
        support.rename(
            columns={
                "PE_OI": "Put OI"
            }
        )
    )

    # ===================================
    # RESISTANCE TABLE
    # ===================================

    st.subheader("Top Resistance Levels")

    st.table(
        resistance.rename(
            columns={
                "CE_OI": "Call OI"
            }
        )
    )

    # ===================================
    # CALL WRITING
    # ===================================

    st.subheader("Fresh Call Writing")

    st.table(call_writing)

    # ===================================
    # PUT WRITING
    # ===================================

    st.subheader("Fresh Put Writing")

    st.table(put_writing)

    # ===================================
    # PCR TABLE
    # ===================================

    pcr_table = pd.DataFrame({
        "Total Put OI": [total_put_oi],
        "Total Call OI": [total_call_oi],
        "PCR": [pcr]
    })

    st.subheader("PCR Analysis")
    st.table(pcr_table)

    # ===================================
    # COMPLETE OPTION CHAIN
    # ===================================

    st.subheader("Live Option Chain")

    st.dataframe(
        df.sort_values("Strike")
    )


