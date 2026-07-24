import os
import sqlite3
from datetime import datetime, timedelta, timezone

import pandas as pd

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "oi_history.db")
IST = timezone(timedelta(hours=5, minutes=30))
SNAPSHOT_INTERVAL_MIN = 5
MARKET_OPEN = (9, 15)
MARKET_CLOSE = (15, 30)


def now_ist():
    return datetime.now(IST)


def is_market_hours(dt=None):
    """NSE cash/derivatives hours: 9:15-15:30 IST, Monday-Friday."""
    dt = dt or now_ist()
    if dt.weekday() >= 5:
        return False
    open_t = dt.replace(hour=MARKET_OPEN[0], minute=MARKET_OPEN[1], second=0, microsecond=0)
    close_t = dt.replace(hour=MARKET_CLOSE[0], minute=MARKET_CLOSE[1], second=0, microsecond=0)
    return open_t <= dt <= close_t


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS oi_snapshots (
            ts TEXT NOT NULL,
            strike REAL NOT NULL,
            ce_oi INTEGER,
            pe_oi INTEGER,
            ce_ltp REAL,
            pe_ltp REAL,
            spot REAL
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ts ON oi_snapshots (ts)")
    return conn


def _last_snapshot_time(conn):
    row = conn.execute("SELECT MAX(ts) FROM oi_snapshots").fetchone()
    if row and row[0]:
        return datetime.fromisoformat(row[0])
    return None


def save_snapshot(df, spot, dt=None):
    """Persist one OI snapshot if within market hours and >= SNAPSHOT_INTERVAL_MIN since the last save."""
    dt = dt or now_ist()
    if not is_market_hours(dt):
        return False

    conn = _get_conn()
    try:
        last_ts = _last_snapshot_time(conn)
        if last_ts is not None and (dt - last_ts) < timedelta(minutes=SNAPSHOT_INTERVAL_MIN):
            return False

        ts_str = dt.isoformat()
        rows = [
            (
                ts_str,
                round(float(r["Strike"]), 2),
                int(r["CE_OI"]),
                int(r["PE_OI"]),
                float(r["CE_LTP"]),
                float(r["PE_LTP"]),
                float(spot),
            )
            for _, r in df.iterrows()
        ]
        conn.executemany(
            "INSERT INTO oi_snapshots (ts, strike, ce_oi, pe_oi, ce_ltp, pe_ltp, spot) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            rows,
        )
        conn.commit()
        return True
    finally:
        conn.close()


def get_snapshot_near(target_dt, tolerance_minutes=10):
    """Return (actual_timestamp, DataFrame) for the latest snapshot at/before target_dt within tolerance."""
    conn = _get_conn()
    try:
        window_start = (target_dt - timedelta(minutes=tolerance_minutes)).isoformat()
        window_end = target_dt.isoformat()
        row = conn.execute(
            "SELECT MAX(ts) FROM oi_snapshots WHERE ts <= ? AND ts >= ?",
            (window_end, window_start),
        ).fetchone()
        actual_ts = row[0] if row else None
        if not actual_ts:
            return None, None

        cur = conn.execute(
            "SELECT strike, ce_oi, pe_oi, ce_ltp, pe_ltp, spot FROM oi_snapshots WHERE ts = ?",
            (actual_ts,),
        )
        data = cur.fetchall()
        snap_df = pd.DataFrame(
            data, columns=["Strike", "CE_OI", "PE_OI", "CE_LTP", "PE_LTP", "Spot"]
        )
        return datetime.fromisoformat(actual_ts), snap_df
    finally:
        conn.close()
