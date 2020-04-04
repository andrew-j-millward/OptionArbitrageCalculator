############################################################
# Options Arbitrage Calculator - ticker_refresh.py
############################################################
#
# Author: Andrew Joseph Millward
#
############################################################

############################################################
# Operational Code
############################################################

if __name__ == '__main__':
    """ Slowly refreshes all ticker data using a single
        thread. Forces exclusion list order to be
        alphabetical. Much slower than standard run.
    """
    print('Resetting ticker exclusion list...')
    ticker_file = open('ignore_symbol.txt', 'w')
    ticker_file.close()
    import main
    print('Reset completed.\n')