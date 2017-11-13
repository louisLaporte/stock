# sp500

This is a quick tour of how to use this command

## list
### Store
```
$ ./sp500 list store
['/info', '/web']
```
### Table
```
$ ./sp500 list table info
['symbol', 'security_name', 'gcis_sector', 'gcis_subsector', 'hq_address', 'date_added', 'cik'] 
```

## show
### Table
```
$ ./sp500 show table info
   symbol                        security_name             gcis_sector                                gcis_subsector                     hq_address  date_added         cik
0      MMM                           3M Company             Industrials                      Industrial Conglomerates            St. Paul, Minnesota              0000066740
1      ABT                  Abbott Laboratories             Health Care                         Health Care Equipment        North Chicago, Illinois  1964-03-31  0000001800
2     ABBV                          AbbVie Inc.             Health Care                               Pharmaceuticals        North Chicago, Illinois  2012-12-31  0001551152
3      ACN                        Accenture plc  Information Technology                IT Consulting & Other Services                Dublin, Ireland  2011-07-06  0001467373
4     ATVI                  Activision Blizzard  Information Technology                   Home Entertainment Software       Santa Monica, California  2015-08-31  0000718877
5      AYI                    Acuity Brands Inc             Industrials             Electrical Components & Equipment               Atlanta, Georgia  2016-05-03  0001144215
...
```

### Where
Case sensistive
```
$ ./sp500 show where aa
    symbol            security_name  gcis_sector     gcis_subsector           hq_address  date_added         cik                                          wikipedia                    website                         twitter
16     ALK     Alaska Air Group Inc  Industrials           Airlines  Seattle, Washington  2016-05-13  0000766421  http://en.wikipedia.org/wiki/Alaska_Air_Group_Inc  http://www.alaskaair.com/   https://twitter.com/alaskaair
31     AAL  American Airlines Group  Industrials           Airlines    Fort Worth, Texas  2015-03-23  0000006201  http://en.wikipedia.org/wiki/American_Airlines...          http://www.aa.com  http://twitter.com/americanair
315    MAA   Mid-America Apartments  Real Estate  Residential REITs   Memphis, Tennessee  2016-12-02  0000912595  http://en.wikipedia.org/wiki/Mid-America_Apart...       http://www.maac.com/                             nan
```
Insensitive case
```
$ ./sp500 show where -i aa
    symbol            security_name             gcis_sector                              gcis_subsector             hq_address  date_added         cik                                          wikipedia                           website                          twitter
8      AAP       Advance Auto Parts  Consumer Discretionary                           Automotive Retail      Roanoke, Virginia  2015-07-09  0001158449    http://en.wikipedia.org/wiki/Advance_Auto_Parts  http://www.advanceautoparts.com/  https://twitter.com/AdvanceAuto
16     ALK     Alaska Air Group Inc             Industrials                                    Airlines    Seattle, Washington  2016-05-13  0000766421  http://en.wikipedia.org/wiki/Alaska_Air_Group_Inc         http://www.alaskaair.com/    https://twitter.com/alaskaair
31     AAL  American Airlines Group             Industrials                                    Airlines      Fort Worth, Texas  2015-03-23  0000006201  http://en.wikipedia.org/wiki/American_Airlines...                 http://www.aa.com   http://twitter.com/americanair
51    AAPL               Apple Inc.  Information Technology  Technology Hardware, Storage & Peripherals  Cupertino, California  1982-11-30  0000320193            http://en.wikipedia.org/wiki/Apple_Inc.                  http://apple.com                              nan
315    MAA   Mid-America Apartments             Real Estate                           Residential REITs     Memphis, Tennessee  2016-12-02  0000912595  http://en.wikipedia.org/wiki/Mid-America_Apart...              http://www.maac.com/                              nan
458    UAA     Under Armour Class A  Consumer Discretionary         Apparel, Accessories & Luxury Goods    Baltimore, Maryland  2016-03-25  0001336917          http://en.wikipedia.org/wiki/Under_Armour       http://www.underarmour.com/                              nan
```
