import yfinance as yf

class FundamentalAnalysis:
    def __init__(self, ticker):
        self.ticker = ticker
        self.stock = yf.Ticker(ticker)
        #print(self.stock.info[])
        self.market_cap = self.stock.info["marketCap"]
        self.eps = self.stock.info["trailingEps"]
        
    def get_revenue(self):
        income_statement = self.stock.financials
        revenue = income_statement.loc['Total Revenue']
        return revenue.tail()
    
    def get_net_income(self):
        income_statement = self.stock.financials
        net_income = income_statement.loc['Net Income']
        return net_income.tail()
    
    def get_pe_ratio(self):
        pe_ratio = self.market_cap / self.eps
        return pe_ratio
    
    def suggest_buy_sell(self):
        # Calculate the P/E ratio of the stock
        pe_ratio = self.get_pe_ratio()
        
        # Get the revenue growth rate
        revenue = self.get_revenue()
        revenue_growth_rate = (revenue[-1] / revenue[0]) ** (1/len(revenue)) - 1
        
        # Get the net income growth rate
        net_income = self.get_net_income()
        net_income_growth_rate = (net_income[-1] / net_income[0]) ** (1/len(net_income)) - 1
        
        # Suggest buy if P/E ratio is low and revenue/net income growth rate is high
        if pe_ratio < 15 and revenue_growth_rate > 0.1 and net_income_growth_rate > 0.1:
            sugg =  "Buy"
        
        # Suggest sell if P/E ratio is high and revenue/net income growth rate is low
        elif pe_ratio > 25 and revenue_growth_rate < 0.05 and net_income_growth_rate < 0.05:
            sugg =  "Sell"
        
        # Otherwise, suggest hold
        else:
            sugg =  "Hold"

        suggestion = 'Fundamental Analysis of stock f{self.ticker} : f{sugg}'

        return suggestion
