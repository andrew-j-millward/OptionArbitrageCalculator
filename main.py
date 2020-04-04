############################################################
# Options Arbitrage Calculator - main.py
############################################################
#
# Author: Andrew Joseph Millward
#
############################################################
# Imports
############################################################

import collections, email, os, math, string, urllib.request 
import requests, concurrent.futures, ticker_arbitrage
from yahoo_fin import options
import bs4

############################################################
# Global Variables
############################################################

max_price = ticker_arbitrage.max_price

############################################################
# Functions
############################################################

def main(NASDAQ = False):
    """
    Refreshes list of either NASDAQ or S&P 500 tickers and
    outputs all non-excluded tickers to be searched.
    @params:
        NASDAQ       - Optional  : Use NASDAQ (T) or S&P 500 (F)
    """
    print('Refreshing list of stock tickers...')
    if NASDAQ:
        # NASDAQ URL
        url = 'http://ftp.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt'

        # Retrieve file.
        urllib.request.urlretrieve(url, 'nasdaqlisted.txt')
        print('Refresh completed successfully.\n')

        # Unpack all file entries.
        print('Deconstructing stock index data into list...')
        ticker_file = open('nasdaqlisted.txt', 'r')
        global tickers
        tickers = ticker_file.readlines()
        del[tickers[-1]]
        del[tickers[0]]
        for nasdaqticker_index in range(len(tickers)):
            tickers[nasdaqticker_index] = tickers[nasdaqticker_index].split('|')[0]
    else:
        # S&P 500 URL
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

        # Create a request to the given URL and store data.
        ticker_wiki = requests.get(url)
        soup = bs4.BeautifulSoup(ticker_wiki.text, 'lxml')
        table = soup.find('table', {'class': 'wikitable sortable'})

        # Gather all ticker information from table
        tickers = []
        for row in table.findAll('tr')[1:]:
            ticker = row.findAll('td')[0].text.replace("\n","")
            tickers.append(ticker)
    print('List construction completed successfully.\n')

    # Remove "ignored" tickers from search space.
    print('Beginning lookup procedure for each index...')
    threads = list()
    ignore_list = open("ignore_symbol.txt", "r")
    ignore_list = ignore_list.read().splitlines()
    tickers_reduced = []
    for i in tickers:
        if i not in ignore_list:
            tickers_reduced.append(str(i))
    tickers = tickers_reduced
    

############################################################
# Operational Code
############################################################

if __name__ == "__main__":
    """
    Runs multi-threaded workload of all tickers in S&P 500
    and looks for arbitrage opportunities.
    """
    main()
    found = False
    with concurrent.futures.ThreadPoolExecutor(max_workers=None) as executor:
        executor.map(ticker_arbitrage.ticker_arbitrage, tickers)
    if found == False:
        print("No suitable arbitrage opportunities were found at this time.")
else:
    """
    Runs single-thread workload of all tickers in S&P 500
    to reduce computing requirements and looks for
    arbitrage opportunities.
    """
    main()
    for ticker in tickers:
        ticker_arbitrage.ticker_arbitrage(ticker)