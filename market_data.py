"""Download forex history from Yahoo Finance using yfinance."""
import pandas as pd
import yfinance as yf

def fetch_forex_data(ticker: str, interval: str, period: str) -> pd.DataFrame:
    data = yf.download(
        ticker,
        period=period,
        interval=interval,
        auto_adjust=False,
        progress=False,
        threads=False,
    )
    if data is None or data.empty:
        raise RuntimeError(
            "No market data was returned. Check your internet connection, "
            "then try refreshing or selecting another timeframe."
        )

    # Recent yfinance versions can return MultiIndex columns even for one ticker.
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    required = {"Open", "High", "Low", "Close"}
    missing = required.difference(data.columns)
    if missing:
        raise RuntimeError(f"Market data is missing columns: {', '.join(sorted(missing))}")

    data = data.dropna(subset=["Open", "High", "Low", "Close"]).copy()
    data.index = pd.to_datetime(data.index)
    data["EMA 9"] = data["Close"].ewm(span=9, adjust=False).mean()
    data["EMA 21"] = data["Close"].ewm(span=21, adjust=False).mean()
    return data
