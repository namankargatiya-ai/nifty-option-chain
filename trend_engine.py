import pandas as pd


# =====================================================
# EMA
# =====================================================

def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()


# =====================================================
# RSI
# =====================================================

def rsi(close, period=14):
    delta = close.diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    return 100 - (100 / (1 + rs))


# =====================================================
# VWAP
# =====================================================

def vwap(df):

    tp = (df["High"] + df["Low"] + df["Close"]) / 3

    return (tp * df["Volume"]).cumsum() / df["Volume"].cumsum()


# =====================================================
# Trend Engine
# =====================================================

def calculate_trend(df, pcr=1.0):

    df = df.copy()

    df["EMA20"] = ema(df["Close"], 20)
    df["EMA50"] = ema(df["Close"], 50)
    df["EMA100"] = ema(df["Close"], 100)
    df["EMA200"] = ema(df["Close"], 200)

    df["RSI"] = rsi(df["Close"])

    df["VWAP"] = vwap(df)

    last = df.iloc[-1]

    score = 0

    reasons = []

    # -------------------------------
    # Price vs VWAP
    # -------------------------------

    if last["Close"] > last["VWAP"]:
        score += 10
        reasons.append("Price Above VWAP")
    else:
        reasons.append("Price Below VWAP")

    # -------------------------------
    # EMA Alignment
    # -------------------------------

    if last["EMA20"] > last["EMA50"]:
        score += 10
        reasons.append("EMA20 > EMA50")

    if last["EMA50"] > last["EMA100"]:
        score += 10
        reasons.append("EMA50 > EMA100")

    if last["EMA100"] > last["EMA200"]:
        score += 10
        reasons.append("EMA100 > EMA200")

    # -------------------------------
    # RSI
    # -------------------------------

    if last["RSI"] > 60:
        score += 10
        reasons.append(f"RSI Strong ({last['RSI']:.1f})")

    elif last["RSI"] > 50:
        score += 5
        reasons.append(f"RSI Positive ({last['RSI']:.1f})")

    else:
        reasons.append(f"RSI Weak ({last['RSI']:.1f})")

    # -------------------------------
    # PCR
    # -------------------------------

    if pcr > 1.20:
        score += 10
        reasons.append("Bullish PCR")

    elif pcr < 0.80:
        reasons.append("Bearish PCR")

    else:
        score += 5
        reasons.append("Neutral PCR")

    # -------------------------------
    # Classification
    # -------------------------------

    if score >= 55:
        trend = "🟢 STRONG BULLISH"

    elif score >= 40:
        trend = "🟢 BULLISH"

    elif score >= 30:
        trend = "🟡 NEUTRAL"

    elif score >= 20:
        trend = "🔴 BEARISH"

    else:
        trend = "🔴 STRONG BEARISH"

    confidence = min(95, score + 30)

    return {
        "trend": trend,
        "score": score,
        "confidence": confidence,
        "ema20": round(last["EMA20"], 2),
        "ema50": round(last["EMA50"], 2),
        "ema100": round(last["EMA100"], 2),
        "ema200": round(last["EMA200"], 2),
        "vwap": round(last["VWAP"], 2),
        "rsi": round(last["RSI"], 2),
        "reasons": reasons,
    }
