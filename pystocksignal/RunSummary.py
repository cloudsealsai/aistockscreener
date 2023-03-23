import yfinance as yf
import plotly.offline as py
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import mplfinance as mpf
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, date
import re
import os,sys
#import schedule
import time
import PyPDF2
sys.path.append(r'C:\Users\CLOUDSEALS\Python\Dev\Stock Screener\pystocksignals')
from Signals import Signals
from utils import utils
from FundamentalAnalysis import FundamentalAnalysis
from TechnicalAnalysis import TechnicalAnalysis

class RunSummary():
    
    def __init__(self, ticker = None) -> None:
        #s = Signals(ticker)
        #self.stock_pdata = s.getStockData()
        self.s = Signals()
        self.u = utils()
        if ticker is None:
            df = self.DarvasScreening()

            path = os.path.join(os.getcwd(), 'EOD\Monitor\DBOX')

            if not os.path.exists(path):
                os.makedirs(path)
            
            

            df.to_excel(os.path.join(path, 'ATH_BOX_{}.xlsx'.format(datetime.strftime(date.today(), '%Y%m%d'))))
            #df.to_pickle(os.path.join(path, 'pickle\ATH_BOX_{}.pkl'.format(datetime.strftime(date.today(), '%Y%m%d'))))

            files = os.listdir(path)

            if files:
                dbox_daily = []
                for f in files:
                    #print(os.path.join(path,f))
                    dbox_daily_df = pd.read_excel(os.path.join(path,f))
                    dbox_daily.append(dbox_daily_df)
                _df = pd.concat(dbox_daily)
                #print(_df)
                df = self.DarvasScreening(_df)
                df.to_excel(os.path.join(path, 'Combined_ATH_BOX_{}.xlsx'.format(datetime.strftime(date.today(), '%Y%m%d'))))
                


        if not df.empty:
            df_box = df.loc[df.DBox == True]

            if not df_box.empty:
                
                for tkr in df_box.Market_ticker.unique():
                # # Run Stock price Analysis
                    sg = Signals(tkr)
                    sg.getStockData()
                    tsug = TechnicalAnalysis(tkr).suggest_trade()
                    sg.stockAnalysis()
                    sg.signal_hypothetical()

                



       

       
        
        # #s.DarvasScreening()
        # 
        
        # #fsug = FundamentalAnalysis(ticker).suggest_buy_sell()
        # tsug = TechnicalAnalysis(ticker).suggest_trade()
        # 


        # # # Fundamental Analsysis


        # # # signals generator

        # #     # Hypothetical signal
        # 

        # #     #Darvas checks

        # 


    def DarvasScreening(self, df = pd.DataFrame()):
        
        if df.empty:
            #print('1')
            self._allTH = self.u.getAllTimeHighSnap_NSE_BSE()
        else:
            self._allTH = df
        
        darvas_list = []
        for t in self._allTH.Market_ticker.unique():
            #print(t)
            df = self.s.getStockData(t)

            if not df.empty:
                darvas_list.append(self.s.logic_darvasbox(df))

        

        return pd.DataFrame(darvas_list)
    
    def generate_pdf(self):
        # Create a new PDF file
        pdf_file = open('example.pdf', 'wb')
        pdf_writer = PyPDF2.PdfFileWriter()

        # Create a Matplotlib figure and add a plot
        fig = plt.figure()
        ax = fig.add_subplot(111)
        x = [1, 2, 3, 4, 5]
        y = [2, 3, 5, 4, 6]
        ax.plot(x, y)

        # Convert the Matplotlib figure to a PNG image and add it to the PDF
        fig.savefig('graph.png')
        with open('graph.png', 'rb') as img:
            img_obj = PyPDF2.pdf.ImageReader(img)
            page = PyPDF2.pdf.PageObject.createBlankPage(None, img_obj.getSize()[0], img_obj.getSize()[1])
            page.addImage(img_obj, 0, 0)
            pdf_writer.addPage(page)

        # Add some text to the PDF
        page = PyPDF2.pdf.PageObject.createBlankPage(None, 612, 792) # 8.5 x 11 inches (US Letter)
        page.compressContentStreams()
        page.addText("Example text added to PDF file", 100, 600)

        # Add the page with the text to the PDF
        pdf_writer.addPage(page)

        # Write the updated PDF file to disk
        pdf_writer.write(pdf_file)
        pdf_file.close()


        

        


    





        
        # print(tout)
        # fname = '{}_sample.pdf'.format(ticker)
        # u.create_pdf(tout,[],fname)


        #print(fsug)


        # s.stockAnalysis()
        # s.signal_hypothetical()
        # s.signal_DarvasBox()