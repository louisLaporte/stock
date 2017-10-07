#!/usr/bin/env python3
import urllib.request
from bs4 import BeautifulSoup
import quandl
import pandas as pd

with open('secret/quandl_key', 'r') as f:
    api_key = f.readline().replace('\n', '')
quandl.ApiConfig.api_key = api_key


def get_ticker_stocks(ticker, start, end):
    """
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
    List of the S&P500 companies from Wikipedia
    :return: S&P500 by sectors
    :rtype: dict
    """
    site = "http://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    req = urllib.request.Request(site)
    req.add_header('User-Agent', 'Mozilla/5.0')
    page = urllib.request.urlopen(req)
    soup = BeautifulSoup(page, "lxml")

    table = soup.find('table', {'class': 'wikitable sortable'})
    sector_tickers = dict()
    for row in table.findAll('tr'):
        col = row.findAll('td')
        if len(col) > 0:
            sector = str(col[3].string.strip()).lower().replace(' ', '_')
            ticker = str(col[0].string.strip())
            if sector not in sector_tickers:
                sector_tickers[sector] = list()
            sector_tickers[sector].append(ticker)
    return sector_tickers
