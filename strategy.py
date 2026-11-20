"""EMA 9/21 crossover strategy."""

def get_signal(data):
    """Return BUY, SELL or HOLD based on the last two available candles."""
    if data is None or len(data) < 22:
        return "HOLD"

    previous = data.iloc[-2]
    current = data.iloc[-1]

    if previous["EMA 9"] <= previous["EMA 21"] and current["EMA 9"] > current["EMA 21"]:
        return "BUY"
    if previous["EMA 9"] >= previous["EMA 21"] and current["EMA 9"] < current["EMA 21"]:
        return "SELL"
    return "HOLD"
