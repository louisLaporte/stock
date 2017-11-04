#!/usr/bin/env python3
import bs4
import quandl
import pandas as pd
import requests
import os
import json
import logging
from scrapy.selector import Selector

log = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(name)s][%(levelname)s]%(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)

store_file = os.path.realpath(os.path.dirname(__file__) + '/../dataset/sp500.h5')


class SP500:

    def __init__(self, store_file=store_file):
        """
        Construtor for SP500

        Retrieve S&P500's tickers info from wikipedia
        """
        self._load_quandl_api_key()
        if not os.path.exists(store_file):
            self.store = pd.HDFStore(store_file)
        else:
            self.store = pd.HDFStore(store_file, mode='r+')
        log.info(self.store.keys())
        log.info(self.store)

        if '/default' not in self.store.keys():
            self.save_default_info()
        if '/website' not in self.store.keys():
            self.save_websites()
        if '/social' not in self.store.keys():
            self.save_social_accounts()

    def __exit__(self):
        self.store.close()

    def get_store(self):
        """
        Get store tables

        :return: tables name
        :rtype: list
        """
        return self.store.keys()

    def get_table(self, table):
        """
        Get table from store

        :param table: table name
        :type table: str
        :return: table info
        :rtype: pandas.DataFrame
        """
        if not table.startswith("/"):
            table = "/" + table
        if table not in self.get_store():
            raise ValueError("Table {} not found".format(table))
        return self.store[table]

    def get_table_header(self, table):
        """
        Get table from store

        :param table: table name
        :type table: str
        :return: table header
        :rtype: list
        """
        return self.get_table(table).columns.values

    def update_store(self):
        raise NotImplementedError

    @staticmethod
    def _load_quandl_api_key():
        with open('../secret/quandl_key.json', 'r') as f:
            api_key = json.load(f)
        quandl.ApiConfig.api_key = api_key['key']

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
        self.store['default'] = tickers_df
        self.store['wikipedia'] = wikipedia_df

    def get_website(self, symbol):
        """
        Get ticker's website

        :param symbol: ticker symbol
        :type symbol: str
        :return: website for the given symbol
        :rtype: str
        """
        tsw = self.store['website']
        return tsw[tsw['symbol'] == symbol].loc[0]["link"]

    def update_websites(self):
        raise NotImplementedError

    def save_websites(self):
        """
        Save websites url in hdf5 database
        """
        wiki_df = self.store['wikipedia']
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
            log.debug(row['symbol'], website)
            websites.append([row['symbol'], website])
        website_df = pd.DataFrame(websites, columns=header)
        self.store['website'] = website_df
        log.debug("Website error for symbols: {}".format(error_symbol))

    def get_social_account(self, symbol, social_name):
        tsw = self.store['social']
        return tsw[tsw['symbol'] == symbol].loc[0]["twitter_account"]

    def update_social_accounts(self):
        raise NotImplementedError

    def save_social_accounts(self):
        """
        Save social accounts names in hdf5 database
        """
        website_df = self.store['website']
        header = ["symbol", "twitter_account"]
        accounts = []
        error_symbol = []
        for idx, row in website_df.iterrows():
            log.debug(row['link'])
            try:
                headers = {'User-Agent': "Mozilla/5.0 (Windows NT 6.1) \
                    AppleWebKit/537.36 (KHTML, like Gecko) \
                    Chrome/41.0.2228.0 Safari/537.36"}
                resp = requests.get(row['link'], verify=True, headers=headers, timeout=15)
                resp.raise_for_status()
                response = Selector(text=resp.text, type='html')
                account = response.xpath(
                    '//a[re:test(@href, ".*twitter.com/(#!/)?(@)?\w+$")]//@href'
                )
                account = account.extract_first()
                if account:
                    accounts.append(account)
            except Exception as err:
                log.debug(err)
                error_symbol.append(row['symbol'])
                continue
        log.debug(len(accounts))
        for account in accounts:
            log.debug(account)
        social_df = pd.DataFrame(accounts, columns=header)
        self.store['social'] = social_df
        log.debug("Website error for symbols: {}".format(error_symbol))

    def get_sectors(self):
        """
        Get list of sectors

        :return: list of unique sectors
        :rtype: list
        """
        return self.store['default']["gics_sector"].unique().tolist()

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
        tst = self.store['default']
        return tst[tst["gics_sector"].isin(sectors)]

    def get_tickers_symbol(self):
        """
        Get list of tickers symbol

        :return: list of unique sectors
        :rtype: list
        """
        return self.store["default"]["symbol"].tolist()

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
        return pd.DataFrame(
            quandl.get_table('WIKI/PRICES',
                             ticker=ticker,
                             date={'gte': start, 'lte': end})
        )
