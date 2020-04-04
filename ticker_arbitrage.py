############################################################
# Options Arbitrage Calculator - ticker_arbitrage.py
############################################################
#
# Author: Andrew Joseph Millward
#
############################################################
# Imports
############################################################

import urllib.request, requests, concurrent.futures, yfinance, bs4
from yahoo_fin import stock_info
from yahoo_fin import options
from selenium import webdriver
from bs4 import BeautifulSoup

############################################################
# Global Variables
############################################################

max_price = False

############################################################
# Functions
############################################################

def ticker_arbitrage(index):
    """
    Call to calculate option quotes for a single stock ticker.
    @params:
        index       - Required  : NASDAQ stock symbol (Str)
    """
    index = index.replace(".","-")
    url = 'https://finance.yahoo.com/quote/' + str(index) + '/options'
        
    try:
        # Specialized local import
        from bs4 import BeautifulSoup as soup
        
        # Create a request to the given URL and store data.
        request = requests.get(url)
        data = request.text
        soup = soup(data, "html.parser")
        table_calls = soup.findAll("table")
        table_calls = table_calls[0]
        table_puts = soup.findAll("table")
        table_puts = table_puts[1]
        try:
            date = yfinance.Ticker(index).options[0]
        except IndexError:
            print("Ticker: " + index + " -> does not appear to have any valid dates. Adding to exclusion list. It is possible that this ticker is valid, but due to network constraints, the data cannot be retrieved at this time.")
            exclusion_list = open("ignore_symbol.txt", "a")
            exclusion_list.write(index+"\n")
            exclusion_list.close()
            return( -1 ) # Failure
            
        # Gather all call body data points and write them to list of lists.
        rows = table_calls.tbody.findAll("tr")
        call_contents_array = []
        for i in range(len(rows)):
            call_contents = rows[i].findAll("td")
            for j in range(len(call_contents)):
                call_contents[j] = (call_contents[j].text)
            call_contents_array.append(call_contents)

        # Gather all put body data points and write them to list of lists.
        rows = table_puts.tbody.findAll("tr")
        put_contents_array = []
        for i in range(len(rows)):
            put_contents = rows[i].findAll("td")
            for j in range(len(put_contents)):
                put_contents[j] = (put_contents[j].text)
            put_contents_array.append(put_contents)

        price = float(stock_info.get_live_price(index))
        max_combo = [0, 0, 0, 0, 0, "NaN", "NaN"]
        for call in call_contents_array:
            for put in put_contents_array:
                vol_call = int(call[8].replace(",", "").replace("-","0"))
                vol_put = int(put[8].replace(",", "").replace("-","0"))
                if vol_call >= 0 and vol_put >= 0:
                    if max_price:
                        premium_col = 5
                    else:
                        premium_col = 3
                    call_premium = float(call[premium_col].replace(",", "").replace("-","0"))*100
                    call_strike = float(call[2].replace(",", "").replace("-","0"))
                    put_premium = float(put[premium_col].replace(",", "").replace("-","0"))*100
                    put_strike = float(put[2].replace(",", "").replace("-","0"))
                    dif_call = max(0, price-call_strike)
                    dif_put = max(0, put_strike-price)
                    if (call_premium+put_premium) > 0 and call_premium >= 20 and put_premium >= 20:
                        pl = ((dif_call+dif_put)-(call_premium+put_premium))/(call_premium+put_premium)
                        if pl > max_combo[0]:
                            max_combo = [pl, call_premium, call_strike, put_premium, put_strike, index, date]

        if max_combo[5] != "NaN":
            print("""\n__________________________________________________________\n""" +
                  """|Arbitrage opportunity found with the following structure:\n""" +
                  """|                                                         \n""" +
                  """|  Symbol: """ + max_combo[5] + """                       \n""" +
                  """|  Call: $""" + str(max_combo[1]) + """ @ $""" + str(max_combo[2]) + """\n""" +
                  """|  Put: $""" + str(max_combo[3]) + """ @ $""" + str(max_combo[4]) + """\n""" +
                  """|  Expiration: """ + str(date) + """                      \n""" +
                  """|                                                         \n""" +
                  """|_________________________________________________________""")
            found = True

    # Exception handling for various cases of use.
    except requests.exceptions.ConnectionError:
        print("Make sure you are using a valid URL.")
        return ( -1 ) # Failure

############################################################
# Operational Code
############################################################

if __name__ == "__main__":
    """
    Allows a user to enter a list of stocks of interest in
    user_check_symbols.txt and automatically check each
    stock while ignoring other stocks in S&P 500 and
    NASDAQ.
    """

    tickers = open("user_check_symbols.txt", "r")
    tickers = tickers.read().splitlines()

    try:
        found = False
        with concurrent.futures.ThreadPoolExecutor(max_workers=None) as executor:
            executor.map(ticker_arbitrage, tickers)

        if found == False:
            print("No suitable arbitrage opportunities were found at this time.")
    except:
        print("An unknown error occurred. Exiting...")