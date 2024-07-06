# Momentum Trading Strategy with Backtrader

This repository contains a momentum trading strategy implemented using Backtrader, a popular Python framework for backtesting trading strategies. The strategy is designed to detect swing highs and lows in candlestick charts and execute trades based on range contraction and breakouts, with additional filters for moving averages and volume confirmation.

## Strategy Overview

The strategy implemented in this code focuses on identifying potential entry points based on the following criteria:

1. **Swing Highs and Lows Detection**: Utilizes a custom function `pivotid` to identify swing highs and lows in candlestick data.

2. **Moving Averages (SMA)**: Filters trades based on the relationship between a 20-period and 50-period Simple Moving Average (SMA).

3. **Volume Confirmation**: Ensures that trades are executed only when trading volume exceeds a 20-period SMA of volume.

4. **Risk Management**: Limits risk exposure by calculating position sizes dynamically based on the maximum risk per trade and the maximum capital fraction allocated to a single trade.

5. **Execution**: Executes trades using bracket orders (`buy_bracket` for long positions and `sell_bracket` for short positions) with predefined stop-loss and take-profit levels.

## Getting Started

To run the strategy:

1. **Install Dependencies**:
   - Ensure you have Python 3.x installed.
   - Install required libraries using `pip install -r requirements.txt`.

2. **Run the Strategy**:
   - Adjust the `tickers` list to include desired stocks for backtesting.
   - Set the start and end dates for historical data in the `yf.download` function.

3. **View Results**:
   - The strategy computes various performance metrics including Sharpe Ratio, drawdown, annual returns, and more.
   - Executed trades and positions can be visualized using the built-in plotting functionality of Backtrader.

## Performance Metrics

After running the strategy, the following statistics are printed:

- **Transactions**: Detailed transaction history including buy and sell orders.
- **Trades**: Analysis of trade outcomes including win rate, total trades, and more.
- **Sharpe Ratio**: Measure of risk-adjusted return.
- **SQN (System Quality Number)**: Assessment of trade distribution's quality.
- **Drawdown**: Analysis of peak-to-trough decline during the strategy's trading period.
- **Final Value**: Portfolio value at the end of the backtest period.
