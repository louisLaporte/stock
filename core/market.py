#!/usr/bin/env python3
import bs4
import quandl
import pandas as pd
import requests


class SP500:

    def __init__(self):
        """
        Construtor for SP500

        Retrieve S&P500's tickers info from wikipedia
        """
        with open('secret/quandl_key', 'r') as f:
            api_key = f.readline().replace('\n', '')
        quandl.ApiConfig.api_key = api_key
        resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
        resp.raise_for_status()
        soup = bs4.BeautifulSoup(resp.text, 'lxml')
        table = soup.find('table', {'class': 'wikitable sortable'})
        tickers = []
        header = ["Symbol", "Security Name", "GICS Sector", "GICS Subsector",
                  "HQ Address", "Date Added", "CIK"]

        for row in table.findAll('tr')[1:]:
            ticker = [h.text for h in row.findAll('td') if h.text != 'reports']
            tickers.append(ticker)

        self.df = pd.DataFrame(tickers, columns=header)

    def get_sectors(self):
        """
        Get list of sectors

        :return: list of unique sectors
        :rtype: list
        """
        return self.df["GICS Sector"].unique().tolist()

    def get_tickers_by_sectors(self, sectors):
        """
        Get tickers table by sectors

        :param sectors: GCIS sectors
        :type sectors: list
        :return: a table of tickers by selected sectors
        :rtype: pandas.DataFrame
        """
        if not isinstance(sectors, list):
            raise TypeError("Sectors must be a list")
        if len(set(sectors) & set(self.get_sectors())) != len(sectors):
            raise ValueError("Unknown sectors: {}".format(sectors))
        return self.df[self.df["GICS Sector"].isin(sectors)]

    def get_tickers_symbol(self):
        """
        Get list of tickers symbol

        :return: list of unique sectors
        :rtype: list
        """
        return self.df["Symbol"].tolist()

    @staticmethod
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

    def save_sp500_tickers(self, fname="sp500.csv"):
        """
        Save S&P500's tickers info

        :param fname: File to store info
        :type fname: str
        """
        if not fname:
            raise ValueError("File name is empty.")
        self.df.to_csv(fname, header=self.df.columns.values.tolist(), index=False)
