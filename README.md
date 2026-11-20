# Forex Trading Dashboard (Paper Trading)

A beginner-friendly forex dashboard built with Python, Streamlit, pandas and yfinance.

## Features
- Forex pairs: EUR/USD, GBP/USD, AUD/USD and NZD/USD
- Price history with EMA 9 and EMA 21
- BUY / SELL / HOLD crossover signals
- Paper account starting at $10,000
- Simulated position sizing, stop-loss and take-profit
- Open position, cash, equity, realized/unrealized P/L and trade history

## Important safety note
This project is a learning simulator. It does not connect to a forex broker or place real trades. Yahoo Finance quotes can be delayed, incomplete or unavailable. The default costs and risk settings are simplified examples, not recommendations.

## Install in Windows VS Code

1. Extract this folder.
2. Open the folder in VS Code: **File > Open Folder**.
3. Open **Terminal > New Terminal**.
4. Create a virtual environment:

   ```powershell
   py -m venv .venv
   ```

5. Activate it:

   ```powershell
   .venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, run this once in that terminal:

   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .venv\Scripts\Activate.ps1
   ```

6. Install packages:

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

7. Start the dashboard:

   ```powershell
   python -m streamlit run app.py
   ```

8. Streamlit opens the dashboard in your browser, usually at `http://localhost:8501`.

## Using the dashboard
- Choose a currency pair and timeframe in the sidebar.
- Read the latest available price and EMA signal.
- Use **Execute BUY signal** or **Execute SELL signal** to simulate a trade. Buttons are disabled unless the signal and account state permit the action.
- Stop-loss and take-profit are checked against the latest downloaded candle whenever the app reruns.
- Refresh data using the sidebar button.
- Reset the simulated account from the Paper account tab.

## Defaults
- Starting balance: $10,000
- Risk budget per trade: 1% of equity
- Maximum position notional: 20% of equity
- Stop-loss: 0.5%
- Take-profit: 1.0%
- Simulated fee: 0.01% per side

## Technical notes
- Yahoo Finance ticker symbols are used for the USD-quoted pairs.
- Intraday data availability is limited by the data provider and may vary.
- The dashboard uses the last returned candle for its EMA signal. The latest candle may still be forming, so treat signals as provisional.
- Paper account state is stored in Streamlit's session state and is reset when the session is restarted or the reset button is used.
