import yfinance as yf
import talib as ta

from Signals import Signals

class TechnicalAnalysis:
    def __init__(self, ticker):
        
        self.ticker = ticker 
        #self.stock = yf.Ticker(ticker)
        self.data = Signals(ticker).getStockData()
        
    def get_sma(self, period):
        sma = ta.SMA(self.data["Close"], timeperiod=period)
        return sma
    
    def get_ema(self, period):
        ema = ta.EMA(self.data["Close"], timeperiod=period)
        return ema
    
    def get_macd(self):
        macd, signal, hist = ta.MACD(self.data["Close"], fastperiod=12, slowperiod=26, signalperiod=9)
        return macd, signal, hist
    
    def get_rsi(self):
        rsi = ta.RSI(self.data["Close"], timeperiod=14)
        return rsi

    def get_BB(self):
        BUpper, BMiddle, BLower= ta.BBANDS(self.data['Close'], timeperiod=20, nbdevup=2, nbdevdn=2)
        return BUpper, BMiddle, BLower

    
    def suggest_trade(self):
        sma50 = self.get_sma(50)
        sma20 = self.get_sma(20)
        sma200 = self.get_sma(200)
        ema20 = self.get_ema(20)
        ema50 = self.get_ema(50)
        macd, signal, hist = self.get_macd()
        rsi = self.get_rsi()
        BBU, BBM, BBL = self.get_BB()
        
        last_close = self.data["Close"].iloc[-1]
        last_macd = macd.iloc[-1]
        last_signal = signal.iloc[-1]
        last_hist = hist.iloc[-1]
        last_rsi = rsi.iloc[-1]
        
        if last_close > sma50.iloc[-1] and last_close > sma200.iloc[-1] and last_close > ema20.iloc[-1] and last_macd > last_signal and last_rsi > 50:
            sugg =  "Buy"
        elif last_close < sma50.iloc[-1] and last_close < sma200.iloc[-1] and last_close < ema20.iloc[-1] and last_macd < last_signal and last_rsi < 50:
            sugg =  "Sell"
        else:
            sugg =  "Hold"

        # All Technicals
        signals = {}
        if last_close > sma20.iloc[-1] and last_close > sma50.iloc[-1]:
            signals['MA'] = 'Buy'
        else:
            signals['MA'] = 'Sell'

        if ema20.iloc[-1] > ema50.iloc[-1]:
            signals['EMA'] = 'Buy'
        else:
            signals['EMA'] = 'Sell'

        if last_rsi > 70:
            signals['RSI'] = 'Sell'
        elif last_rsi < 30:
            signals['RSI'] = 'Buy'
        else:
            signals['RSI'] = 'Hold'

        if last_hist > 0:
            signals['MACD'] = 'Buy'
        else:
            signals['MACD'] = 'Sell'

        if last_close > BBU.iloc[-1]:
            signals['BB'] = 'Sell'
        elif last_close < BBL.iloc[-1]:
            signals['BB'] = 'Buy'
        else:
            signals['BB'] = 'Hold'

        
        # Print the signals for the stock
        print(f"\nTechnical Analysis Signals for {self.ticker}\n")
        print(f"Moving Average: {signals['MA']}")
        print(f"Exponential Moving Average: {signals['EMA']}")
        print(f"Relative Strength Index: {signals['RSI']}")
        print(f"Moving Average Convergence Divergence: {signals['MACD']}")
        print(f"Bollinger Bands: {signals['BB']}\n")

        print(f"{self.ticker} Technical Analysis overview : {sugg}\n")

        return sugg
