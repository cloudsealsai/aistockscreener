import yfinance as yf
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

class StockAIAnalyzer:
    def __init__(self, ticker):
        self.ticker = ticker
    
    def get_stock_data(self):
        
        stock_data = yf.download(self.ticker, start="2010-01-01", end="2022-02-22")
        stock_data['Date'] = stock_data.index
        stock_data.reset_index(drop=True, inplace=True)
        stock_data['Price Diff'] = stock_data['Close'].diff()
        stock_data['Target'] = stock_data['Price Diff'].shift(-1)
        stock_data.drop(stock_data.tail(1).index, inplace=True)
    
        return stock_data
    
    def train_model(self, data):
        X = data[['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']]
        y = data['Target']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = LinearRegression()
        model.fit(X_train, y_train)
        return model
    
    def predict_target(self, model):

        latest_data = yf.download(self.ticker, period="1d")

        latest_features = latest_data[['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']].values

        predicted_target = model.predict(latest_features)

        return predicted_target[0]
    
    def suggest_buy_sell(self, predicted_target):
        # Fetch the latest stock data
        latest_data = yf.download(self.ticker, period="1d")
        
        # Get the latest closing price
        latest_close_price = latest_data['Close'].iloc[-1]
        
        # Calculate the difference between the predicted target price and the latest closing price
        price_difference = predicted_target - latest_close_price
        
        # Suggest a buy or sell decision based on the price difference
        if price_difference > 0:
            print("Suggest buying the stock")
        else:
            print("Suggest selling the stock")
