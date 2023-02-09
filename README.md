# aistockscreener

Extract stock sentiments from financial news headlines in FinViz website using Python


FinViz is definitely one of my favourite go-to websites for information on the stock market. From fundamental ratios, technical indicators to news headlines and insider training data, it is a perfect stock screener. Furthermore, it has updated information on the performance of each sector, industry and any major stock index.


News Section in FinViz page for ‘AMZN’ stock ticker
Instead of having to go through each headline for every stock you are interested in, we can use Python to parse this website data and perform sentiment analysis (i.e. assign a sentiment score) for each headline before averaging it over a period of time.

The idea is that the averaged value may give valuable information for the overall sentiment of a stock for a given day (or week if you decide to average over a week’s news). 
