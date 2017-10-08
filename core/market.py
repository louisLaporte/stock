#!/usr/bin/env python3
import bs4
import quandl
import pandas as pd
import requests

with open('secret/quandl_key', 'r') as f:
    api_key = f.readline().replace('\n', '')
quandl.ApiConfig.api_key = api_key


def get_ticker_stocks(ticker, start, end):
    """
    Get stocks for the given ticker from start date to end date

    :param ticker: ticker name
    :type ticker: str
    :param start: first date for stocks
    :type start: str
    :param end: last date for stocks
    :type end: str
    :return: ticker stocks between start and end
    :rtype: pandas.DataFrame
    """
    return pd.DataFrame(quandl.get_table('WIKI/PRICES',
                                         ticker=ticker,
                                         date={'gte': start, 'lte': end}))


def get_sp500_tickers():
    """
    Retrieve S&P500's tickers info from wikipedia

    :return: Array of tickers
    :rtype: pandas.DataFrame
    """
    resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    resp.raise_for_status()
    soup = bs4.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    tickers = []
    header = ["Ticker", "Security Name", "GICS Sector", "GICS Subsector",
              "HQ Address", "Date Added", "CIK"]

    for row in table.findAll('tr')[1:]:
        ticker = [h.text for h in row.findAll('td') if h.text != 'reports']
        tickers.append(ticker)

    return pd.DataFrame(tickers, columns=header)


def save_sp500_tickers(fname="sp500.csv"):
    """
    Save S&P500's tickers info

    :param fname: File to store info
    :type fname: str
    """
    if not fname:
        raise ValueError("File name is empty.")
    tickers = get_sp500_tickers()
    tickers.to_csv(fname, header=tickers.columns.values.tolist(), index=False)
