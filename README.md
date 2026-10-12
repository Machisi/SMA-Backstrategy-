# SMA Crossover Backtest

A Python backtest of a long-only simple moving average (SMA) crossover strategy on Apple (AAPL). The script downloads daily price data, turns a 20/50-day crossover into portfolio returns, summarizes performance and completed trades, and displays two charts.

## Strategy at a glance

| Setting | Value |
| --- | --- |
| Asset | Apple (AAPL) |
| Data | Daily prices from Yahoo Finance via [yfinance](https://ranaroussi.github.io/yfinance/) |
| Backtest start | September 1, 2024 |
| Backtest end | Current date at runtime; the download end date is exclusive |
| Moving averages | 20 trading days (short) and 50 trading days (long) |
| Position | Fully invested when SMA 20 > SMA 50; otherwise in cash |
| Starting portfolio value | $75 |
| Risk-free rate | 4% annually, used in the Sharpe ratio |

The strategy uses the **previous day's position** to calculate each day's return:

```text
position[t]        = 1 if SMA20[t] > SMA50[t], otherwise 0
strategy_return[t] = position[t-1] × close_to_close_return[t]
portfolio_value[t] = $75 × cumulative_product(1 + strategy_return)
```

This one-day shift prevents the return calculation from applying a signal to the same day's price move that produced it.

## Run the backtest

With Python 3 installed, install the dependencies (preferably in a virtual environment) and run the script:

```bash
python -m pip install numpy pandas matplotlib yfinance
python sma_backtest.py
```

The script needs an internet connection to download prices and a graphical environment to display the charts. Configuration is defined at the top of [sma_backtest.py](./sma_backtest.py); change the ticker, dates, moving-average windows, starting balance, or risk-free rate there before running it.

## Output

- **Console:** a log of completed buy-to-sell trades, followed by final portfolio value, total return, CAGR, Sharpe ratio, and maximum drawdown.
- **Price chart:** closing price, both SMAs, and crossover buy/sell markers.
- **Portfolio chart:** the compounded value of the strategy over the test period.

Results are calculated when the script runs. No fixed performance figure is shown here because the end date moves forward with each run.

## Scope and assumptions

- The model is long-only and applies the full portfolio return when invested. Cash earns no interest; fractional exposure is implicit in the $75 starting balance.
- Transaction fees, bid-ask spread, slippage, and taxes are excluded.
- The trade log uses closing prices on crossover dates for illustration. Portfolio returns use the previous day's signal, so the trade log is not a fill-by-fill reconciliation of the equity curve. An open position at the end of the sample is not listed as a completed trade.
- The study covers one asset and one parameter pair. It does not include a buy-and-hold benchmark, out-of-sample testing, or parameter optimization.
- Price adjustment and column layout follow the installed `yfinance` version's defaults. Fix the end date and data settings before comparing runs or reporting a reproducible result.

This project is a research exercise, not a live trading system or investment recommendation.
