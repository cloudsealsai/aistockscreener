import pandas as pd
import mplfinance as mpf
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import os
import matplotlib.pyplot as plt
from PyPDF2 import PdfFileMerger, PdfFileReader, PdfFileWriter
from io import BytesIO
import matplotlib.pyplot as plt

import time

class utils():

    def __init__(self):
        self.alltimehigh_link = "https://in.tradingview.com/markets/stocks-india/market-movers-ath/"

    def strconvert(self,row):
        try:
            if (row == '—%') or (row == '—'):
                row = 0.0
            elif '%' in row:
                row = float(row.strip('%'))
            else:
                row = float(row)
        except:
            row = 0.0
        return row

    def getAllTimeHighSnap_NSE_BSE(self):

        reqweb = requests.get(self.alltimehigh_link)
        #print('Connection Status : {}'.format(reqweb))
        src = reqweb.content
        soup = BeautifulSoup(src, 'lxml')
        allth = soup.find("table", attrs = {"class":"table-DR3mi0GH"})

        t_headers = ['ticker', 'Price', 'CHG%', 'CHG', 'Rating', 'Vol', 'MKT CAP', 'P/E', 'EPS TTM']

        table_data = []
        for tr in allth.tbody.find_all("tr"):
            t_row = {}
            t_row['Market_ticker'] = tr.find_all('a')[0].text
            for td,  th in zip(tr.find_all('td'),t_headers):
                #print(td)
                t_row[th] = td.text.replace('\n', ' ').strip() 
            table_data.append(t_row)

        daysnap = pd.DataFrame(table_data)
        daysnap['fTicker'] = daysnap.apply(lambda x: re.sub(r'(?:^| )\w(?:$| )', ' ',x.ticker.replace('\t', ' ')).strip(), axis = 1)
        daysnap['tTicker'] =  daysnap.apply(lambda x: x.fTicker.split(' ')[0], axis =1)
        daysnap['Date'] = datetime.now ()

        daysnap_f = daysnap[['Date','Market_ticker', 'tTicker', 'Price', 'CHG%', 'CHG', 'Rating', 'Vol', 'MKT CAP', 'P/E','EPS TTM']].copy()
        daysnap_f['Price'] = daysnap.apply(lambda x: float(x['Price'].split('INR')[0]), axis =1)
        daysnap_f['CHG%'] = daysnap_f.apply(lambda x: self.strconvert(x['CHG%']), axis=1)
        daysnap_f.sort_values(by = ['CHG%'], ascending = False, inplace = True)
            
        sorted_ATH = daysnap_f.sort_values(by = ['CHG%'], ascending = False)#.to_csv(os.path.join(path, 'TV_Snap_{vd:%Y_%m_%d_%H_%M}.csv'.format(vd = datetime.today())), index=False)
        
        return sorted_ATH

    def trend(self, x):
        if x > -0.5 and x <= 0.5:
            return "Slight or No change"
        elif x > 0.5 and x <= 1:
            return "Slight Positive"
        elif x > -1 and x <= -0.5:
            return "Slight Negative"
        elif x > 1 and x <= 3:
            return "Positive"
        elif x > -3 and x <= -1:
            return "Negative"
        elif x > 3 and x <= 7:
            return "Among top gainers"
        elif x > -7 and x <= -3:
            return "Among top losers"
        elif x > 7:
            return "Bull run"
        elif x <= -7:
            return "Bear drop"





    def create_pdf(self,texts, plots, filename):
        # Create a PDF writer object
        pdf_writer = PdfFileWriter()
        print(texts)
        # Loop through the texts and add them to the PDF
        for text in texts:
            print(text)
            pdf_writer.add_page(text)
        
        # Loop through the plots and add them to the PDF
        for plot in plots:
            # Create a BytesIO object to hold the plot
            plot_buffer = BytesIO()
            plt.savefig(plot_buffer, format='pdf')
            plt.close()
            
            # Add the plot to the PDF
            pdf_writer.addPage(PdfFileReader(BytesIO(plot_buffer.getvalue())).getPage(0))
        
        # Save the PDF file
        with open(filename, 'wb') as f:
            pdf_writer.write(f)
