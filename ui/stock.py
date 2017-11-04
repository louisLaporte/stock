#!/usr/bin/env python3
from math import pi
import sys
import os
import logging
from datetime import date
from dateutil.relativedelta import relativedelta
from bokeh.layouts import layout, column
from bokeh.plotting import figure, ColumnDataSource
from bokeh.models import HoverTool
from bokeh.models.widgets import (
    Select,
    TextInput,
    DataTable,
    DateFormatter,
    TableColumn
)

project_path = os.path.realpath(os.path.dirname(__file__) + '/..')
sys.path.append(project_path)

import core.market
import util.twitter
import plot
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('[%(name)s][%(levelname)s]%(message)s')
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
log.addHandler(ch)


class Market():
    ###########################################################################
    # PLOT WIDGET
    ###########################################################################
    # +----------------------------+
    # | +-----------+ +----------+ |
    # | | start_btn | | end_btn  | |
    # | +-----------+ +----------+ |
    # +----------------------------+
    # |                            |
    # |          plot              |
    # |                            |
    # +----------------------------+
    ###########################################################################

    def __init__(self,
                 start=(date.today() - relativedelta(years=3)),
                 end=date.today()):
        self.start = str(start)
        self.end = str(end)
        self.sp500 = core.market.SP500('dataset/tickers.h5')
        symbols = self.sp500.tickers_store['default']['symbol'].values.tolist()
        # log.info("{}".format(symbols))
        # Select tick button
        title = "Company tick"
        self.select_tick = Select(title=title, value=symbols[0], options=symbols)
        # Inputs buttons
        self.start_date = TextInput(value=self.start, title='start')
        self.end_date = TextInput(value=self.end, title='end')
        # layout
        self.plot_layout = self.candle_plot(symbols[0])

        self.start_date.on_change('value', self.on_start_date_input_change)
        self.end_date.on_change('value', self.on_end_date_input_change)
        self.select_tick.on_change('value', self.on_tick_selection_change)
        self.layout = layout([[self.select_tick, self.start_date, self.end_date],
                              [self.plot_layout]])

    def candle_plot(self, ticker, index_name='date'):
        self.df = self.sp500.get_ticker_stocks(ticker, self.start, self.end)
        self.df = plot.normalize_name(self.df)
        self.df = self.df.set_index(index_name)
        index = self.df.index.get_level_values(index_name)
        stock_data = {index_name: index}

        for val in self.df.columns.values:
            stock_data[val] = self.df[val]
        # log.info(stock_data)

        source = ColumnDataSource(data=dict(stock_data))
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
        p = figure(x_axis_type="datetime", plot_width=1600,
                   title=ticker, tools="xwheel_zoom, xpan, reset, save",
                   active_drag="xpan")

        p.add_tools(hover)
        p.toolbar.logo = None
        p.grid.grid_line_alpha = 0.3
        p.xaxis.major_label_orientation = pi / 4
        p.xaxis.axis_label = 'Date'
        p.yaxis.axis_label = 'Price'

        p.line(index_name, 'adj_close', color='#A6CEE3', source=source)
        p.line(index_name, 'adj_open', color='#FB9A99', source=source)
        p.segment(index_name, 'high', index_name, 'low', color="white", source=source)
        p.vbar(index[inc], w, self.df['open'][inc], self.df['close'][inc],
               fill_color="#D5E1DD", line_color="white")
        p.vbar(index[dec], w, self.df['open'][dec], self.df['close'][dec],
               fill_color="#F2583E", line_color="white")
        p.legend.location = "top_left"
        p.background_fill_color = "black"
        columns = [TableColumn(field="date", title="date",
                               formatter=DateFormatter())]
        for key in stock_data.keys():
            if key != 'date':
                columns.append(TableColumn(field=key, title=key))

        # Layout
        return column(p, DataTable(source=source, columns=columns, width=1600))

    # CALLBACK
    def on_tick_selection_change(self, attr, old, new):
        log.debug('VALUE: old {} | new {}'.format(old, new))
        self.layout.children[1] = self.candle_plot(new)

    def on_start_date_input_change(self, attr, old, new):
        log.debug('VALUE: old {} | new {}'.format(old, new))
        self.start = new
        self.layout.children[1] = self.candle_plot(self.select_tick.value)

    def on_end_date_input_change(self, attr, old, new):
        log.debug('VALUE: old {} | new {}'.format(old, new))
        self.end = new
        self.layout.children[1] = self.candle_plot(self.select_tick.value)


class Twitter:

    def __init__(self,
                 start=(date.today() - relativedelta(years=3)),
                 end=date.today()):
        self.twitter = util.twitter.Twitter()
