#!/usr/bin/env python3
from math import pi
import numpy as np
import pandas as pd
from pandas_datareader import data, wb

from bokeh.driving import linear
from bokeh.layouts import gridplot, widgetbox, layout, row, column, WidgetBox
from bokeh.plotting import figure, show, output_file, ColumnDataSource
from bokeh.io import curdoc
from bokeh.models import HoverTool

from bokeh.models.widgets import (Select, Slider, TextInput, RangeSlider, Div,
                                  CheckboxGroup, DataTable, DateFormatter, TableColumn,
                                  Panel, Tabs)
import core.market
# from bokeh.models.widgets.inputs import DateRangeSlider
# from bokeh.client import push_session
import random
def datetime(x):
    return np.array(x, dtype=np.datetime64)


class Market():
    ###########################################################################
    # PLOT WIDGET
    ###########################################################################
    # +----------------------------+--------------+
    # |                            |              |
    # |          plot              |  checkbox    |
    # |                            |              |
    # +----------------------------+--------------+
    # | +-----------+ +----------+ |
    # | | start_btn | | end_btn  | |
    # | +-----------+ +----------+ |
    # +----------------------------+
    ###########################################################################

    def __init__(self, start='2014-01-01', end='2014-06-01',
                 tickers=core.market.get_sp500_tickers()['industrials']):
        super().__init__()
        self.start = start
        self.end = end
        self.select_tick_btn = Select(
            title="Company tick",
            value=tickers[0],
            options=tickers
        )
        self.debug = Div(text="""Some text""", width=200, height=100)

        # /!\ not working: wait for bokeh master release 12.7
        # date_range_slider = DateRangeSlider(bounds=(start, end),
        #                                    value=(start, end),
        #                                    range=({'days': 1}, {'days':5})
        # )
        self.start_date_input = TextInput(value=start, title='start')
        self.end_date_input = TextInput(value=end, title='end')
        # layout

        self.display_plot_checkbox_group = CheckboxGroup(
            labels=["open/close", "high/low", "volume", 'all'],
            active=[3]
        )
        self.plot_layout = self.candle_plot(tickers[0])

        self.start_date_input.on_change("value", self.on_start_date_input_change)
        self.end_date_input.on_change("value", self.on_end_date_input_change)
        self.select_tick_btn.on_change('value', self.on_tick_selection_change)
        self.main_layout = layout([
            [self.select_tick_btn, self.start_date_input, self.end_date_input],
            [self.plot_layout],
        ])

    def widget(self):
        return self.main_layout

    def normalize_name(self):
        self.df.columns = [c.lower().replace(' ', '_') for c in self.df.columns.values]
        self.df.index.names = [c.lower().replace(' ', '_') for c in self.df.index.names]

    def candle_plot(self, ticker, index_name='date'):
        self.df = core.market.get_ticker_stocks(ticker, self.start, self.end)

        self.normalize_name()
        self.df = self.df.set_index(index_name)
        print(self.df[['open', 'close', 'adj_open', 'adj_close', 'volume', 'split_ratio']])
        index = self.df.index.get_level_values(index_name)
        data = {index_name: index}

        for val in self.df.columns.values:
            data[val] = self.df[val]

        source = ColumnDataSource(data=dict(data))
#
        hover = HoverTool(tooltips=[('date', '@date{%F}'),
                                    ('adj close', '$@adj_close{%0.2f}'),
                                    ('adj open', '$@adj_open{%0.2f}'),
                                    ('volume', '@volume{0.00 a}'),
                                    ('open', '@open{%0.2f}'),
                                    ('close', '@close{%0.2f}')],
                          formatters={'date': 'datetime',
                                      'adj_close': 'printf',
                                      'adj_open': 'printf',
                                      'open': 'printf',
                                      'close': 'printf'},
                          mode='vline')
        inc = self.df['close'] > self.df['open']
        dec = self.df['open'] > self.df['close']
        w = 12 * 60 * 60 * 1000  # half day in ms
        p = figure(x_axis_type="datetime", plot_width=1600, title=ticker, tools=[hover])
        p.grid.grid_line_alpha = 0.3
        p.xaxis.major_label_orientation = pi / 4
        p.xaxis.axis_label = 'Date'
        p.yaxis.axis_label = 'Price'
        p.grid.grid_line_alpha = 0.3

        p.line(index_name, 'adj_close', color='#A6CEE3', source=source)
        p.line(index_name, 'adj_open', color='#FB9A99', source=source)
        p.segment(index_name, 'high', index_name, 'low', color="white", source=source)

        p.vbar(index[inc], w, self.df['open'][inc], self.df['close'][inc],
               fill_color="#D5E1DD", line_color="white")
        p.vbar(index[dec], w, self.df['open'][dec], self.df['close'][dec],
               fill_color="#F2583E", line_color="white")
        p.legend.location = "top_left"
        p.background_fill_color = "black"
        columns = [
            TableColumn(field="date", title="date", formatter=DateFormatter()),
        ]
        for key in data.keys():
            if key != 'date':
                columns.append(TableColumn(field=key, title=key))

        data_table = DataTable(source=source, columns=columns, width=1600)
        layout = column(p, data_table)
        return layout


    # def month_average(self):
    #     aapl = np.array(AAPL['adj_close'])
    #     aapl_dates = np.array(AAPL['date'], dtype=np.datetime64)

    #     window_size = 30
    #     window = np.ones(window_size)/float(window_size)
    #     aapl_avg = np.convolve(aapl, window, 'same')

    #     p = figure(x_axis_type="datetime", title="AAPL One-Month Average")
    #     p.grid.grid_line_alpha = 0
    #     p.xaxis.axis_label = 'Date'
    #     p.yaxis.axis_label = 'Price'
    #     p.ygrid.band_fill_color = "olive"
    #     p.ygrid.band_fill_alpha = 0.1

    #     p.circle(aapl_dates, aapl, size=4, legend='close',
    #              color='darkgrey', alpha=0.2)

    #     p.line(aapl_dates, aapl_avg, legend='avg', color='navy')
    #     p.legend.location = "top_left"
    ############################################################################
    # CALLBACK
    ############################################################################
    def on_tick_selection_change(self, attr, old, new):
        print('old', old, 'new', new)
        self.main_layout.children[1] = self.candle_plot(new)

    def on_start_date_input_change(self, attr, old, new):
        self.start = new
        self.main_layout.children[1] = self.candle_plot(self.select_tick_btn.value)

    def on_end_date_input_change(self, attr, old, new):
        self.end = new
        self.main_layout.children[1] = self.candle_plot(self.select_tick_btn.value)


def MainWindow():
    companies = ['AAPL', 'IBM', 'GOOGL', 'MSFT']
    market = Market()
    tab1 = Panel(child=market.widget(), title="Market")
    # tab2 = Panel(title="live", child=layout([l]))
    tabs = Tabs(tabs=[tab1])  # , tab2 ])
# stream some data
    return tabs

curdoc().add_root(MainWindow())