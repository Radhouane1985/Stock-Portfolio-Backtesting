import yfinance as yf
import backtrader as bt
import pandas as pd

# Function to detect swing highs and lows in candlestick charts
def pivotid(df1, l, n1, n2):  # n1 n2 are number of candle to count before and after candle l to consider it as High or Low
    if l - n1 < 0 or l + n2 >= len(df1):
        return 0
    
    pividlow = 1
    pividhigh = 1
    for i in range(l - n1, l + n2 + 1):
        if df1.low[l] > df1.low[i]:
            pividlow = 0
        if df1.high[l] < df1.high[i]:
            pividhigh = 0
    if pividlow and pividhigh:
        return 3
    elif pividlow:
        return 1
    elif pividhigh:
        return 2
    else:
        return 0

class YahooFinanceData(bt.feeds.PandasData):
    params = (('datetime', None),
              ('open', -1),
              ('high', -1),
              ('low', -1),
              ('close', -1),
              ('volume', -1),
              ('openinterest', -1))

# Class to Create My Trend Following Strategy Based on Range Contraction and Breakouts (with 2 sma's filter and Volume Confirmation)
class MomentumStrategy(bt.Strategy):
    
    # Model Parameters: risk_percent is the max risk per trade, max_percent is the max capital fraction invested in one trade
    params = (('before', 5), ('after', 5), ('risk_percent', 0.02), ('max_percent', 0.20))

    def __init__(self):
        self.dataframes = {}
        #self.orders = {}
        self.sma20 = {}
        self.sma50 = {}
        self.mavol = {}
        self.trades = {data._name: {'wins': 0, 'total': 0} for data in self.datas}
        
        for data in self.datas:
            self.dataframes[data._name] = pd.DataFrame(columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
            #self.orders[data._name] = None
            self.sma20[data._name] = bt.indicators.SimpleMovingAverage(data.close, period=20)
            self.sma50[data._name] = bt.indicators.SimpleMovingAverage(data.close, period=50)
            self.mavol[data._name] = bt.indicators.SimpleMovingAverage(data.volume, period=20)

    def next(self):
        for data in self.datas:
            df = self.dataframes[data._name]
            new_row = pd.DataFrame({
                'datetime': [data.datetime.datetime()],
                'open': [data.open[0]],
                'high': [data.high[0]],
                'low': [data.low[0]],
                'close': [data.close[0]],
                'volume': [data.volume[0]]
            })
            df = pd.concat([df, new_row], ignore_index=True)
            self.dataframes[data._name] = df
            
            # Logic to Detect Swing Highs and Swing Lows
            if len(df) > self.params.before + self.params.after:
                df['pivot_MT'] = df.apply(lambda x: pivotid(df, x.name, self.params.before, self.params.after), axis=1)
                listOfPos_MT = 11* [0]
                result_MT = df['pivot_MT'].isin([1, 2])
                
                for i in range(len(result_MT)):
                    if result_MT[i]:
                        listOfPos_MT.append(i)
                        listOfPos_MT.pop(0)
                
                # Ensure listOfPos_MT has enough elements
                if len(listOfPos_MT) >= 11:

                    if not self.position:

                        # Conditions to enter Long Positions
                        if df['pivot_MT'].iloc[listOfPos_MT[10]] == df['pivot_MT'].iloc[listOfPos_MT[8]] == df['pivot_MT'].iloc[listOfPos_MT[6]] == 1 and df['pivot_MT'].iloc[listOfPos_MT[9]] == df['pivot_MT'].iloc[listOfPos_MT[7]] == df['pivot_MT'].iloc[listOfPos_MT[5]] ==2:
                         
                            if (df['high'].iloc[listOfPos_MT[9]] - df['low'].iloc[listOfPos_MT[10]]) <= (df['high'].iloc[listOfPos_MT[9]] - df['low'].iloc[listOfPos_MT[8]]) <= (df['high'].iloc[listOfPos_MT[7]] - df['low'].iloc[listOfPos_MT[8]]):
                                if (df['high'].iloc[listOfPos_MT[9]] < df['high'].iloc[listOfPos_MT[7]]):

                                    if data.close[0] > df['high'].iloc[listOfPos_MT[9]]:
                                        
                                        if self.sma20[data._name] > self.sma50[data._name] and data.volume[0] > self.mavol[data._name]:
                                            risk = data.close[0] - df['low'].iloc[listOfPos_MT[10]]
                                            size = min((self.params.max_percent * self.broker.getvalue()) / data.close[0], (self.params.risk_percent * self.broker.cash) / risk)
                                            self.buy_bracket(
                                                data=data,
                                                size=size,
                                                stopprice=df['low'].iloc[listOfPos_MT[10]],
                                                limitprice=data.close[0] + 5 * risk
                                            )
                        # Conditions for Short Positions
                        elif df['pivot_MT'].iloc[listOfPos_MT[10]] == df['pivot_MT'].iloc[listOfPos_MT[8]] == df['pivot_MT'].iloc[listOfPos_MT[6]] == 2 and df['pivot_MT'].iloc[listOfPos_MT[9]] == df['pivot_MT'].iloc[listOfPos_MT[7]] == df['pivot_MT'].iloc[listOfPos_MT[5]] == 1:
                            
                            if (df['high'].iloc[listOfPos_MT[10]] - df['low'].iloc[listOfPos_MT[9]]) <= (df['high'].iloc[listOfPos_MT[8]] - df['low'].iloc[listOfPos_MT[9]]) <= (df['high'].iloc[listOfPos_MT[8]] - df['low'].iloc[listOfPos_MT[7]]):
                                if (df['low'].iloc[listOfPos_MT[9]] > df['low'].iloc[listOfPos_MT[7]]):
                                    
                                    if data.close[0] < df['low'].iloc[listOfPos_MT[9]]:

                                        if self.sma20[data._name] < self.sma50[data._name] and data.volume[0] > self.mavol[data._name]:
                                            risk = df['high'].iloc[listOfPos_MT[10]] - data.close[0]
                                            size = min((self.params.max_percent * self.broker.getvalue()) / data.close[0], (self.params.risk_percent * self.broker.cash) / risk)
                                            self.sell_bracket(
                                                data=data,
                                                size=size,
                                                stopprice=df['high'].iloc[listOfPos_MT[10]],
                                                limitprice=data.close[0] - 5 * risk
                                            )


    def stop(self):
        print('Ending Value: %.2f' % self.broker.getvalue())

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(MomentumStrategy)
    # Tickers to Invest in
    tickers = ['AAPL', 'MSFT', 'GOOG', 'AMZN', 'META', 'WMT', 'NVDA', 'AVGO', 'COST', 'TSLA']  # Add more tickers as needed
    for ticker in tickers:
        data = yf.download(ticker, start="2020-01-01", end="2024-07-04")
        data_feed = YahooFinanceData(dataname=data)
        cerebro.adddata(data_feed, name=ticker)

    cerebro.broker.setcash(100000.0)
    
    # Getting Some Statistics of the Strategy
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name = 'sharpe')
    cerebro.addanalyzer(bt.analyzers.Transactions, _name = 'trans')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name = 'trades')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name = 'drawdown')
    cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name = 'return')
    cerebro.addanalyzer(bt.analyzers.SQN, _name = 'sqn')

    # Run Cerebro Engine
    back = cerebro.run()
    fv = cerebro.broker.getvalue()
    
    # Printing Statistics
    print('----------------------------------------------------------------------------')
    print('Transactions :', back[0].analyzers.trans.get_analysis())
    print('----------------------------------------------------------------------------')
    print('Trades :', back[0].analyzers.trades.get_analysis())
    print('----------------------------------------------------------------------------')
    print('Sharpe :', back[0].analyzers.sharpe.get_analysis())
    print('----------------------------------------------------------------------------')
    print('Sqn :', back[0].analyzers.sqn.get_analysis())
    print('----------------------------------------------------------------------------')
    print('drawdown :', back[0].analyzers.drawdown.get_analysis())
    print('----------------------------------------------------------------------------')
    print('Final Value :', fv)
    
    # Plotting the Chart to see Executed Positions
    cerebro.plot()
