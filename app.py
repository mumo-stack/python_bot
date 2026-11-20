"""Streamlit forex dashboard: market data + EMA signals + paper trading only."""
import streamlit as st

import config
from market_data import fetch_forex_data
from strategy import get_signal
from paper_engine import (
    create_account,
    account_equity,
    open_position,
    close_position,
    update_position_mark,
    check_stop_or_target,
)

st.set_page_config(
    page_title="Forex Paper Trading Dashboard",
    page_icon="📈",
    layout="wide",
)

st.title("📈 Forex Trading Dashboard")
st.caption("EMA 9/21 strategy · Market data from Yahoo Finance · Paper trading only")

if "account" not in st.session_state:
    st.session_state.account = create_account(config.STARTING_BALANCE)
if "notice" not in st.session_state:
    st.session_state.notice = ""

with st.sidebar:
    st.header("Dashboard settings")
    pair = st.selectbox("Currency pair", list(config.PAIRS.keys()), index=0)
    timeframe_label = st.selectbox("Chart timeframe", list(config.TIMEFRAMES.keys()), index=2)
    interval, period = config.TIMEFRAMES[timeframe_label]
    st.divider()
    st.subheader("Risk settings")
    st.write(f"Risk per trade: **{config.RISK_PER_TRADE:.1%}**")
    st.write(f"Maximum position: **{config.MAX_POSITION_FRACTION:.0%}** of equity")
    st.write(f"Stop-loss: **{config.STOP_LOSS_PCT:.2%}**")
    st.write(f"Take-profit: **{config.TAKE_PROFIT_PCT:.2%}**")
    st.caption("These are learning defaults, not a recommendation.")
    if st.button("Refresh market data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

@st.cache_data(ttl=60, show_spinner=False)
def load_data(ticker, selected_interval, selected_period):
    return fetch_forex_data(ticker, selected_interval, selected_period)

ticker = config.PAIRS[pair]
try:
    with st.spinner(f"Loading {pair} market data..."):
        data = load_data(ticker, interval, period)
except Exception as exc:
    st.error(f"Could not load forex data: {exc}")
    st.info("Check your internet connection, wait a moment, and press Refresh market data.")
    st.stop()

if len(data) < 22:
    st.warning("There is not enough price history to calculate the EMA crossover. Try another timeframe.")
    st.stop()

price = float(data["Close"].iloc[-1])
previous_price = float(data["Close"].iloc[-2])
change_pct = ((price / previous_price) - 1) * 100 if previous_price else 0
signal = get_signal(data)
last_time = data.index[-1]

account = st.session_state.account
update_position_mark(account, pair, price)
candle_id = last_time.isoformat()
protective_result = check_stop_or_target(
    account, pair, data.iloc[-1], config.SIMULATED_FEE_RATE, candle_id
)
if protective_result:
    st.session_state.notice = protective_result[1]

if st.session_state.notice:
    st.info(st.session_state.notice)
    st.session_state.notice = ""

position = account["position"]
equity = account_equity(account, pair, price)
unrealized = 0.0
if position:
    unrealized = (
        (price - position["entry_price"]) * position["amount"]
        - position["entry_fee"]
        - (position["amount"] * price * config.SIMULATED_FEE_RATE)
    )

# Top market metrics
m1, m2, m3, m4 = st.columns(4)
m1.metric(f"{pair} latest price", f"{price:.5f}", f"{change_pct:+.3f}%")
m2.metric("Trading signal", signal)
m3.metric("Account equity", f"${equity:,.2f}")
m4.metric("Realized P/L", f"${account['realized_pnl']:,.2f}")

tab_market, tab_account, tab_history = st.tabs(["📊 Market analysis", "💼 Paper account", "📜 Trade history"])

with tab_market:
    st.subheader(f"{pair} price chart")
    chart = data[["Close", "EMA 9", "EMA 21"]].rename(columns={"Close": "Price"})
    st.line_chart(chart, height=380)
    st.caption(f"Last data candle: {last_time}. Data availability and timestamps depend on Yahoo Finance.")
    a, b, c = st.columns(3)
    a.metric("EMA 9", f"{float(data['EMA 9'].iloc[-1]):.5f}")
    b.metric("EMA 21", f"{float(data['EMA 21'].iloc[-1]):.5f}")
    c.metric("Latest candle close", f"{price:.5f}")

    if signal == "BUY":
        st.success("BUY signal: EMA 9 has crossed above EMA 21.")
    elif signal == "SELL":
        st.warning("SELL signal: EMA 9 has crossed below EMA 21.")
    else:
        st.info("HOLD signal: no new EMA crossover is detected.")

    st.subheader("Paper trade controls")
    if position and position["pair"] != pair:
        st.warning(
            f"You have an open {position['pair']} position. Select {position['pair']} "
            "to manage or close it before trading another pair."
        )
    else:
        col_buy, col_sell = st.columns(2)
        with col_buy:
            buy_disabled = signal != "BUY" or position is not None
            if st.button("Execute BUY signal", type="primary", disabled=buy_disabled, use_container_width=True):
                ok, message = open_position(
                    account, pair, price,
                    config.RISK_PER_TRADE,
                    config.MAX_POSITION_FRACTION,
                    config.STOP_LOSS_PCT,
                    config.TAKE_PROFIT_PCT,
                    config.SIMULATED_FEE_RATE,
                    candle_id,
                )
                st.session_state.notice = message
                st.rerun()
        with col_sell:
            sell_disabled = signal != "SELL" or position is None
            if st.button("Execute SELL signal", disabled=sell_disabled, use_container_width=True):
                ok, message = close_position(account, price, "EMA crossover", config.SIMULATED_FEE_RATE)
                st.session_state.notice = message
                st.rerun()

with tab_account:
    st.subheader("Paper account overview")
    c1, c2, c3 = st.columns(3)
    c1.metric("Starting balance", f"${account['starting_balance']:,.2f}")
    c2.metric("Available cash", f"${account['cash']:,.2f}")
    c3.metric("Unrealized P/L", f"${unrealized:,.2f}")
    st.metric("Total account equity", f"${equity:,.2f}")

    if position:
        st.subheader("Open position")
        if position["pair"] == pair:
            st.write(f"**Pair:** {position['pair']}  |  **Units:** {position['amount']:,.2f}")
            st.write(f"**Entry:** {position['entry_price']:.5f}  |  **Current:** {price:.5f}")
            p1, p2 = st.columns(2)
            p1.metric("Stop-loss", f"{position['stop_price']:.5f}")
            p2.metric("Take-profit", f"{position['target_price']:.5f}")
            if st.button("Close open paper position now", type="primary"):
                ok, message = close_position(account, price, "Manual close", config.SIMULATED_FEE_RATE)
                st.session_state.notice = message
                st.rerun()
        else:
            st.write(f"Open position: **{position['pair']}**")
            st.write("Switch the currency pair selector to manage this position.")
    else:
        st.info("There are currently no open paper positions.")

    if st.button("Reset paper account", type="secondary"):
        st.session_state.account = create_account(config.STARTING_BALANCE)
        st.session_state.notice = "Paper account reset to its starting balance."
        st.rerun()

with tab_history:
    st.subheader("Completed paper trades")
    trades = account["trades"]
    if trades:
        st.dataframe(trades, use_container_width=True, hide_index=True)
    else:
        st.info("No completed trades yet. Paper trades will appear here after you close a position.")

st.divider()
st.caption(
    "Educational simulator only. No broker connection, no real orders and no guarantee of "
    "real-time quotes. Yahoo Finance data may be delayed, incomplete or unavailable. "
    "Do not use this dashboard as the sole basis for financial decisions."
)
