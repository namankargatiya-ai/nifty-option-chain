import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import date, timedelta, datetime

# ===================================
# PAGE CONFIG
# ===================================
st.set_page_config(
    page_title="Nifty Option Chain Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ===================================
# AUTO REFRESH (every 30 seconds)
# ===================================
try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=30000, key="refresh")
except ImportError:
    pass

# ===================================
# DARK THEME CSS
# ===================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background-color: #0d1117 !important;
    color: #e6edf3 !important;
}
.stApp { background-color: #0d1117 !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem !important; max-width: 100% !important; }

.dash-title {
    text-align: center; font-size: 1.7rem; font-weight: 700;
    color: #e6edf3; letter-spacing: 0.04em; margin-bottom: 0.1rem;
}
.dash-subtitle {
    text-align: center; font-size: 0.8rem;
    color: #8b949e; margin-bottom: 1.2rem;
}
.refresh-icon { color: #3fb950; font-size: 1.2rem; }

.metric-card {
    background: #161b22; border: 1px solid #30363d;
    border-radius: 10px; padding: 1rem 1.2rem; text-align: left;
}
.metric-label {
    font-size: 0.72rem; color: #8b949e; font-weight: 600;
    letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 0.3rem;
}
.metric-value {
    font-size: 2rem; font-weight: 700;
    font-family: 'JetBrains Mono', monospace; line-height: 1;
}
.metric-value.green  { color: #3fb950; }
.metric-value.cyan   { color: #58a6ff; }
.metric-value.yellow { color: #d29922; }
.metric-value.purple { color: #a371f7; }
.metric-value.red    { color: #f85149; }
.metric-icon { float: right; font-size: 1.5rem; opacity: 0.5; margin-top: -2.5rem; }

.section-card {
    background: #161b22; border: 1px solid #30363d;
    border-radius: 10px; padding: 1rem 1.2rem;
    margin-bottom: 0.8rem; height: 100%;
}
.section-title {
    font-size: 0.75rem; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; text-align: center;
    margin-bottom: 0.7rem; padding-bottom: 0.5rem;
    border-bottom: 1px solid #30363d;
}
.title-blue   { color: #58a6ff; }
.title-green  { color: #3fb950; }
.title-red    { color: #f85149; }
.title-yellow { color: #d29922; }
.title-orange { color: #e3b341; }
.title-purple { color: #a371f7; }

.dash-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
.dash-table th {
    color: #8b949e; font-weight: 600; text-align: center;
    padding: 0.3rem 0.5rem; border-bottom: 1px solid #30363d;
    font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em;
}
.dash-table td {
    text-align: center; padding: 0.35rem 0.5rem;
    font-family: 'JetBrains Mono', monospace;
    border-bottom: 1px solid #21262d;
}
.dash-table tr:last-child td { border-bottom: none; }
.dash-table .strike-col { color: #e6edf3; font-weight: 600; }
.dash-table .green-val  { color: #3fb950; }
.dash-table .red-val    { color: #f85149; }
.dash-table .yellow-val { color: #d29922; }
.dash-table .cyan-val   { color: #58a6ff; }

.signal-badge {
    display: inline-block; padding: 2px 10px;
    border-radius: 20px; font-size: 0.72rem;
    font-weight: 700; letter-spacing: 0.06em;
}
.badge-buy     { background: #0d2317; color: #3fb950; border: 1px solid #3fb950; }
.badge-sell    { background: #1f0d0d; color: #f85149; border: 1px solid #f85149; }
.badge-neutral { background: #1c1c1c; color: #8b949e; border: 1px solid #30363d; }

.ind-row {
    display: flex; justify-content: space-between;
    align-items: center; padding: 0.32rem 0;
    border-bottom: 1px solid #21262d; font-size: 0.82rem;
}
.ind-row:last-child { border-bottom: none; }
.ind-label { color: #8b949e; font-size: 0.75rem; }
.ind-value { font-family: 'JetBrains Mono', monospace; font-weight: 600; }

.rsi-bar-bg {
    background: #21262d; border-radius: 4px;
    height: 6px; width: 100%; margin-top: 4px;
}
.rsi-bar-fill { height: 6px; border-radius: 4px; }

.chain-card {
    background: #161b22; border: 1px solid #30363d;
    border-radius: 10px; padding: 1rem 1.2rem; margin-top: 0.8rem;
    overflow-x: auto;
}
.chain-table {
    width: 100%; border-collapse: collapse;
    font-size: 0.78rem; min-width: 700px;
}
.chain-table th {
    padding: 0.4rem 0.8rem; font-size: 0.7rem; font-weight: 700;
    letter-spacing: 0.07em; text-transform: uppercase;
    border-bottom: 2px solid #30363d;
}
.chain-table th.calls-col { color: #3fb950; text-align: center; background: #0d2317; }
.chain-table th.puts-col  { color: #f85149; text-align: center; background: #1f0d0d; }
.chain-table th.strike-h  { color: #d29922; text-align: center; }
.chain-table td {
    text-align: right; padding: 0.32rem 0.8rem;
    font-family: 'JetBrains Mono', monospace;
    border-bottom: 1px solid #21262d;
}
.chain-table td.strike-col,
.chain-table td.atm-strike { text-align: center; }
.chain-table tr:last-child td { border-bottom: none; }
.chain-table tbody tr:hover { background: #1f2937; }
.chain-table .atm-row td { background: #2d2a1a !important; font-weight: 700; }
.chain-table .atm-strike { color: #d29922; font-weight: 700; }
.chain-table .atm-badge {
    background: #d29922; color: #0d1117; border-radius: 4px;
    padding: 1px 5px; font-size: 0.65rem; margin-left: 4px;
    font-weight: 700; vertical-align: middle;
}
.green-val   { color: #3fb950; }
.red-val     { color: #f85149; }
.neutral-val { color: #8b949e; }
.strike-col  { color: #c9d1d9; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ===================================
# DATE LOGIC (nearest Tuesday)
# ===================================
today = date.today()
if today.weekday() != 1:
    days_until_tuesday = (1 - today.weekday()) % 7
    if days_until_tuesday == 0:
        days_until_tuesday = 7
    today = today + timedelta(days=days_until_tuesday)

expiry_str   = today.strftime("%Y-%m-%d")
last_updated = date.today().strftime("%d-%m-%Y")

# ===================================
# API CALL — Option Chain
# ===================================
ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiI2OEFKUVUiLCJqdGkiOiI2YTQxZWI5NmYyNGJiZjFjMjA0ZWFkODIiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6dHJ1ZSwiaXNFeHRlbmRlZCI6dHJ1ZSwiaWF0IjoxNzgyNzA1MDQ2LCJpc3MiOiJ1ZGFwaS1nYXRld2F5LXNlcnZpY2UiLCJleHAiOjE4MTQzMDY0MDB9.LuQ-H-ix7cRKRvn_8DEE2r5_VhOoLK2Szz4VHn3qAxE"  # <-- Apna token yahan daalo

headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

url = (
    f"https://api.upstox.com/v2/option/chain"
    f"?instrument_key=NSE_INDEX%7CNifty%2050&expiry_date={expiry_str}"
)
response = requests.get(url, headers=headers)

# ===================================
# HELPERS
# ===================================
def fmt_num(val):
    try:
        val = float(val)
    except (TypeError, ValueError):
        return "-"
    sign = "-" if val < 0 else ""
    s = str(int(abs(val)))
    if len(s) <= 3:
        return sign + s
    result = s[-3:]
    s = s[:-3]
    while len(s) > 2:
        result = s[-2:] + "," + result
        s = s[:-2]
    if s:
        result = s + "," + result
    return sign + result

def color_change(val):
    c    = "green-val" if val >= 0 else "red-val"
    sign = "+" if val >= 0 else ""
    return f'<td class="{c}">{sign}{fmt_num(val)}</td>'

def signal_badge(signal):
    if signal == "BUY":
        return '<span class="signal-badge badge-buy">▲ BUY</span>'
    elif signal == "SELL":
        return '<span class="signal-badge badge-sell">▼ SELL</span>'
    else:
        return '<span class="signal-badge badge-neutral">◆ NEUTRAL</span>'

# ===================================
# OHLC API — RSI + VWAP
# (session_state mein last valid data store)
# ===================================
def fetch_ohlc(token):
    ohlc_url = (
        "https://api.upstox.com/v2/historical-candle/intraday/"
        "NSE_INDEX%7CNifty%2050/5minute"
    )
    h = {"Accept": "application/json", "Authorization": f"Bearer {token}"}
    try:
        r = requests.get(ohlc_url, headers=h, timeout=10)
        if r.status_code == 200:
            candles = r.json().get("data", {}).get("candles", [])
            if candles and len(candles) >= 15:
                ohlc = pd.DataFrame(
                    candles,
                    columns=["ts","open","high","low","close","volume","oi"]
                )
                ohlc = ohlc.sort_values("ts").reset_index(drop=True)
                ohlc[["open","high","low","close","volume"]] = \
                    ohlc[["open","high","low","close","volume"]].astype(float)
                # Save last valid data
                st.session_state.last_ohlc      = ohlc
                st.session_state.last_ohlc_time = datetime.now().strftime("%d-%m-%Y %H:%M")
                return ohlc, False   # False = live
    except Exception:
        pass

    # Market closed or API failed — use last saved
    if "last_ohlc" in st.session_state:
        return st.session_state.last_ohlc, True  # True = stale
    return None, False

# ===================================
# INDICATOR CALCULATIONS
# ===================================
def calc_rsi(series, period=14):
    delta = series.diff()
    gain  = delta.clip(lower=0)
    loss  = -delta.clip(upper=0)
    avg_g = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_l = loss.ewm(com=period - 1, min_periods=period).mean()
    rs    = avg_g / avg_l.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def calc_vwap(ohlc):
    tp         = (ohlc["high"] + ohlc["low"] + ohlc["close"]) / 3
    cum_vol    = ohlc["volume"].cumsum()
    cum_tp_vol = (tp * ohlc["volume"]).cumsum()
    return cum_tp_vol / cum_vol.replace(0, np.nan)

def calc_pivots(ohlc):
    prev = ohlc.iloc[:-1] if len(ohlc) > 1 else ohlc
    H = prev["high"].max()
    L = prev["low"].min()
    C = prev["close"].iloc[-1]
    P  = (H + L + C) / 3
    R1 = 2 * P - L
    S1 = 2 * P - H
    R2 = P + (H - L)
    S2 = P - (H - L)
    R3 = H + 2 * (P - L)
    S3 = L - 2 * (H - P)
    return {"P": P, "R1": R1, "R2": R2, "R3": R3,
            "S1": S1, "S2": S2, "S3": S3}

# ===================================
# FETCH OHLC
# ===================================
ohlc_df, is_stale = fetch_ohlc(ACCESS_TOKEN)

rsi_val  = None
vwap_val = None
pivots   = None
rsi_sig  = "NEUTRAL"
vwap_sig = "NEUTRAL"

if ohlc_df is not None and len(ohlc_df) >= 15:
    rsi_series  = calc_rsi(ohlc_df["close"])
    rsi_val     = round(rsi_series.iloc[-1], 2)
    vwap_series = calc_vwap(ohlc_df)
    vwap_val    = round(vwap_series.iloc[-1], 2)
    pivots      = calc_pivots(ohlc_df)

    rsi_sig = "BUY" if rsi_val >= 60 else ("SELL" if rsi_val <= 40 else "NEUTRAL")

pivot_sig  = "NEUTRAL"
pivot_zone = "No data"

# ===================================
# TITLE  (with live/stale indicator)
# ===================================
stale_label = ""
if "last_ohlc_time" in st.session_state:
    data_src = (
        f'<span style="color:#f85149">⚠️ Last: {st.session_state.last_ohlc_time}</span>'
        if is_stale else
        '<span style="color:#3fb950">● Live</span>'
    )
    stale_label = f"&nbsp;|&nbsp; Indicators: {data_src}"

st.markdown(f"""
<div class="dash-title">
    NIFTY OPTION CHAIN DASHBOARD BY NAMAN &nbsp;<span class="refresh-icon">↻</span>
</div>
<div class="dash-subtitle">
    Last Updated: <span style="color:#3fb950">{last_updated}</span>
    &nbsp;|&nbsp;
    Expiry: <span style="color:#58a6ff">{expiry_str}</span>
    {stale_label}
</div>
""", unsafe_allow_html=True)

if response.status_code != 200:
    st.error(f"❌ API Error {response.status_code}: Token check karein ya market band ho sakti hai.")
    st.stop()

# ===================================
# DATA PROCESSING — Option Chain
# ===================================
data = response.json()["data"]
rows = []
for item in data:
    strike  = item["strike_price"]
    ce_data = item.get("call_options", {})
    pe_data = item.get("put_options",  {})
    rows.append({
        "Strike":       strike,
        "CE_OI":        ce_data.get("market_data", {}).get("oi",            0) or 0,
        "PE_OI":        pe_data.get("market_data", {}).get("oi",            0) or 0,
        "CE_OI_CHANGE": ce_data.get("market_data", {}).get("oi_day_change", 0) or 0,
        "PE_OI_CHANGE": pe_data.get("market_data", {}).get("oi_day_change", 0) or 0,
        "CE_LTP":       ce_data.get("market_data", {}).get("ltp",           0) or 0,
        "PE_LTP":       pe_data.get("market_data", {}).get("ltp",           0) or 0,
    })

df = pd.DataFrame(rows).reset_index(drop=True)
spot       = data[0]["underlying_spot_price"]
atm_strike = min(df["Strike"], key=lambda x: abs(x - spot))

# ===================================
# OI CHANGE — session_state method
# ===================================
current_oi = {
    str(int(row["Strike"])): {
        "CE_OI": int(row["CE_OI"]),
        "PE_OI": int(row["PE_OI"])
    }
    for _, row in df.iterrows()
}

if "prev_oi" not in st.session_state:
    st.session_state.prev_oi = {}

prev_oi = st.session_state.prev_oi

if prev_oi:
    def get_change(strike, side):
        key  = str(int(strike))
        curr = current_oi.get(key, {}).get(side, 0)
        prev = prev_oi.get(key, {}).get(side, 0)
        return curr - prev
    df["CE_OI_CHANGE"] = df["Strike"].apply(lambda s: get_change(s, "CE_OI"))
    df["PE_OI_CHANGE"] = df["Strike"].apply(lambda s: get_change(s, "PE_OI"))
else:
    df["CE_OI_CHANGE"] = 0
    df["PE_OI_CHANGE"] = 0

st.session_state.prev_oi = current_oi

# ===================================
# DERIVED DATA
# ===================================
near_df    = df[(df["Strike"] >= spot - 500) & (df["Strike"] <= spot + 500)]
support    = near_df.sort_values("PE_OI", ascending=False).head(3)[["Strike", "PE_OI"]]
resistance = near_df.sort_values("CE_OI", ascending=False).head(3)[["Strike", "CE_OI"]]

total_put_oi  = df["PE_OI"].sum()
total_call_oi = df["CE_OI"].sum()
pcr           = round(total_put_oi / total_call_oi, 2) if total_call_oi else 0

if pcr > 1.2:
    market_view = "BULLISH"; view_color = "green-val"
elif pcr < 0.8:
    market_view = "BEARISH"; view_color = "red-val"
else:
    market_view = "NEUTRAL"; view_color = "yellow-val"

# ===================================
# VWAP + PIVOT SIGNALS
# (needs spot, so computed after data processing)
# ===================================
if vwap_val is not None:
    if spot > vwap_val * 1.001:
        vwap_sig = "BUY"
    elif spot < vwap_val * 0.999:
        vwap_sig = "SELL"
    else:
        vwap_sig = "NEUTRAL"

if pivots:
    if spot > pivots["R2"]:
        pivot_sig  = "SELL"; pivot_zone = f"Above R2 ({pivots['R2']:,.0f})"
    elif spot > pivots["R1"]:
        pivot_sig  = "BUY";  pivot_zone = f"R1–R2 ({pivots['R1']:,.0f}–{pivots['R2']:,.0f})"
    elif spot > pivots["P"]:
        pivot_sig  = "BUY";  pivot_zone = f"Pivot–R1 ({pivots['P']:,.0f}–{pivots['R1']:,.0f})"
    elif spot > pivots["S1"]:
        pivot_sig  = "NEUTRAL"; pivot_zone = f"S1–Pivot ({pivots['S1']:,.0f}–{pivots['P']:,.0f})"
    elif spot > pivots["S2"]:
        pivot_sig  = "SELL"; pivot_zone = f"S2–S1 ({pivots['S2']:,.0f}–{pivots['S1']:,.0f})"
    else:
        pivot_sig  = "SELL"; pivot_zone = f"Below S2 ({pivots['S2']:,.0f})"

# Overall signal — majority vote
signals    = [rsi_sig, vwap_sig, pivot_sig]
buy_count  = signals.count("BUY")
sell_count = signals.count("SELL")
if buy_count >= 2:
    overall_sig = "BUY"
elif sell_count >= 2:
    overall_sig = "SELL"
else:
    overall_sig = "NEUTRAL"

# ===================================
# TOP METRIC CARDS
# ===================================
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">NIFTY SPOT</div>
        <div class="metric-value green">{round(spot, 2):,.2f}</div>
        <div class="metric-icon">📈</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">ATM STRIKE</div>
        <div class="metric-value cyan">{atm_strike:,.0f}</div>
        <div class="metric-icon">⚙️</div>
    </div>""", unsafe_allow_html=True)

with c3:
    pcr_color = "green" if pcr > 1.2 else ("red" if pcr < 0.8 else "yellow")
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">PCR</div>
        <div class="metric-value {pcr_color}">{pcr}</div>
        <div class="metric-icon">👥</div>
    </div>""", unsafe_allow_html=True)

with c4:
    ov_color = "green" if overall_sig == "BUY" else ("red" if overall_sig == "SELL" else "yellow")
    ov_icon  = "▲" if overall_sig == "BUY" else ("▼" if overall_sig == "SELL" else "◆")
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">OVERALL SIGNAL</div>
        <div class="metric-value {ov_color}" style="font-size:1.5rem">{ov_icon} {overall_sig}</div>
        <div class="metric-icon">🎯</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

# ===================================
# ROW 2: Summary | Support | Resistance | PCR
# ===================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    summary_rows = [
        ("Spot",                 f"{round(spot, 2):,.2f}",              "green-val"),
        ("ATM",                  f"{atm_strike:,.0f}",                   "cyan-val"),
        ("PCR",                  str(pcr),                               "yellow-val"),
        ("Market View",          market_view,                            view_color),
        ("Strongest Support",    f"{support.iloc[0]['Strike']:,.0f}",    "green-val"),
        ("Strongest Resistance", f"{resistance.iloc[0]['Strike']:,.0f}", "red-val"),
    ]
    rows_html = "".join([
        f'<tr>'
        f'<td style="color:#8b949e;text-align:left;padding:0.32rem 0.4rem">{m}</td>'
        f'<td class="{c}" style="text-align:right;padding:0.32rem 0.4rem">{v}</td>'
        f'</tr>'
        for m, v, c in summary_rows
    ])
    st.markdown(f"""
    <div class="section-card">
        <div class="section-title title-blue">MARKET SUMMARY</div>
        <table class="dash-table">{rows_html}</table>
    </div>""", unsafe_allow_html=True)

with col2:
    sup_rows = "".join([
        f'<tr>'
        f'<td class="strike-col">{row["Strike"]:,.0f}</td>'
        f'<td class="green-val">{fmt_num(row["PE_OI"])}</td>'
        f'</tr>'
        for _, row in support.iterrows()
    ])
    st.markdown(f"""
    <div class="section-card">
        <div class="section-title title-green">TOP SUPPORT (Put OI)</div>
        <table class="dash-table">
            <tr><th>Strike</th><th>Put OI</th></tr>
            {sup_rows}
        </table>
    </div>""", unsafe_allow_html=True)

with col3:
    res_rows = "".join([
        f'<tr>'
        f'<td class="strike-col">{row["Strike"]:,.0f}</td>'
        f'<td class="red-val">{fmt_num(row["CE_OI"])}</td>'
        f'</tr>'
        for _, row in resistance.iterrows()
    ])
    st.markdown(f"""
    <div class="section-card">
        <div class="section-title title-red">TOP RESISTANCE (Call OI)</div>
        <table class="dash-table">
            <tr><th>Strike</th><th>Call OI</th></tr>
            {res_rows}
        </table>
    </div>""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="section-card">
        <div class="section-title title-yellow">PCR ANALYSIS</div>
        <table class="dash-table">
            <tr>
                <td style="color:#8b949e;text-align:left">Total Put OI</td>
                <td class="green-val" style="text-align:right">{fmt_num(total_put_oi)}</td>
            </tr>
            <tr>
                <td style="color:#8b949e;text-align:left">Total Call OI</td>
                <td class="red-val" style="text-align:right">{fmt_num(total_call_oi)}</td>
            </tr>
            <tr>
               .chain-card {
    background: #161b22; border: 1px solid #30363d;
    border-radius: 10px; padding: 1rem 1.2rem; margin-top: 0.8rem;
    overflow-x: auto;
}
.chain-table {
    width: 100%; border-collapse: collapse;
    font-size: 0.78rem; min-width: 700px;
}
.chain-table th {
    padding: 0.4rem 0.8rem; font-size: 0.7rem; font-weight: 700;
    letter-spacing: 0.07em; text-transform: uppercase;
    border-bottom: 2px solid #30363d;
}
.chain-table th.calls-col { color: #3fb950; text-align: center; background: #0d2317; }
.chain-table th.puts-col  { color: #f85149; text-align: center; background: #1f0d0d; }
.chain-table th.strike-h  { color: #d29922; text-align: center; }
.chain-table td {
    text-align: right; padding: 0.32rem 0.8rem;
    font-family: 'JetBrains Mono', monospace;
    border-bottom: 1px solid #21262d;
}
.chain-table td.strike-col,
.chain-table td.atm-strike { text-align: center; }
.chain-table tr:last-child td { border-bottom: none; }
.chain-table tbody tr:hover { background: #1f2937; }

.chain-table .atm-row td { background: #2d2a1a !important; font-weight: 700; }
.chain-table .atm-strike { color: #d29922; font-weight: 700; }
.chain-table .atm-badge {
    background: #d29922; color: #0d1117; border-radius: 4px;
    padding: 1px 5px; font-size: 0.65rem; margin-left: 4px;
    font-weight: 700; vertical-align: middle;
}
.calls-header-row { background: #0d2317; }

.green-val   { color: #3fb950; }
.red-val     { color: #f85149; }
.neutral-val { color: #8b949e; }
.strike-col  { color: #c9d1d9; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ===================================
# DATE LOGIC (nearest Tuesday)
# ===================================
today = date.today()
if today.weekday() != 1:
    days_until_tuesday = (1 - today.weekday()) % 7
    if days_until_tuesday == 0:
        days_until_tuesday = 7
    today = today + timedelta(days=days_until_tuesday)

expiry_str    = today.strftime("%Y-%m-%d")
last_updated  = date.today().strftime("%d-%m-%Y")

# ===================================
# API CALL
# ===================================
ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiI2OEFKUVUiLCJqdGkiOiI2YTQxZWI5NmYyNGJiZjFjMjA0ZWFkODIiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6dHJ1ZSwiaXNFeHRlbmRlZCI6dHJ1ZSwiaWF0IjoxNzgyNzA1MDQ2LCJpc3MiOiJ1ZGFwaS1nYXRld2F5LXNlcnZpY2UiLCJleHAiOjE4MTQzMDY0MDB9.LuQ-H-ix7cRKRvn_8DEE2r5_VhOoLK2Szz4VHn3qAxE"   # <-- Apna token yahan daalo

headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

url = (
    f"https://api.upstox.com/v2/option/chain"
    f"?instrument_key=NSE_INDEX%7CNifty%2050&expiry_date={expiry_str}"
)
response = requests.get(url, headers=headers)

# ===================================
# HELPERS  (defined ONCE, used everywhere)
# ===================================
def fmt_oi(val):
    val = int(val)
    if val >= 10_000_000:
        return f"{val/10_000_000:.2f}Cr"
    elif val >= 100_000:
        return f"{val/100_000:.2f}L"
    return f"{val:,}"

def fmt_num(val):
    """Indian-style number formatting, handles int/float/None."""
    try:
        val = float(val)
    except (TypeError, ValueError):
        return "-"
    sign = "-" if val < 0 else ""
    s = str(int(abs(val)))
    if len(s) <= 3:
        return sign + s
    result = s[-3:]
    s = s[:-3]
    while len(s) > 2:
        result = s[-2:] + "," + result
        s = s[:-2]
    if s:
        result = s + "," + result
    return sign + result

def color_change(val, prefix="+"):
    c    = "green-val" if val >= 0 else "red-val"
    sign = "+" if val >= 0 else ""
    return f'<td class="{c}">{sign}{fmt_num(val)}</td>'

# ===================================
# TITLE
# ===================================
st.markdown(f"""
<div class="dash-title">
    NIFTY OPTION CHAIN DASHBOARD BY NAMAN &nbsp;<span class="refresh-icon">↻</span>
</div>
<div class="dash-subtitle">
    Last Updated: <span style="color:#3fb950">{last_updated}</span>
    &nbsp;|&nbsp;
    Expiry: <span style="color:#58a6ff">{expiry_str}</span>
</div>
""", unsafe_allow_html=True)

if response.status_code != 200:
    st.error(f"❌ API Error {response.status_code}: Token check karein ya market band ho sakti hai.")
    st.stop()

# ===================================
# DATA PROCESSING
# ===================================
data = response.json()["data"]
rows = []
for item in data:
    strike  = item["strike_price"]
    ce_data = item.get("call_options", {})
    pe_data = item.get("put_options",  {})
    rows.append({
        "Strike":       strike,
        "CE_OI":        ce_data.get("market_data", {}).get("oi",            0) or 0,
        "PE_OI":        pe_data.get("market_data", {}).get("oi",            0) or 0,
        "CE_OI_CHANGE": ce_data.get("market_data", {}).get("oi_day_change", 0) or 0,
        "PE_OI_CHANGE": pe_data.get("market_data", {}).get("oi_day_change", 0) or 0,
        "CE_LTP":       ce_data.get("market_data", {}).get("ltp",           0) or 0,
        "PE_LTP":       pe_data.get("market_data", {}).get("ltp",           0) or 0,
    })

df = pd.DataFrame(rows).reset_index(drop=True)
spot = data[0]["underlying_spot_price"]
atm_strike = min(df["Strike"], key=lambda x: abs(x - spot))

# ===================================
# OI CHANGE — session_state method
# ===================================
current_oi = {
    str(int(row["Strike"])): {
        "CE_OI": int(row["CE_OI"]),
        "PE_OI": int(row["PE_OI"])
    }
    for _, row in df.iterrows()
}

if "prev_oi" not in st.session_state:
    st.session_state.prev_oi = {}

prev_oi = st.session_state.prev_oi

if prev_oi:
    def get_change(strike, side):
        key = str(int(strike))
        curr = current_oi.get(key, {}).get(side, 0)
        prev = prev_oi.get(key, {}).get(side, 0)
        return curr - prev

    df["CE_OI_CHANGE"] = df["Strike"].apply(lambda s: get_change(s, "CE_OI"))
    df["PE_OI_CHANGE"] = df["Strike"].apply(lambda s: get_change(s, "PE_OI"))
else:
    df["CE_OI_CHANGE"] = 0
    df["PE_OI_CHANGE"] = 0

st.session_state.prev_oi = current_oi
near_df = df[(df["Strike"] >= spot - 500) & (df["Strike"] <= spot + 500)]

support    = near_df.sort_values("PE_OI", ascending=False).head(3)[["Strike", "PE_OI"]]
resistance = near_df.sort_values("CE_OI", ascending=False).head(3)[["Strike", "CE_OI"]]

total_put_oi  = df["PE_OI"].sum()
total_call_oi = df["CE_OI"].sum()
pcr           = round(total_put_oi / total_call_oi, 2) if total_call_oi else 0

call_writing = near_df.sort_values("CE_OI_CHANGE", ascending=False).head(3)[["Strike", "CE_OI_CHANGE"]]
put_writing  = near_df.sort_values("PE_OI_CHANGE", ascending=False).head(3)[["Strike", "PE_OI_CHANGE"]]

if pcr > 1.2:
    market_view = "BULLISH";  view_color = "green-val"
elif pcr < 0.8:
    market_view = "BEARISH";  view_color = "red-val"
else:
    market_view = "NEUTRAL";  view_color = "yellow-val"

# ===================================
# TOP METRIC CARDS
# ===================================
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">NIFTY</div>
        <div class="metric-value green">{round(spot, 2):,.2f}</div>
        <div class="metric-icon">📈</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">ATM</div>
        <div class="metric-value cyan">{atm_strike:,.0f}</div>
        <div class="metric-icon">⚙️</div>
    </div>""", unsafe_allow_html=True)

with c3:
    pcr_color = "green" if pcr > 1.2 else ("red" if pcr < 0.8 else "yellow")
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">PCR</div>
        <div class="metric-value {pcr_color}">{pcr}</div>
        <div class="metric-icon">👥</div>
    </div>""", unsafe_allow_html=True)

with c4:
    vcolor = "green" if market_view == "BULLISH" else ("red" if market_view == "BEARISH" else "yellow")
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">VIEW</div>
        <div class="metric-value {vcolor}" style="font-size:1.5rem">{market_view}</div>
        <div class="metric-icon">👁️</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

# ===================================
# MIDDLE ROW
# ===================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    summary_rows = [
        ("Spot",                f"{round(spot, 2):,.2f}",          "green-val"),
        ("ATM",                 f"{atm_strike:,.0f}",               "cyan-val"),
        ("PCR",                 str(pcr),                           "yellow-val"),
        ("Market View",         market_view,                        view_color),
        ("Strongest Support",   f"{support.iloc[0]['Strike']:,.0f}","green-val"),
        ("Strongest Resistance",f"{resistance.iloc[0]['Strike']:,.0f}","red-val"),
    ]
    rows_html = "".join([
        f'<tr>'
        f'<td style="color:#8b949e;text-align:left;padding:0.32rem 0.4rem">{m}</td>'
        f'<td class="{c}" style="text-align:right;padding:0.32rem 0.4rem">{v}</td>'
        f'</tr>'
        for m, v, c in summary_rows
    ])
    st.markdown(f"""
    <div class="section-card">
        <div class="section-title title-blue">MARKET SUMMARY</div>
        <table class="dash-table">{rows_html}</table>
    </div>""", unsafe_allow_html=True)

with col2:
    sup_rows = "".join([
        f'<tr>'
        f'<td class="strike-col">{row["Strike"]:,.0f}</td>'
        f'<td class="green-val">{fmt_num(row["PE_OI"])}</td>'
        f'</tr>'
        for _, row in support.iterrows()
    ])
    st.markdown(f"""
    <div class="section-card">
        <div class="section-title title-green">TOP SUPPORT LEVELS (Put OI)</div>
        <table class="dash-table">
            <tr><th>Strike</th><th>Put OI</th></tr>
            {sup_rows}
        </table>
    </div>""", unsafe_allow_html=True)

with col3:
    res_rows = "".join([
        f'<tr>'
        f'<td class="strike-col">{row["Strike"]:,.0f}</td>'
        f'<td class="red-val">{fmt_num(row["CE_OI"])}</td>'
        f'</tr>'
        for _, row in resistance.iterrows()
    ])
    st.markdown(f"""
    <div class="section-card">
        <div class="section-title title-red">TOP RESISTANCE LEVELS (Call OI)</div>
        <table class="dash-table">
            <tr><th>Strike</th><th>Call OI</th></tr>
            {res_rows}
        </table>
    </div>""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="section-card">
        <div class="section-title title-yellow">PCR ANALYSIS</div>
        <table class="dash-table">
            <tr>
                <td style="color:#8b949e;text-align:left">Total Put OI</td>
                <td class="green-val" style="text-align:right">{fmt_num(total_put_oi)}</td>
            </tr>
            <tr>
                <td style="color:#8b949e;text-align:left">Total Call OI</td>
                <td class="red-val" style="text-align:right">{fmt_num(total_call_oi)}</td>
            </tr>
            <tr>
                <td style="color:#8b949e;text-align:left">PCR</td>
                <td class="yellow-val" style="text-align:right;font-size:1.1rem;font-weight:700">{pcr}</td>
            </tr>
        </table>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)

# ===================================
# FRESH WRITING ROW
# ===================================
cw_col, pw_col = st.columns(2)

with cw_col:
    cw_rows = "".join([
        f'<tr><td class="strike-col">{row["Strike"]:,.0f}</td>{color_change(row["CE_OI_CHANGE"])}</tr>'
        for _, row in call_writing.iterrows()
    ])
    st.markdown(f"""
    <div class="section-card">
        <div class="section-title title-green">FRESH CALL WRITING</div>
        <table class="dash-table">
            <tr><th>Strike</th><th>CE OI Change</th></tr>
            {cw_rows}
        </table>
    </div>""", unsafe_allow_html=True)

with pw_col:
    pw_rows = "".join([
        f'<tr><td class="strike-col">{row["Strike"]:,.0f}</td>{color_change(row["PE_OI_CHANGE"])}</tr>'
        for _, row in put_writing.iterrows()
    ])
    st.markdown(f"""
    <div class="section-card">
        <div class="section-title title-orange">FRESH PUT WRITING</div>
        <table class="dash-table">
            <tr><th>Strike</th><th>PE OI Change</th></tr>
            {pw_rows}
        </table>
    </div>""", unsafe_allow_html=True)

# ===================================
# OPTION CHAIN TABLE
# ===================================

# Reset index so idxmin() returns a positional integer safe for iloc
# ===================================
# OPTION CHAIN TABLE
# ===================================
df = df.reset_index(drop=True)
atm_pos = (df["Strike"] - atm_strike).abs().idxmin()
start   = max(0, atm_pos - 10)
end     = min(len(df), atm_pos + 11)

chain_df = df.iloc[start:end].copy()
chain_df = chain_df.sort_values("Strike").reset_index(drop=True)

# Build rows separately — no nested f-strings
rows_parts = []
for _, row in chain_df.iterrows():
    is_atm = abs(row["Strike"] - atm_strike) < 0.01

    atm_class    = "atm-row"    if is_atm else ""
    strike_class = "atm-strike" if is_atm else "strike-col"
    atm_label    = '<span class="atm-badge">★ ATM</span>' if is_atm else ""

    ce_oi     = float(row.get("CE_OI",        0) or 0)
    pe_oi     = float(row.get("PE_OI",        0) or 0)
    ce_change = float(row.get("CE_OI_CHANGE", 0) or 0)
    pe_change = float(row.get("PE_OI_CHANGE", 0) or 0)
    ce_ltp    = float(row.get("CE_LTP",       0) or 0)
    pe_ltp    = float(row.get("PE_LTP",       0) or 0)

    ce_chg_cls = "green-val"   if ce_change > 0 else ("red-val" if ce_change < 0 else "neutral-val")
    pe_chg_cls = "green-val"   if pe_change > 0 else ("red-val" if pe_change < 0 else "neutral-val")
    ce_sign    = "+" if ce_change > 0 else ""
    pe_sign    = "+" if pe_change > 0 else ""

    strike_disp = str(int(row["Strike"])) if float(row["Strike"]).is_integer() else f"{float(row['Strike']):.2f}"

    tr = (
        f'<tr class="{atm_class}">'
        f'<td class="green-val">{fmt_num(ce_oi)}</td>'
        f'<td class="{ce_chg_cls}">{ce_sign}{fmt_num(ce_change)}</td>'
        f'<td style="color:#e6edf3">{ce_ltp:.2f}</td>'
        f'<td class="{strike_class}">{strike_disp} {atm_label}</td>'
        f'<td style="color:#e6edf3">{pe_ltp:.2f}</td>'
        f'<td class="{pe_chg_cls}">{pe_sign}{fmt_num(pe_change)}</td>'
        f'<td class="red-val">{fmt_num(pe_oi)}</td>'
        f'</tr>'
    )
    rows_parts.append(tr)

chain_rows_html = "\n".join(rows_parts)

# Build full HTML block as a plain string — NO outer f-string nesting
html_block = """
<div class="chain-card">
    <div class="section-title title-yellow" style="font-size:0.85rem">
        ATM OPTION CHAIN (-10 to +10 STRIKES)
    </div>
    <table class="chain-table">
        <thead>
            <tr>
                <th colspan="3" class="calls-col">CALLS</th>
                <th class="strike-h">STRIKE</th>
                <th colspan="3" class="puts-col">PUTS</th>
            </tr>
            <tr>
                <th class="calls-col">CE OI</th>
                <th class="calls-col">CE OI Change</th>
                <th class="calls-col">CE LTP</th>
                <th class="strike-h">—</th>
                <th class="puts-col">PE LTP</th>
                <th class="puts-col">PE OI Change</th>
                <th class="puts-col">PE OI</th>
            </tr>
        </thead>
        <tbody>
""" + chain_rows_html + """
        </tbody>
    </table>
</div>
"""

st.markdown(html_block, unsafe_allow_html=True)
