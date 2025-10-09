import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt 

# === CONFIGURATION ===
TICKER = "AAPL"
START_DATE = "2024-09-01"
END_DATE = dt.date.today().strftime("%Y-%m-%d")
SHORT_WINDOW = 20
LONG_WINDOW = 50
INITIAL_BALANCE = 75
RISK_FREE_RATE = 0.04  # Annual risk-free rate

# === DOWNLOAD DATA ===
print(f"Downloading {TICKER} data from Yahoo Finance...")
data = yf.download(TICKER, start=START_DATE, end=END_DATE)
data.dropna(inplace=True)

# === CALCULATE MOVING AVERAGES ===
data['SMA_Short'] = data['Close'].rolling(window=SHORT_WINDOW).mean()
data['SMA_Long'] = data['Close'].rolling(window=LONG_WINDOW).mean()

# === GENERATE TRADING SIGNALS ===
data['Signal'] = 0
data.loc[data['SMA_Short'] > data['SMA_Long'], 'Signal'] = 1  # Buy signal
data.loc[data['SMA_Short'] < data['SMA_Long'], 'Signal'] = 0  # Sell signal

# === CALCULATE RETURNS ===
data['Returns'] = data['Close'].pct_change()
data['STRATEGY_RETURNS'] = data['Returns'] * data['Signal'].shift(1)

# === PORTFOLIO PERFORMANCE ===
data['PORTFOLIO_VALUE'] = (1 + data['STRATEGY_RETURNS']).cumprod() * INITIAL_BALANCE
final_value = data['PORTFOLIO_VALUE'].iloc[-1]

total_return = (final_value / INITIAL_BALANCE - 1) * 100
years = (data.index[-1] - data.index[0]).days / 365.25
cagr = (final_value / INITIAL_BALANCE) ** (1 / years) - 1

volatility = data['STRATEGY_RETURNS'].std() * np.sqrt(252)
sharpe_ratio = (data['STRATEGY_RETURNS'].mean() * 252 - RISK_FREE_RATE) / volatility

rolling_max = data['PORTFOLIO_VALUE'].cummax()
drawdown = (data['PORTFOLIO_VALUE'] - rolling_max) / rolling_max
max_drawdown = drawdown.min() * 100

# === TRADE LOG ===
trades = []
position_open = False
entry_price = 0
entry_date = None

for i in range(1, len(data)):
    if not position_open and data['Signal'].iloc[i] == 1 and data['Signal'].iloc[i - 1] == 0:
        position_open = True
        entry_price = data['Close'].iloc[i]
        entry_date = data.index[i]
    elif position_open and data['Signal'].iloc[i] == 0 and data['Signal'].iloc[i - 1] == 1:
        exit_price = data['Close'].iloc[i]
        exit_date = data.index[i]
        pct_return = (exit_price - entry_price) / entry_price * 100
        trades.append({
            'Entry Date': entry_date.date(),
            'Exit Date': exit_date.date(),
            'Entry Price': round(entry_price, 2),
            'Exit Price': round(exit_price, 2),
            'Return (%)': round(pct_return, 2)
        })
        position_open = False  # fixed capitalization

trades_df = pd.DataFrame(trades)

# === OUTPUT ===
print("\n=== TRADE LOG ===")
print(trades_df.to_string(index=False))

print("\n=== PERFORMANCE SUMMARY ===")
print(f"Ticker:             {TICKER}")
print(f"Period:             {START_DATE} → {END_DATE}")
print(f"Short SMA Window:   {SHORT_WINDOW}")
print(f"Long SMA Window:    {LONG_WINDOW}")
print(f"Initial Balance:    ${INITIAL_BALANCE:,.2f}")
print(f"Final Balance:      ${final_value:,.2f}")
print(f"Total Return:       {total_return:.2f}%")
print(f"CAGR:               {cagr:.2%}")
print(f"Sharpe Ratio:       {sharpe_ratio:.2f}")
print(f"Max Drawdown:       {max_drawdown:.2f}%")

# === PLOTS ===
plt.figure(figsize=(14, 7))
plt.plot(data['Close'], label='Price', alpha=0.5)
plt.plot(data['SMA_Short'], label=f'SMA {SHORT_WINDOW}', linewidth=1.5)
plt.plot(data['SMA_Long'], label=f'SMA {LONG_WINDOW}', linewidth=1.5)

buy_signals = data[(data['Signal'] == 1) & (data['Signal'].shift(1) == 0)]
sell_signals = data[(data['Signal'] == 0) & (data['Signal'].shift(1) == 1)]

plt.scatter(buy_signals.index, buy_signals['Close'], marker='^', color='green', label='Buy', alpha=1)
plt.scatter(sell_signals.index, sell_signals['Close'], marker='v', color='red', label='Sell', alpha=1)

plt.title(f"{TICKER} SMA Crossover Strategy")
plt.xlabel("Date")
plt.ylabel("Price ($)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# === PORTFOLIO VALUE PLOT ===
plt.figure(figsize=(12, 5))
plt.plot(data['PORTFOLIO_VALUE'], label='Portfolio Value')
plt.title(f"Portfolio Growth — Final Value: ${final_value:,.2f}")
plt.xlabel("Date")
plt.ylabel("Portfolio Value ($)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

