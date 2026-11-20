"""Session-based forex paper trading functions. No real orders are sent."""
from datetime import datetime, timezone

def create_account(starting_balance):
    return {
        "starting_balance": float(starting_balance),
        "cash": float(starting_balance),
        "position": None,
        "trades": [],
        "realized_pnl": 0.0,
    }

def account_equity(account, current_pair=None, current_price=None):
    position = account["position"]
    if not position:
        return account["cash"]
    mark = position["last_price"]
    if current_pair == position["pair"] and current_price is not None:
        mark = float(current_price)
    return account["cash"] + position["amount"] * mark

def open_position(account, pair, price, risk_pct, max_position_fraction,
                  stop_loss_pct, take_profit_pct, fee_rate, candle_id=None):
    if account["position"] is not None:
        return False, "There is already an open paper position. Close it first."

    price = float(price)
    equity = account_equity(account)
    risk_budget = equity * risk_pct
    amount_by_risk = risk_budget / (price * stop_loss_pct)
    amount_by_cap = (equity * max_position_fraction) / price
    amount_by_cash = account["cash"] / (price * (1 + fee_rate))
    amount = min(amount_by_risk, amount_by_cap, amount_by_cash)

    if amount <= 0:
        return False, "Position size is zero. Check the account balance and settings."

    notional = amount * price
    fee = notional * fee_rate
    account["cash"] -= notional + fee
    account["position"] = {
        "pair": pair,
        "amount": amount,
        "entry_price": price,
        "last_price": price,
        "stop_price": price * (1 - stop_loss_pct),
        "target_price": price * (1 + take_profit_pct),
        "entry_fee": fee,
        "opened_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "opened_candle": str(candle_id) if candle_id is not None else None,
    }
    return True, f"Paper BUY opened: {amount:,.2f} units of {pair} at {price:.5f}."

def close_position(account, price, reason, fee_rate):
    position = account["position"]
    if not position:
        return False, "There is no open paper position."

    price = float(price)
    proceeds = position["amount"] * price
    exit_fee = proceeds * fee_rate
    pnl = (
        (price - position["entry_price"]) * position["amount"]
        - position["entry_fee"]
        - exit_fee
    )
    account["cash"] += proceeds - exit_fee
    account["realized_pnl"] += pnl
    account["trades"].insert(0, {
        "time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "pair": position["pair"],
        "side": "BUY → SELL",
        "entry": position["entry_price"],
        "exit": price,
        "amount": position["amount"],
        "pnl": pnl,
        "reason": reason,
    })
    account["position"] = None
    return True, f"Paper position closed ({reason}). P/L after simulated fees: ${pnl:,.2f}."

def update_position_mark(account, pair, price):
    position = account["position"]
    if position and position["pair"] == pair:
        position["last_price"] = float(price)

def check_stop_or_target(account, pair, candle, fee_rate, candle_id=None):
    position = account["position"]
    if not position or position["pair"] != pair:
        return None
    # Do not test the entry candle: its high/low may have happened before entry.
    if candle_id is not None and position.get("opened_candle") is not None:
        if str(candle_id) <= position["opened_candle"]:
            return None

    low = float(candle["Low"])
    high = float(candle["High"])

    # If both levels are inside one candle, assume the stop was hit first.
    if low <= position["stop_price"]:
        return close_position(account, position["stop_price"], "Stop-loss", fee_rate)
    if high >= position["target_price"]:
        return close_position(account, position["target_price"], "Take-profit", fee_rate)
    return None
