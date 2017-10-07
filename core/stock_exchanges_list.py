import pandas as pd
import os


def get_list():
    list_path = os.path.expanduser('~/Desktop/XTrader/Data/0 - General/CSV/')
    os.chdir(list_path)
    exchange_list = ['nyse', 'nasdaq', 'amex']
    pd_all = pd.DataFrame([])
    for item in exchange_list:
        url = "http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=%s&render=download" % item
        print(url)
        df = pd.DataFrame.from_csv(url)
        df.insert(7, "Exchange", '%s' % item)
        filename_exchanges = "%s.csv" % (item)
        if os.path.isfile(filename_exchanges):
            os.remove(filename_exchanges)
        df.to_csv(filename_exchanges)
        pd_all = pd_all.append(df)
    filename_all = "all.csv"
    if os.path.isfile(filename_all):
        os.remove(filename_all)
    pd_all.to_csv("all.csv")

get_list()