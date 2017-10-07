#!/usr/bin/env python3.4
from collections import OrderedDict
def getquote(symbol):

    import urllib.request
    import csv

    url = "http://www.finance.yahoo.com/d/quotes?s=" + symbol + \
    "&f=aa2a5bb2b3b4b6cc1c3c6c8dd1d2ee1e7e8e9f6ghjkg1g3g4g5g6ii5j1j3j4j5j6k1k2k"\
    "3k4k5ll1l2l3mm2m3m4m5m6m7m8nn4opp1p2p5p6qrr1r2r5r6r7ss1s7t1t6t7t8vv1v7ww1w4xy"
    response = urllib.request.urlopen(url)
    l = response.read().decode('utf-8')
    L = l.split(',')

    D = OrderedDict()
    D['ask']                                        = L[0]
    D['average daily volume']                       = L[1]
    D['ask size']                                   = L[2]
    D['bid']                                        = L[3]
    D['ask (realtime)']                             = L[4]
    D['bid (realtime)']                             = L[5]
    D['book value']                                 = L[6]
    D['bid size']                                   = L[7]
    D['change and % change']                        = L[8]
    D['change']                                     = L[9]
    D['commission']                                 = L[10]
    D['change (realtime)']                          = L[11]
    D['afterhours change (realtime)']               = L[12]
    D['dividend/share']                             = L[13]
    D['last trade date']                            = L[14]
    D['trade date']                                 = L[15]
    D['earning/share']                              = L[16]
    D['Error indicator']                            = L[17]
    D['eps (this year)']                            = L[18]
    D['eps (next year)']                            = L[19]
    D['eps (next quarter)']                         = L[20]
    D['float shares']                               = L[21]
    D['day low']                                    = L[22]
    D['day high']                                   = L[23]
    D['52 week low']                                = L[24]
    D['52 week high']                               = L[25]
    D['holdings gain percent']                      = L[26]
    D['annualized gain']                            = L[27]
    D['holdings gain']                              = L[28]
    D['holdings gain percent (realtime)']           = L[29]
    D['Holdings Gain (Real-time)']                  = L[30]
    D['More Info']                                  = L[31]
    D['Order Book (Real-time)']                     = L[32]
    D['Market Capitalization']                      = L[33]
    D['Market Cap (Real-time)	']                  = L[34]
    D['EBITDA']                                     = L[35]
    D['Change From 52-week Low']                    = L[36]
    D['Percent Change From 52-week Low']            = L[37]
    D['Last Trade (Real-time) With Time']           = L[38]
    D['Change Percent (Real-time)']                 = L[39]
    D['Last Trade Size']                            = L[40]
    D['Change From 52-week High']                   = L[41]
    D['Percebt Change From 52-week High']           = L[42]
    D['Last Trade (With Time)']                     = L[43]
    D['Last Trade (Price Only)']                    = L[44]
    D['High Limit']                                 = L[45]
    D['Low Limit']                                  = L[46]
    D['Day’s Range']                                = L[47]
    D['Day’s Range (Real-time)']                    = L[48]
    D['50-day Moving Average']                      = L[49]
    D['200-day Moving Average']                     = L[50]
    D['Change From 200-day Moving Average']         = L[51]
    D['Percent Change From 200-day Moving Average'] = L[52]
    D['Change From 50-day Moving Average']          = L[53]
    D['Percent Change From 50-day Moving Average']  = L[54]
    D['Name']                                       = L[55]
    D['Notes']                                      = L[56]
    D['Open']                                       = L[57]
    D['Previous Close']                             = L[58]
    D['Price Paid']                                 = L[59]
    D['Change in Percent']                          = L[60]
    D['Price/Sales']                                = L[61]
    D['Price/Book']                                 = L[62]
    D['Ex-Dividend Date']                           = L[63]
    D['P/E Ratio']                                  = L[64]
    D['Dividend Pay Date']                          = L[65]
    D['P/E Ratio (Real-time)']                      = L[66]
    D['PEG Ratio']                                  = L[67]
    D['Price/EPS Estimate Current Year']            = L[68]
    D['Price/EPS Estimate Next Year']               = L[69]
    D['Symbol']                                     = L[70]
    D['Shares Owned']                               = L[71]
    D['Short Ratio']                                = L[72]
    D['Last Trade Time']                            = L[73]
    D['Trade Links']                                = L[74]
    D['Ticker Trend	']                              = L[75]
    D['1 yr Target Price']                          = L[76]
    D['Volume']                                     = L[77]
    D['Holdings Value']                             = L[78]
    D['Holdings Value (Real-time)']                 = L[79]
    D['52-week Range']                              = L[80]
    D['Day’s Value Change']                         = L[81]
    D['Day’s Value Change (Real-time)']             = L[82]
    D['Stock Exchange']                             = L[83]
    D['Dividend Yield']                             = L[84]
    i = 0
    for k, v in D.items():
        print("{} {:<60} {}".format(i, k, v))
        i += 1

    return
