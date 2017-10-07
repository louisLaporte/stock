import pandas as pd
import pandas_datareader as pdr
import os
from datetime import datetime


def get_historical(ticker):

    start_date = datetime(2000, 1, 1)
    end_date = datetime.now().date()
    filename = ticker + ".csv"
    ticker_string = "%s" % ticker
    ticker_data = pdr.get_data_yahoo(symbols=ticker_string, start=start_date, end=end_date)
    if os.path.isfile(filename):
        os.remove(filename)
    df = pd.DataFrame(ticker_data)
    df.to_csv(filename)
    return
