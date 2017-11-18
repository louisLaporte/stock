#!/usr/bin/env python3
import bs4
import quandl
import pandas as pd
import numpy as np
import requests
import os
import json
import shutil
import tempfile
import re
import multiprocessing as mp
from scrapy.selector import Selector
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
ch = logging.StreamHandler()
formatter = logging.Formatter('[%(name)s][%(levelname)s] %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__) + '/..')
pd.set_option('display.width', os.get_terminal_size().columns)
# pd.set_option('display.colheader_justify', 'left')


class SP500:

    def __init__(self, store_file=''):
        """
        Construtor for SP500

        Retrieve S&P500's tickers info from wikipedia. During the process data
        will be handle in a temporary file.

        :param store_file: file containing the stored tables
        :type store_file: str
        """
        self._load_quandl_api_key()
        self.store_file = PROJECT_PATH + '/dataset/sp500.h5'
        self.tmp_store = tempfile.NamedTemporaryFile(delete=True, suffix='.h5')
        log.debug("Creating store {}".format(self.tmp_store.name))

        if not os.path.exists(self.store_file):
            self.store = pd.HDFStore(self.tmp_store.name)
            self.update_store()
        else:
            shutil.copyfile(self.store_file, self.tmp_store.name)
            self.store = pd.HDFStore(self.tmp_store.name)

    def __del__(self):
        log.debug("Moving {} to {}".format(self.tmp_store.name, self.store_file))
        if not os.path.exists(self.store_file):
            os.mknod(self.store_file)
        try:
            shutil.copyfile(self.tmp_store.name, self.store_file)
        except NameError:
            pass
        self.tmp_store.close()

    @staticmethod
    def _load_quandl_api_key():
        with open(PROJECT_PATH + '/secret/quandl_key.json', 'r') as f:
            api_key = json.load(f)
        quandl.ApiConfig.api_key = api_key['key']

    def _normalize_table_name(self, table):
        if not table.startswith("/"):
            table = "/" + table
        return table

    def parallelize(self, callback, tname):
        """
        Parallelize tasks to update table.

        The callback must have 2 argument (list of dataframes, queue of return
        values.

        :param callback: callback method
        :param tname: table name
        :type table: str
        :return: queued result
        :rtype: list
        """
        ret = []
        ret_queue = mp.Queue()
        cpu_count = mp.cpu_count() * 2
        df_list = np.array_split(self.store[tname], cpu_count)
        proc = []
        for i in range(cpu_count):
            p = mp.Process(target=callback, args=(df_list[i], ret_queue))
            log.info("Starting process {}".format(p))
            proc.append(p)
            p.start()
        # Gather results
        for i in range(cpu_count):
            ret.append(ret_queue.get())
            log.info("Joining process {}".format(p))
            proc[i].join()
        return ret

    def get_store_tables(self):
        """
        Get tables name in store

        :return: tables name
        :rtype: list
        """
        return self.store.keys()

    def remove_table(self, table):
        raise NotImplementedError

    def get_table(self, table):
        """
        Get table from store

        :param table: table name
        :type table: str
        :return: table info
        :rtype: pandas.DataFrame
        """
        return self.store.get(table).sort_index()

    def get_table_header(self, table):
        """
        Get table from store

        :param table: table name
        :type table: str
        :return: table header
        :rtype: list
        """
        return self.get_table(table).columns.values.tolist()

    def update_table(self, tname):
        if tname == 'info':
            self.update_info()
        elif tname == 'web':
            self.update_websites()
            self.update_social_accounts()
        else:
            raise KeyError("Table {} not found".format(tname))

    def update_store(self):
        """
        Update all tables informations
        """
        self.update_info()
        self.update_websites()
        self.update_social_accounts()

    def _request(self, url, res_type='bs4'):
        headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1) \
                           AppleWebKit/537.36 (KHTML, like Gecko) \
                           Chrome/41.0.2228.0 Safari/537.36"
        }
        try:
            resp = requests.get(url, verify=True, headers=headers, timeout=15)
            resp.raise_for_status()
            if res_type == 'bs4':
                return bs4.BeautifulSoup(resp.text, 'lxml')
            elif res_type == 'selector':
                return Selector(text=resp.text, type='html')
            else:
                log.error('Not a valid response type')
                return
        except Exception as err:
            log.error(err)
            return

    def update_info(self, condition=None):
        # Find S&P500 info from wikipedia
        companies = []
        wikipedia = []
        wikipedia_url = 'http://en.wikipedia.org'

        resp = self._request(wikipedia_url + '/wiki/List_of_S%26P_500_companies')
        table = resp.find('table', {'class': 'wikitable sortable'})
        headers = {
            "companies": [
                "symbol", "security_name", "gcis_sector", "gcis_subsector",
                "hq_address", "date_added", "cik"
            ],
            "wikipedia": ["symbol", "wikipedia"]
        }

        for row in table.findAll('tr')[1:]:
            cells = row.findAll('td')
            company = [h.text for h in cells if h.text != 'reports']
            companies.append(company)
            # [ticker symbol, wikipedia url]
            wiki = [cells[0].text, wikipedia_url + cells[1].a.get('href')]
            wikipedia.append(wiki)

        self.store['info'] = pd.DataFrame(companies, columns=headers["companies"])
        self.store['web'] = pd.DataFrame(wikipedia, columns=headers["wikipedia"])
        log.info("Info updated.")

    def get_website(self, symbol):
        """
        Get ticker's website

        :param symbol: ticker symbol
        :type symbol: str
        :return: website for the given symbol
        :rtype: str
        """
        tsw = self.store['web']
        return tsw[tsw['symbol'] == symbol].loc[0]["website"]

    def update_websites(self):
        """
        Save websites url in hdf5 database
        """
        def web_worker(df, ret_queue):
            websites = []
            for _, row in df.iterrows():
                resp = self._request(row['wikipedia'])
                if not resp:
                    websites.append(np.NaN)
                    log.error("No website found for {}".format(row['symbol']))
                    continue
                table = resp.find('table', {'class': 'infobox'})
                for r in table.findAll('tr')[1:]:
                    if hasattr(r.th, 'text'):
                        if r.th.text == 'Website':
                            website = r.td.a.get('href')
                            break
                else:
                    website = np.NaN
                # Clean up url
                if website.startswith('//'):
                    website = 'http:' + website
                # NOTE: don't remove after last /, the full url is needed
                # website = "/".join(website.split('/')[:3])
                websites.append(website)
                log.info("{:<4} {}".format(row['symbol'], website))
            ret_queue.put(df.assign(website=websites))

        self.store['web'] = pd.concat(self.parallelize(web_worker, 'web'))

    def get_row(self, regex=None, ignorecase=False):
        df = None
        tables = [self.store[table] for table in self.store.keys()]
        df = pd.merge(*tables, how='outer', on=['symbol'])
        if ignorecase:
            r = re.compile(r"{}".format(regex), re.IGNORECASE)
        else:
            r = re.compile(r"{}".format(regex))
        if regex:
            df = df.astype(str)
            return df[
                df.apply(
                    lambda x: bool([v for v in x.values if r.search(v)]),
                    axis=1)
            ]
        return df

    def get_social_account(self, symbol, social_name):
        tsw = self.store['social']
        return tsw[tsw['symbol'] == symbol].loc[0]["twitter_account"]

    def update_social_accounts(self):
        """
        Save social accounts names in hdf5 database
        """
        def social_worker(df, ret_queue):
            accounts = {"twitter": []}
            for _, row in df.iterrows():
                resp = self._request(row['website'], res_type='selector')
                if not resp:
                    log.error("No response")
                    accounts["twitter"].append(np.NaN)
                    continue
                try:
                    twitter_account = resp.xpath(
                        '//a[re:test(@href, ".*twitter.com/(#!/)?(@)?\w+$")]//@href'
                    )
                    twitter_account = twitter_account.extract_first()
                    if twitter_account:
                        accounts["twitter"].append(twitter_account)
                        log.info("{:<4} {}".format(row['symbol'], twitter_account))
                    else:
                        accounts["twitter"].append(np.NaN)
                        log.error("No social account found for {}".format(row['symbol']))
                except Exception as err:
                    accounts["twitter"].append(np.NaN)
                    log.error(err)
                    log.error("No social account found for {}".format(row['symbol']))
                    continue
            ret_queue.put(df.assign(twitter=accounts["twitter"]))

        self.store['web'] = pd.concat(self.parallelize(social_worker, 'web'))

    def get_sectors(self):
        """
        Get list of sectors

        :return: list of unique sectors
        :rtype: list
        """
        return self.store['info']["gcis_sector"].unique().tolist()

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

        tst = self.store['info']
        return tst[tst["gcis_sector"].isin(sectors)]

    def get_tickers_symbol(self):
        """
        Get list of tickers symbol

        :return: list of unique sectors
        :rtype: list
        """
        return self.store["info"]["symbol"].tolist()

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
