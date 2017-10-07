#!/usr/bin/env python3
import urllib.request
from bs4 import BeautifulSoup

SITE = "http://en.wikipedia.org/wiki/List_of_S%26P_500_companies"


def scrape_list(site):
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


print(scrape_list(SITE))
