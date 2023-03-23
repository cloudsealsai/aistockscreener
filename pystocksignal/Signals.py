import yfinance as yf
import plotly.offline as py
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import talib
import mplfinance as mpf
import matplotlib.pyplot as plt
from utils import utils
from datetime import datetime, date


class Signals():
   
    def __init__(self, yticker = None, days = 252) -> None:
        self.u = utils()
        if yticker is not None:
            self.yticker = yticker
        self.days = days
        

    def getStockData(self, yticker = None):

        if yticker is not None:
            self.yticker = yticker
        
        try:
            _df = yf.download(tickers= self.yticker+".NS", progress=False, show_errors=False)
            if _df.empty:
                _df = yf.download(tickers=self.yticker+".BO", progress=False, show_errors=False)
        except:
            _df = pd.DataFrame()

        #print('Data not available : {}'.format(self.yticker))
        #_df = pd.DataFrame()

        if not _df.empty:
        
            _df.reset_index(inplace=True)
            days_sdata =int( (_df['Date'].max() - _df['Date'].min()).days)

            #print(days_sdata)
            #print(self.days)

            if days_sdata > self.days:
                #print('inside days check')
                #self.days = days_sdata 
                n = int(self.days)*-1
                #print(n)
                self.adf = _df.iloc[n:]
                #print(self.adf)
                #print(self.adf.shape)
            else:
                self.adf = _df#.iloc[self.days*-1:].copy()
                #print(self.adf.shape)
                #print(self.adf.shape)
            #print("Actual data is {} days, Analysing the {} stock data of {}. \n".format(days_sdata ,self.yticker, self.days))
        else:
            self.adf = pd.DataFrame()
        
        
        
        return self.adf

    def stockAnalysis(self):

        try:

            self.adf.dropna(inplace = True, axis = 0)

            dict_stockAnlys = {}
            dict_stockAnlys['Ticker'] = self.yticker
            dict_stockAnlys['Data_Available'] = self.days
            stats_stock = self.adf.describe().astype(int)
            #print(stats_stock)
            dict_stockAnlys['bStats'] = stats_stock

            print(""" In last {} days, the average closing price for {} stock was about ₹{}.
                For about 75% of time the stock was trading below ₹{} and it clocked maximum 
                of ₹{}. The maximum volume of shares traded on a single day was {} with 
                median quantity being 2776142. \n \n""".format(self.days, self.yticker
                                                        , stats_stock['Close'].iloc[1]
                                                        , stats_stock['Close'].iloc[6]
                                                        , stats_stock['Close'].iloc[7]
                                                        , stats_stock['Volume'].iloc[7]
                                                        , stats_stock['Volume'].iloc[6]))
            
            perc_adf = self.adf.copy()
            perc_adf['Days_perc_change'] = perc_adf['Adj Close'].pct_change()*100
            perc_adf.dropna(axis = 0, inplace = True)
            perc_adf.set_index('Date', inplace=True)

            print('Percentage Change Returns Analysis \n ')

            perc_adf['Days_perc_change'].plot(figsize=(12,6), fontsize=12)
            #pd.plot(perc_adf['Date'], perc_adf['Days_perc_change'])
            plt.xlabel('Date')
            plt.ylabel('Daily Return')
            plt.show()

            print('\n Returns Histogram Analysis \n ')

            perc_adf['Days_perc_change'].hist(bins = 50, figsize=(10, 5))
            plt.xlabel('Daily Returns')
            plt.ylabel('Frequency')
            plt.show()

            perc_describe = perc_adf.Days_perc_change.describe()

            print("""\n \n For the past {} days, the mean daily returns has been about {} and for the most
            of the days the daily return was less than {}. During this period, the highest percentage change in positive 
            direction was observed to be {}% and was {}% in downward direction \n \n """.format(self.days,round(perc_describe.iloc[1],2)
                                                                                        ,round(perc_describe.iloc[6], 2)
                                                                                        ,round(perc_describe.iloc[7], 2) ,
                                                                                        round(perc_describe.iloc[3],2)))


            print(" \n Trend Analysis \n")
            perc_adf["Trend"]= np.zeros(perc_adf["Days_perc_change"].count())
            perc_adf["Trend"]= perc_adf["Days_perc_change"].apply(lambda x:self.u.trend(x))
            
            pie_data = perc_adf.groupby('Trend')
            pie_label = sorted([i for i in perc_adf.loc[:, 'Trend'].unique()])
            plt.pie(pie_data['Trend'].count(), labels = pie_label, autopct = '%1.1f%%', radius = 1)
            plt.show()

            perc_adf.reset_index(inplace=True)

            # vol = perc_adf['Adj Close'].rolling(7).std()*np.sqrt(7)
            # vol.plot(figsize = (10, 5))
            print('\n Returns vs Volume Analysis \n ')
            plt.stem(perc_adf["Date"], perc_adf["Days_perc_change"])
            perc_adf.set_index('Date',inplace=True)
            (perc_adf["Volume"]/10000000).plot( color = "green", alpha = 0.5)

            perc_adf['SMA20'] = talib.SMA(perc_adf['Close'], timeperiod=20)
            perc_adf['SMA50'] = talib.SMA(perc_adf['Close'], timeperiod=50)
            perc_adf['EMA20'] = talib.EMA(perc_adf['Close'], timeperiod=20)
            perc_adf['EMA50'] = talib.EMA(perc_adf['Close'], timeperiod=50)
            perc_adf['RSI'] = talib.RSI(perc_adf['Close'], timeperiod=14)
            perc_adf['MACD'], perc_adf['MACDsignal'], perc_adf['MACDhist'] = talib.MACD(perc_adf['Close'], fastperiod=12, slowperiod=26, signalperiod=9)
            perc_adf['BBupper'], perc_adf['BBmiddle'], perc_adf['BBlower'] = talib.BBANDS(perc_adf['Close'], timeperiod=20, nbdevup=2, nbdevdn=2)

            # Generate technical analysis signals based on the indicators
            signals = {}
            if perc_adf['Close'].iloc[-1] > perc_adf['SMA20'].iloc[-1] and perc_adf['Close'].iloc[-1] > perc_adf['SMA50'].iloc[-1]:
                signals['MA'] = 'Buy'
            else:
                signals['MA'] = 'Sell'
            if perc_adf['EMA20'].iloc[-1] > perc_adf['EMA50'].iloc[-1]:
                signals['EMA'] = 'Buy'
            else:
                signals['EMA'] = 'Sell'
            if perc_adf['RSI'].iloc[-1] > 70:
                signals['RSI'] = 'Sell'
            elif perc_adf['RSI'].iloc[-1] < 30:
                signals['RSI'] = 'Buy'
            else:
                signals['RSI'] = 'Hold'
            if perc_adf['MACDhist'].iloc[-1] > 0:
                signals['MACD'] = 'Buy'
            else:
                signals['MACD'] = 'Sell'
            if perc_adf['Close'].iloc[-1] > perc_adf['BBupper'].iloc[-1]:
                signals['BB'] = 'Sell'
            elif perc_adf['Close'].iloc[-1] < perc_adf['BBlower'].iloc[-1]:
                signals['BB'] = 'Buy'
            else:
                signals['BB'] = 'Hold'

            # Print the signals for the stock
            # print(f"Technical Analysis Signals for {self.yticker}")
            # print(f"Moving Average: {signals['MA']}")
            # print(f"Exponential Moving Average: {signals['EMA']}")
            # print(f"Relative Strength Index: {signals['RSI']}")
            # print(f"Moving Average Convergence Divergence: {signals['MACD']}")
            # print(f"Bollinger Bands: {signals['BB']}")

            # Plot the technical indicators
            
            fig, ax = plt.subplots(2, sharex=True, figsize=(12,8))

            ax[0].set_title(f'Technical Analysis for {self.yticker}')
            ax[0].plot(perc_adf.index, perc_adf['Close'], label='Close')
            ax[0].plot(perc_adf.index, perc_adf['SMA20'], label='SMA20')
            ax[0].plot(perc_adf.index, perc_adf['SMA50'], label='SMA50')
            ax[0].plot(perc_adf.index, perc_adf['EMA20'], label='EMA20')
            ax[0].plot(perc_adf.index, perc_adf['EMA50'], label='EMA50')
            ax[0].legend()

            ax[1].plot(perc_adf.index, perc_adf['RSI'], label='RSI')
            ax[1].plot(perc_adf.index, perc_adf['MACD'], label='MACD')
            ax[1].plot(perc_adf.index, perc_adf['MACDsignal'], label='MACD Signal')
            ax[1].bar(perc_adf.index, perc_adf['MACDhist'], label='MACD Hist')
            ax[1].plot(perc_adf.index, perc_adf['BBupper'], label='Bollinger Band Upper')
            ax[1].plot(perc_adf.index, perc_adf['BBmiddle'], label='Bollinger Band Middle')
            ax[1].plot(perc_adf.index, perc_adf['BBlower'], label='Bollinger Band Lower')
            ax[1].legend()

            plt.show()
        except:
            print('error in sAnalysis')

        


    def signal_hypothetical(self):

        df_signals = self.adf.copy()
        df_signals['Buy_Signal'] = 0
        df_signals['Sell_Signal'] = 0
        df_signals['Marker_buy'] = np.nan
        df_signals['Marker_sell'] = np.nan
        df_signals['Symbol'] = "circle"
        df_signals['Color'] = "aqua"

        for i in range(len(df_signals)):
            try:
                Buy_condition = ((df_signals.iloc[i]['Low'] < df_signals.iloc[i-5]['Low']) 
                    and (df_signals.iloc[i]['Low'] < df_signals.iloc[i-13]['Low']) 
                    and (df_signals.iloc[i]['Low'] < df_signals.iloc[i-21]['Low'])  
                    and (df_signals.iloc[i]['Close'] > df_signals.iloc[i-1]['Close']) 
                    and (df_signals.iloc[i+1]['Buy_Signal'] == 0))
                
                Sell_condition = ((df_signals.iloc[i]['High'] > df_signals.iloc[i-5]['High']) 
                    and (df_signals.iloc[i]['High'] > df_signals.iloc[i-13]['High']) 
                    and (df_signals.iloc[i]['High'] > df_signals.iloc[i-21]['High'])  
                    and (df_signals.iloc[i]['Close'] < df_signals.iloc[i-1]['Close']) 
                    and (df_signals.iloc[i+1]['Sell_Signal'] == 0))
                # Bullish
                if Buy_condition:
                
                    df_signals.iloc[i+1, df_signals.columns.get_loc('Buy_Signal')] = 1
                    df_signals.iloc[i+1, df_signals.columns.get_loc('Marker_buy')] = df_signals.iloc[i]['Low']*0.98
                    df_signals.iloc[i+1, df_signals.columns.get_loc('Color')] = "green"
                                
                # Bearish
                elif Sell_condition:
                    df_signals.iloc[i+1, df_signals.columns.get_loc('Sell_Signal')] = -1
                    df_signals.iloc[i+1, df_signals.columns.get_loc('Marker_sell')] = df_signals.iloc[i]['High']*1.02
                    df_signals.iloc[i+1, df_signals.columns.get_loc('Color')] = "red"
                
            except Exception as e:
                pass
                print(e)
            
        try:
            apd = [mpf.make_addplot(df_signals['Marker_buy'], scatter=True, markersize = 10, marker= r'$\Uparrow$', color = 'green'), mpf.make_addplot(df_signals['Marker_sell'], scatter=True, markersize = 10, marker= r'$\Downarrow$', color = 'red')]

            print('Stock : {} \nSignal Type : Hypothetical \n'.format(self.yticker))
            mpf.plot(self.adf.set_index('Date'), type = 'candle',volume = True, addplot= apd )    

            self.sHypo_df = df_signals.copy()  
        except:
            print('Error in HSignal')
            
        #return sHypo_df

    # def stock_52wHigh(self):

    #     df_signals = self.adf.copy()
    #     df_signals['Buy_Signal'] = 0
    #     df_signals['Sell_Signal'] = 0
    #     df_signals['Marker_buy'] = np.nan
    #     df_signals['Marker_sell'] = np.nan
    #     df_signals['Symbol'] = "circle"
    #     df_signals['Color'] = "aqua"

    #     for i in range(len(df_signals)):
    #         try:
    #             Buy_condition = ((df_signals.iloc[i]['Low'] < df_signals.iloc[i-5]['Low']) 
    #                 and (df_signals.iloc[i]['Low'] < df_signals.iloc[i-13]['Low']) 
    #                 and (df_signals.iloc[i]['Low'] < df_signals.iloc[i-21]['Low'])  
    #                 and (df_signals.iloc[i]['Close'] > df_signals.iloc[i-1]['Close']) 
    #                 and (df_signals.iloc[i+1]['Buy_Signal'] == 0))
                
    #             Sell_condition = ((df_signals.iloc[i]['High'] > df_signals.iloc[i-5]['High']) 
    #                 and (df_signals.iloc[i]['High'] > df_signals.iloc[i-13]['High']) 
    #                 and (df_signals.iloc[i]['High'] > df_signals.iloc[i-21]['High'])  
    #                 and (df_signals.iloc[i]['Close'] < df_signals.iloc[i-1]['Close']) 
    #                 and (df_signals.iloc[i+1]['Sell_Signal'] == 0))

    #             # Bullish
    #             if Buy_condition:
                
    #                 df_signals.iloc[i+1, df_signals.columns.get_loc('Buy_Signal')] = 1
    #                 df_signals.iloc[i+1, df_signals.columns.get_loc('Marker_buy')] = df_signals.iloc[i]['Low']*0.98
    #                 df_signals.iloc[i+1, df_signals.columns.get_loc('Color')] = "green"
                                
    #             # Bearish
    #             elif Sell_condition:
    #                 df_signals.iloc[i+1, df_signals.columns.get_loc('Sell_Signal')] = -1
    #                 df_signals.iloc[i+1, df_signals.columns.get_loc('Marker_sell')] = df_signals.iloc[i]['High']*1.02
    #                 df_signals.iloc[i+1, df_signals.columns.get_loc('Color')] = "red"
                
    #         except Exception as e:
    #             pass
    #             print(e)
            
    #     apd = [mpf.make_addplot(df_signals['Marker_buy'], scatter=True, markersize = 10, marker= r'$\Uparrow$', color = 'green'), mpf.make_addplot(df_signals['Marker_sell'], scatter=True, markersize = 10, marker= r'$\Downarrow$', color = 'red')]

    #     print('Stock : {} \nSignal Type : Hypothetical \n'.format(self.yticker))
    #     mpf.plot(self.adf.set_index('Date'), type = 'candle',volume = True, addplot= apd )    

    #     sHypo_df = df_signals.copy()  

    def signal_DarvasBox(self):

        # Only for Bull Market Environment
        EMA = self.adf['Close'].ewm(span=200, adjust=False).mean()
        EMA_vol = self.adf['Volume'].ewm(span=200, adjust=False).mean()
        #print(self.df)
        #print(EMA)
        ema_plot = [mpf.make_addplot(EMA, color = 'green'), mpf.make_addplot(EMA_vol, color = 'red' )]
        mpf.plot(self.adf.set_index('Date'), type = 'candle',volume = True, addplot= ema_plot ) 

        #Darvas Box Logic 

        self.logic_darvasbox(self.adf)

        #max_252, idxmax_252 = max(self.adf.High), self.adf.loc[self.adf.High.idxmax(), 'Date']

    def logic_darvasbox(self, df):

        _max, idx = max(df.High), df.loc[df.High.idxmax(), 'Date']
        self.darvasBuy = _max*1.035
        #print(idx.strftime('%Y%m%d'))

        df_darvasCheck = df.loc[self.adf.Date >= idx]
        df_darvas_before_high = df.loc[self.adf.Date < idx]
        #print(df_darvas_before_high)

        darvas_count = 0
        darvas_screening_dict = {}
        darvas_list = []
        _date = datetime.now()

        #print(df_darvasCheck)

        if len(df_darvasCheck) >= 2:
        
            if (df_darvasCheck['High'].iloc[1] < _max) :
                darvas_count = darvas_count+1
                box_min, minbox_date = df_darvasCheck['Low'].iloc[1], df_darvasCheck['Date'].iloc[1]

                darvas_screening_dict['Date'] = _date
                darvas_screening_dict['Day'] = darvas_count
                darvas_screening_dict['Status'] = '1_Forming'
                darvas_screening_dict['Market_ticker'] = self.yticker
                darvas_screening_dict['NewHigh_Date'] = idx.strftime('%Y-%m-%d')
                darvas_screening_dict['NewHigh_closeprice'] = round(df_darvasCheck['Close'].iloc[0],2)
                darvas_screening_dict['Current_closeprice'] = round(df_darvasCheck['Close'].iloc[1],2)
                darvas_screening_dict['NewHigh_highprice'] = round(df_darvasCheck['High'].iloc[0],2)
                darvas_screening_dict['NewHigh_volume'] = df_darvasCheck['Volume'].iloc[0]
                darvas_screening_dict['buyPrice'] = round(df_darvasCheck['High'].iloc[0]*1.035,2)
                darvas_screening_dict['stoploss_changes'] = round(box_min*0.975,2)
                darvas_screening_dict['Low_price_stoploss_date'] = minbox_date.strftime('%Y-%m-%d')
                darvas_screening_dict['DBox'] = True
                darvas_screening_dict['Day_1_HP'] = df_darvasCheck['High'].iloc[1]
                darvas_screening_dict['Day_1_CP'] = df_darvasCheck['High'].iloc[1]
                
                # darvas_screening_dict['Hypthetical_buy_date'] = self.sHypo_df.loc[self.sHypo_df.Buy_Signal == 1]['Date'].iloc[-1]
                # darvas_screening_dict['Hypthetical_sell_date'] = self.sHypo_df.loc[self.sHypo_df.Sell_Signal == -1]['Date'].iloc[-1]
                

                if (len(df_darvasCheck) >= 3):

                    if (((darvas_count == 1) and (df_darvasCheck['High'].iloc[2] <= df_darvasCheck['High'].iloc[1])) or ((darvas_count == 1) and (df_darvasCheck['High'].iloc[2] <= _max))) :
                        darvas_count = darvas_count+1
                        box_min, minbox_date = df_darvasCheck['Low'].iloc[2], df_darvasCheck['Date'].iloc[2]
                        
                        darvas_screening_dict['Date'] = _date
                        darvas_screening_dict['Day'] = darvas_count
                        darvas_screening_dict['Status'] = '2_Forming'
                        darvas_screening_dict['Market_ticker'] = self.yticker
                        darvas_screening_dict['NewHigh_Date'] = idx.strftime('%Y-%m-%d')
                        darvas_screening_dict['NewHigh_closeprice'] = round(df_darvasCheck['Close'].iloc[0],2)
                        darvas_screening_dict['Current_closeprice'] = round(df_darvasCheck['Close'].iloc[2],2)
                        darvas_screening_dict['NewHigh_highprice'] = round(df_darvasCheck['High'].iloc[0],2)
                        darvas_screening_dict['NewHigh_volume'] = df_darvasCheck['Volume'].iloc[0]
                        darvas_screening_dict['buyPrice'] = round(df_darvasCheck['High'].iloc[0]*1.035,2)
                        darvas_screening_dict['stoploss_changes'] = round(box_min*0.975,2)
                        darvas_screening_dict['Low_price_stoploss_date'] = minbox_date.strftime('%Y-%m-%d')
                        darvas_screening_dict['Day_1_HP'] = df_darvasCheck['High'].iloc[1]
                        darvas_screening_dict['Day_1_CP'] = df_darvasCheck['Close'].iloc[1]
                        darvas_screening_dict['Day_2_HP'] = df_darvasCheck['High'].iloc[2]
                        darvas_screening_dict['Day_2_CP'] = df_darvasCheck['Close'].iloc[2]
                     
                        # darvas_screening_dict['Hypthetical_buy_date'] = self.sHypo_df.loc[self.sHypo_df.Buy_Signal == 1]['Date'].iloc[-1]
                        # darvas_screening_dict['Hypthetical_sell_date'] = self.sHypo_df.loc[self.sHypo_df.Sell_Signal == -1]['Date'].iloc[-1]
                        darvas_screening_dict['DBox'] = True

                        if (len(df_darvasCheck) >= 4):
                            if (((darvas_count == 2) and (df_darvasCheck['High'].iloc[3] <= df_darvasCheck['High'].iloc[2])) or ((darvas_count == 2) and df_darvasCheck['High'].iloc[3] <= _max)) :
                                darvas_count = darvas_count+1
                                #box_min, minbox_date = df_darvasCheck['Low'].iloc[2], df_darvasCheck['Date'].iloc[2]
                                box_min, minbox_date = df_darvasCheck['Low'].iloc[3], df_darvasCheck['Date'].iloc[3]
                                darvas_screening_dict['Date'] = _date
                                darvas_screening_dict['Day'] = darvas_count
                                darvas_screening_dict['Status'] = '3_Formed'
                                darvas_screening_dict['Market_ticker'] = self.yticker
                                darvas_screening_dict['NewHigh_Date'] = idx.strftime('%Y-%m-%d')
                                darvas_screening_dict['NewHigh_closeprice'] = round(df_darvasCheck['Close'].iloc[0],2)
                                darvas_screening_dict['Current_closeprice'] = round(df_darvasCheck['Close'].iloc[3],2)
                                darvas_screening_dict['NewHigh_highprice'] = round(df_darvasCheck['High'].iloc[0],2)
                                darvas_screening_dict['NewHigh_volume'] = df_darvasCheck['Volume'].iloc[0]
                                darvas_screening_dict['buyPrice'] = round(df_darvasCheck['High'].iloc[0]*1.035,2)
                                darvas_screening_dict['stoploss_changes'] = round(box_min*0.975,2)
                                darvas_screening_dict['Low_price_stoploss_date'] = minbox_date.strftime('%Y-%m-%d')
                                darvas_screening_dict['Day_1_HP'] = df_darvasCheck['High'].iloc[1]
                                darvas_screening_dict['Day_1_CP'] = df_darvasCheck['Close'].iloc[1]
                                darvas_screening_dict['Day_2_HP'] = df_darvasCheck['High'].iloc[2]
                                darvas_screening_dict['Day_2_CP'] = df_darvasCheck['Close'].iloc[2]
                                darvas_screening_dict['Day_3_HP'] = df_darvasCheck['High'].iloc[3]
                                darvas_screening_dict['Day_3_CP'] = df_darvasCheck['Close'].iloc[3]     
                                darvas_screening_dict['Current_HP'] = df_darvasCheck['High'].iloc[-1]
                                darvas_screening_dict['Current_CP'] = df_darvasCheck['Close'].iloc[-1] 
                                                          # darvas_screening_dict['Hypthetical_buy_date'] = self.sHypo_df.loc[self.sHypo_df.Buy_Signal == 1]['Date'].iloc[-1]
                                # darvas_screening_dict['Hypthetical_sell_date'] = self.sHypo_df.loc[self.sHypo_df.Sell_Signal == -1]['Date'].iloc[-1]
                                darvas_screening_dict['DBox'] = True
                                
                                print("Pattern D-Box already Formed for {}".format(self.yticker))
                                
                            elif (df_darvasCheck['High'].iloc[3] >= _max):

                                box_min, minbox_date = df_darvasCheck['Low'].iloc[2], df_darvasCheck['Date'].iloc[2]
                                
                                darvas_screening_dict['Date'] = _date
                                darvas_screening_dict['Day'] = darvas_count
                                darvas_screening_dict['Status'] = '3_Forming_Moved_up'
                                darvas_screening_dict['Market_ticker'] = self.yticker
                                darvas_screening_dict['NewHigh_Date'] = idx.strftime('%Y-%m-%d')
                                darvas_screening_dict['NewHigh_closeprice'] = round(df_darvasCheck['Close'].iloc[0],2)
                                darvas_screening_dict['Current_closeprice'] = round(df_darvasCheck['Close'].iloc[2],2)
                                darvas_screening_dict['NewHigh_highprice'] = round(df_darvasCheck['High'].iloc[0],2)
                                darvas_screening_dict['NewHigh_volume'] = df_darvasCheck['Volume'].iloc[0]
                                darvas_screening_dict['buyPrice'] = round(df_darvasCheck['High'].iloc[0]*1.035,2)
                                darvas_screening_dict['stoploss_changes'] = round(box_min*0.975,2)
                                darvas_screening_dict['Low_price_stoploss_date'] = minbox_date.strftime('%Y-%m-%d')
                                darvas_screening_dict['Day_1_HP'] = df_darvasCheck['High'].iloc[1]
                                darvas_screening_dict['Day_1_CP'] = df_darvasCheck['Close'].iloc[1]
                                darvas_screening_dict['Day_2_HP'] = df_darvasCheck['High'].iloc[2]
                                darvas_screening_dict['Day_2_CP'] = df_darvasCheck['Close'].iloc[2]
                                darvas_screening_dict['Day_3_HP'] = df_darvasCheck['High'].iloc[3]
                                darvas_screening_dict['Day_3_CP'] = df_darvasCheck['Close'].iloc[3]
                            
                                # darvas_screening_dict['Hypthetical_buy_date'] = self.sHypo_df.loc[self.sHypo_df.Buy_Signal == 1]['Date'].iloc[-1]
                                # darvas_screening_dict['Hypthetical_sell_date'] = self.sHypo_df.loc[self.sHypo_df.Sell_Signal == -1]['Date'].iloc[-1]
                                darvas_screening_dict['DBox'] = True
   
                            
                    elif (df_darvasCheck['High'].iloc[2] >= _max):
                        box_min, minbox_date = df_darvasCheck['Low'].iloc[2], df_darvasCheck['Date'].iloc[2]
                        
                        darvas_screening_dict['Date'] = _date
                        darvas_screening_dict['Day'] = darvas_count
                        darvas_screening_dict['Status'] = '2_Forming_Moved_up'
                        darvas_screening_dict['Market_ticker'] = self.yticker
                        darvas_screening_dict['NewHigh_Date'] = idx.strftime('%Y-%m-%d')
                        darvas_screening_dict['NewHigh_closeprice'] = round(df_darvasCheck['Close'].iloc[0],2)
                        darvas_screening_dict['Current_closeprice'] = round(df_darvasCheck['Close'].iloc[2],2)
                        darvas_screening_dict['NewHigh_highprice'] = round(df_darvasCheck['High'].iloc[0],2)
                        darvas_screening_dict['NewHigh_volume'] = df_darvasCheck['Volume'].iloc[0]
                        darvas_screening_dict['buyPrice'] = round(df_darvasCheck['High'].iloc[0]*1.035,2)
                        darvas_screening_dict['stoploss_changes'] = round(box_min*0.975,2)
                        darvas_screening_dict['Low_price_stoploss_date'] = minbox_date.strftime('%Y-%m-%d')
                        darvas_screening_dict['Day_1_HP'] = df_darvasCheck['High'].iloc[1]
                        darvas_screening_dict['Day_1_CP'] = df_darvasCheck['Close'].iloc[1]
                        darvas_screening_dict['Day_2_HP'] = df_darvasCheck['High'].iloc[2]
                        darvas_screening_dict['Day_2_CP'] = df_darvasCheck['Close'].iloc[2]
                     
                        # darvas_screening_dict['Hypthetical_buy_date'] = self.sHypo_df.loc[self.sHypo_df.Buy_Signal == 1]['Date'].iloc[-1]
                        # darvas_screening_dict['Hypthetical_sell_date'] = self.sHypo_df.loc[self.sHypo_df.Sell_Signal == -1]['Date'].iloc[-1]
                        darvas_screening_dict['DBox'] = True

                # elif (darvas_count == 2) and df_darvasCheck['High'].iloc[3] > _max:
                #     self.logic_darvasbox(df_darvasCheck['High'].iloc[3:])
                
                    

            elif (df_darvasCheck['High'].iloc[1] >= _max) :
                
                box_min, minbox_date = df_darvasCheck['Low'].iloc[0], df_darvasCheck['Date'].iloc[0]
                darvas_screening_dict['Date'] = _date
                darvas_screening_dict['Day'] = 0
                darvas_screening_dict['Status'] = 'MovedUp_Screening'
                darvas_screening_dict['Market_ticker'] = self.yticker
                darvas_screening_dict['NewHigh_Date'] = idx.strftime('%Y-%m-%d')
                darvas_screening_dict['NewHigh_closeprice'] = round(df_darvasCheck['Close'].iloc[0],2)
                darvas_screening_dict['Current_closeprice'] = round(df_darvasCheck['Close'].iloc[1],2)
                darvas_screening_dict['NewHigh_highprice'] = round(df_darvasCheck['High'].iloc[0],2)
                darvas_screening_dict['NewHigh_volume'] = df_darvasCheck['Volume'].iloc[0]
                darvas_screening_dict['buyPrice'] = round(df_darvasCheck['High'].iloc[0]*1.035,2)
                darvas_screening_dict['stoploss_changes'] = round(box_min*0.975,2)
                darvas_screening_dict['Low_price_stoploss_date'] = minbox_date.strftime('%Y-%m-%d')
                darvas_screening_dict['DBox'] = True

            else:
                #print(df_darvasCheck['High'].iloc[1])
                #print(_max)
                #print(len(df_darvasCheck))
                pass
        
        elif len(df_darvasCheck) <= 1:
            #print("New High has formed on last trading day ({}) for {}, adding to screening list".format( idx,self.yticker ))

            darvas_screening_dict['Date'] = _date
            darvas_screening_dict['Day'] = 0
            darvas_screening_dict['Status'] = 'Screening'
            darvas_screening_dict['Market_ticker'] = self.yticker
            darvas_screening_dict['NewHigh_Date'] = idx.strftime('%Y-%m-%d')
            darvas_screening_dict['NewHigh_closeprice'] = round(df_darvasCheck['Close'].iloc[0],2)
            darvas_screening_dict['Current_closeprice'] = round(df_darvasCheck['Close'].iloc[0],2)
            darvas_screening_dict['NewHigh_highprice'] = round(df_darvasCheck['High'].iloc[0],2)
            darvas_screening_dict['NewHigh_volume'] = df_darvasCheck['Volume'].iloc[0]
            darvas_screening_dict['buyPrice'] = round(df_darvasCheck['High'].iloc[0]*1.035,2)
            darvas_screening_dict['stoploss_changes'] = round(df_darvasCheck['Low'].iloc[0]*0.975,2)
            darvas_screening_dict['Low_price_stoploss_date'] = None
            # darvas_screening_dict['Hypthetical_buy_date'] = self.sHypo_df.loc[self.sHypo_df.Buy_Signal == 1]['Date'].iloc[-1]
            # darvas_screening_dict['Hypthetical_sell_date'] = self.sHypo_df.loc[self.sHypo_df.Sell_Signal == -1]['Date'].iloc[-1]
            darvas_screening_dict['DBox'] = False
            #print(darvas_screening_dict)

        darvas_list.append(darvas_screening_dict)

        return darvas_screening_dict
    

    # def Backtesting():

        
        

    #         # ema_plot = [mpf.make_addplot(round(df_darvasCheck['High'].iloc[0],2), color = 'red'), mpf.make_addplot(round(df_darvasCheck['Low'].iloc[0]*0.95,2), color = 'red' )
    #         #             , mpf.make_addplot(idx, color = 'red')]
    #         #mpf.plot(self.adf.iloc[-10:].set_index('Date'), type = 'candle',volume = True, addplot= ema_plot ) 


            





    #     # else:
    #     #     try:
    #     #         #self.logic_darvasbox(df_darvasCheck['High'].iloc[2:])


    











        

        
