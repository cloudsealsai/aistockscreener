
#!/usr/bin/env python

try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen
import pandas as pd
import certifi
import json


def get_jsonparsed_data(url):
    response = urlopen(url, cafile=certifi.where())
    data = response.read().decode("utf-8")
    return json.loads(data)

def Get_Finanacial_data(ticker):
    
    url = ("https://financialmodelingprep.com/api/v3/income-statement/TATAMOTORS.NS?apikey=demo")
    income_statement = get_jsonparsed_data(url)

    url = ("https://financialmodelingprep.com/api/v3/balance-sheet-statement/TATAMOTORS.NS?apikey=demo")
    Balance_Sheet = get_jsonparsed_data(url)

    url = ("https://financialmodelingprep.com/api/v3/cash-flow-statement/TATAMOTORS.NS?apikey=demo")
    cash_flow = get_jsonparsed_data(url)
    
    url = ("https://financialmodelingprep.com/api/v3/ratios/"+str(ticker)+"?apikey=d19c474874f3d0f0e0ba7a5640feb49b")
    Financial_Ratios = get_jsonparsed_data(url)

    income_statement = pd.DataFrame(income_statement)
    Balance_Sheet = pd.DataFrame(Balance_Sheet)

    cash_flow = pd.DataFrame(cash_flow)
    Financial_Ratios = pd.DataFrame(Financial_Ratios)
    
    income_statement = income_statement.drop(['reportedCurrency', 'cik', 'fillingDate', 'acceptedDate', 'calendarYear', 'period'],axis=1)
    Balance_Sheet = Balance_Sheet.drop(['reportedCurrency', 'cik', 'fillingDate', 'acceptedDate', 'calendarYear', 'period'],axis=1)
    cash_flow = cash_flow.drop(['reportedCurrency', 'cik', 'fillingDate', 'acceptedDate', 'calendarYear', 'period'],axis=1)
    Financial_Ratios = Financial_Ratios.drop(['period'],axis=1)

    income_statement['date'] = pd.to_datetime(income_statement['date'])
    Balance_Sheet['date'] = pd.to_datetime(Balance_Sheet['date'])
    cash_flow['date'] = pd.to_datetime(cash_flow['date'])
    Financial_Ratios['date'] = pd.to_datetime(Financial_Ratios['date'])


    income_statement['Year'] = income_statement['date'].dt.year
    Balance_Sheet['Year'] = Balance_Sheet['date'].dt.year
    cash_flow['Year'] = cash_flow['date'].dt.year
    Financial_Ratios['Year'] = Financial_Ratios['date'].dt.year

    stock_data = pd.merge(income_statement, Balance_Sheet, on=['Year'])
    stock_data = pd.merge(stock_data, cash_flow, on=['Year'])
    stock_data = pd.merge(stock_data, Financial_Ratios, on=['Year'])
    
    stock_data['Revenue_Growth_Rate'] = stock_data['revenue'].pct_change(periods=1) * 100
    stock_data['Oprating_Margin'] = stock_data['operatingIncome']/stock_data['revenue']
    stock_data['ROIC'] = (stock_data['ebtPerEbit']*(1-0.21))/(stock_data['totalDebt']+stock_data['interestExpense'])
    stock_data['Debt to capital'] = stock_data['totalDebt']/(stock_data['totalDebt']+stock_data['totalEquity'])
    stock_data['EV/EBITDA'] = stock_data['enterpriseValueMultiple']/stock_data['ebitda']
    stock_data['Net CF from (to) Debt'] = stock_data['totalDebt']+stock_data['debtRepayment']
    stock_data['Net CF from (to) Equity'] = stock_data['commonStockIssued']+stock_data['commonStockRepurchased']+stock_data['dividendsPaid']
    
    return income_statement, Balance_Sheet, cash_flow, Financial_Ratios,stock_data

def Stock_Fundamental_Analysis_Graphs(ticker):
    
    income_statement, Balance_Sheet, cash_flow, Financial_Ratios, stock_data = Get_Finanacial_data(ticker)
    stock_data = stock_data[stock_data['Year']>2013]
    fig = plt.figure() 
   # width = 1.8
    stock_data[['revenue','operatingIncome']].plot(kind='bar', stacked=True, )
    stock_data['Revenue_Growth_Rate'].plot(secondary_y=True)
    ax = plt.gca()
    ax.set_xticklabels(stock_data['Year'],rotation=90)
    plt.show()

    fig = plt.figure() 
    stock_data[['revenue','operatingIncome']].plot(kind='bar', stacked=True, )
    stock_data['Oprating_Margin'].plot(secondary_y=True, color ='black')
    ax = plt.gca()
    ax.set_xticklabels(stock_data['Year'],rotation=45)
    plt.show()
    
    fig = plt.figure() # Create matplotlib figure
    stock_data[['operatingIncome']].plot(kind='bar', stacked=True, )
    stock_data['ROIC'].plot(secondary_y=True, color='black')
    ax = plt.gca()
    ax.set_xticklabels(stock_data['Year'])
    plt.show()
    
    fig = plt.figure() # Create matplotlib figure
    stock_data[['totalDebtToCapitalization','Debt to capital']].plot(kind='bar', stacked=True, )
    stock_data['interestCoverage'].plot(secondary_y=True, color='black')
    ax = plt.gca()
    ax.set_xticklabels(stock_data['Year'])
    plt.show()

    
    fig = plt.figure() # Create matplotlib figure
    stock_data[['priceToBookRatio','enterpriseValueMultiple']].plot(kind='bar', stacked=True, )
    stock_data['priceEarningsRatio'].plot(secondary_y=True, color='black')
    ax = plt.gca()
    ax.set_xticklabels(stock_data['Year'])
    plt.show()
    
    fig = plt.figure() # Create matplotlib figure
    stock_data[['priceToBookRatio','enterpriseValueMultiple']].plot(kind='bar', stacked=True, )
    stock_data['EV/EBITDA'].plot(secondary_y=True, color='black')
    ax = plt.gca()
    ax.set_xticklabels(stock_data['Year'])
    plt.show()

    
    fig = plt.figure() # Create matplotlib figure
    stock_data[['totalDebt','debtRepayment','commonStockIssued','commonStockRepurchased','dividendsPaid','Net CF from (to) Debt','Net CF from (to) Equity']].plot(kind='line' )
    ax = plt.gca()
    ax.set_xticklabels(stock_data['Year'],rotation=45)
    plt.show()
    return stock_data
