"""Default settings for the forex paper-trading dashboard."""

STARTING_BALANCE = 10_000.00
RISK_PER_TRADE = 0.01          # 1% of account equity
MAX_POSITION_FRACTION = 0.20  # maximum 20% of equity in one position
STOP_LOSS_PCT = 0.005          # 0.5%
TAKE_PROFIT_PCT = 0.010        # 1.0%
SIMULATED_FEE_RATE = 0.0001    # 0.01% per side; simplified cost assumption

PAIRS = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "AUD/USD": "AUDUSD=X",
    "NZD/USD": "NZDUSD=X",
}

TIMEFRAMES = {
    "15 minutes": ("15m", "7d"),
    "30 minutes": ("30m", "30d"),
    "1 hour": ("1h", "30d"),
    "1 day": ("1d", "1y"),
}
