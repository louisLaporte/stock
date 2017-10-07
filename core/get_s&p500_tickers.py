import bs4 as bs
import pandas as pd
import requests
import os


def save_sp500_tickers():

    resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class':'wikitable sortable'})
    tickers = []
    tickers_list = []
    headers = ["Ticker", "Security Name", "GICS Sector", "GICS Subsector", "HQ Address", "Date Added"]

    for row in table.findAll('tr')[1:]:
        ticker_symbol  = row.findAll('td')[0].text
        security_name  = row.findAll('td')[1].text
        gics_sector    = row.findAll('td')[3].text
        gics_subsector = row.findAll('td')[4].text
        address_of_hq  = row.findAll('td')[5].text
        date_added     = row.findAll('td')[6].text

        ticker_row = [ticker_symbol, security_name, gics_sector, gics_subsector, address_of_hq, date_added]
        tickers.append(ticker_symbol)
        tickers_list.append(ticker_row)

    os.remove('S&P500.csv')

    df = pd.DataFrame(tickers_list)
    df.to_csv("S&P500.csv",header=headers, index=False)

    return tickers

save_sp500_tickers()
