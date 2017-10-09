#!/usr/bin/env python3
import bs4
import quandl
import pandas as pd
import numpy as np
import requests
import urllib
import ssl
import re
import os
import logging


class SP500:

    def __init__(self, store_file):
        """
        Construtor for SP500

        Retrieve S&P500's tickers info from wikipedia
        """
        self._load_quandl_api_key()
        if not os.path.exists(store_file):
            self.tickers_store = pd.HDFStore(store_file)
        else:
            self.tickers_store = pd.HDFStore(store_file, mode='r+')
        print(self.tickers_store.keys())

        if '/default' not in self.tickers_store.keys():
            self.save_default_info()
        if '/website' not in self.tickers_store.keys():
            self.save_websites()
        if '/social' not in self.tickers_store.keys():
            self.save_social_accounts()

    def __exit__(self):
        self.tickers_store.close()

    @staticmethod
    def _load_quandl_api_key():
        with open('secret/quandl_key', 'r') as f:
            api_key = f.readline().replace('\n', '')
        quandl.ApiConfig.api_key = api_key

    def save_default_info(self):
        # Find S&P500 info from wikipedia
        tickers = []
        wikipedia = []
        wikipedia_url = 'http://en.wikipedia.org'

        resp = requests.get(wikipedia_url + '/wiki/List_of_S%26P_500_companies')
        resp.raise_for_status()
        soup = bs4.BeautifulSoup(resp.text, 'lxml')
        table = soup.find('table', {'class': 'wikitable sortable'})
        header = ["symbol", "security_name", "gcis_sector", "gcis_subsector",
                  "hq_address", "date_added", "cik"]
        wikipedia_header = ["symbol", "link"]
        for row in table.findAll('tr')[1:]:
            cells = row.findAll('td')
            ticker = [h.text for h in cells if h.text != 'reports']
            tickers.append(ticker)
            wiki = [cells[0].text, wikipedia_url + cells[1].a.get('href')]
            wikipedia.append(wiki)

        wikipedia_df = pd.DataFrame(wikipedia, columns=wikipedia_header)
        tickers_df = pd.DataFrame(tickers, columns=header)
        self.tickers_store['default'] = tickers_df
        self.tickers_store['wikipedia'] = wikipedia_df

    def save_websites(self):
        wiki_df = self.tickers_store['wikipedia']
        header = ["symbol", "link"]
        websites = []
        error_symbol = []
        for idx, row in wiki_df.iterrows():
            resp = requests.get(row['link'])
            soup = bs4.BeautifulSoup(resp.text, 'lxml')
            table = soup.find('table', {'class': 'infobox'})
            try:
                for r in table.findAll('tr')[1:]:
                    if hasattr(r.th, 'text'):
                        if r.th.text == 'Website':
                            website = r.td.a.get('href')
                            break
            except AttributeError:
                error_symbol.append(row['symbol'])
                continue
            else:
                if website.startswith('//'):
                    website = 'http:' + website
            print(row['symbol'], website)
            websites.append([row['symbol'], website])
        website_df = pd.DataFrame(websites, columns=header)
        self.tickers_store['website'] = website_df
        print("Website error for symbols: {}".format(error_symbol))

    def update_data(self):
        return

    def get_website(self, symbol):
        return

    def save_social_accounts(self):
        website_df = self.tickers_store['website']
        header = ["symbol", "twitter_account"]
        accounts = []
        error_symbol = []
        for idx, row in website_df.iterrows():
            print(row['link'])
            if row['link'] in ["http://www.carmax.com/", "http://www.cinfin.com",
                               "http://www.humana.com/", "http://www.kohls.com/",
                               "http://michaelkors.com", "http://www.bestbuy.com/",
                               "http://www.footlocker.com", "http://www.oreillyauto.com"]:
                continue
            try:
                # req = urllib.request.Request(
                #     website,
                # soup = bs4.BeautifulSoup(
                #     urllib.request.urlopen(req,
                #                            context=ssl.create_default_context(
                #                                ssl.Purpose.CLIENT_AUTH)),
                #     'lxml')
                headers = {'User-Agent': "Mozilla/5.0 (Windows NT 6.1) \
                AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"}
                resp = requests.get(row['link'], verify=True, headers=headers)
                resp.raise_for_status()
                soup = bs4.BeautifulSoup(resp.text, 'lxml')

                social = soup.select("a[href*=twitter]")  # .a.get('href')
                for s in social:
                    m = re.match('.*twitter.com/(#!/)?(@)?\w+$', s.get('href'))
                    if m:
                        account = s.get('href').split('/')[-1]
                        print(row['symbol'], account)
                        accounts.append([row['symbol'], account])
                        break
            except Exception as err:
                print(err)
                error_symbol.append(row['symbol'])
                continue
        social_df = pd.DataFrame(accounts, columns=header)
        self.tickers_store['social'] = social_df
        print("Website error for symbols: {}".format(error_symbol))

    def get_sectors(self):
        """
        Get list of sectors

        :return: list of unique sectors
        :rtype: list
        """
        return self.tickers["GICS Sector"].unique().tolist()

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
        return self.tickers[self.tickers["GICS Sector"].isin(sectors)]

    def get_tickers_symbol(self):
        """
        Get list of tickers symbol

        :return: list of unique sectors
        :rtype: list
        """
        return self.tickers["Symbol"].tolist()

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
        self.tickers.to_csv(fname, header=self.df.columns.values.tolist(), index=False)
