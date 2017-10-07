#!/usr/bin/env python3
from math import pi
import numpy as np
from bokeh.layouts import layout, column
from bokeh.plotting import figure, ColumnDataSource
from bokeh.io import curdoc
from bokeh.models import HoverTool

from bokeh.models.widgets import (Select, TextInput, DataTable, DateFormatter,
                                  TableColumn, Panel, Tabs)
import core.market
from datetime import date
from dateutil.relativedelta import relativedelta


def datetime(x):
    return np.array(x, dtype=np.datetime64)


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
                 end=date.today(),
                 tickers=core.market.get_sp500_tickers()['industrials']):
        self.start = str(start)
        self.end = str(end)
        self.select_tick_btn = Select(title="Company tick",
                                      value=tickers[0],
                                      options=tickers)
        self.start_date_input = TextInput(value=self.start, title='start')
        self.end_date_input = TextInput(value=self.end, title='end')
        # layout
        self.plot_layout = self.candle_plot(tickers[0])

        self.start_date_input.on_change('value', self.on_start_date_input_change)
        self.end_date_input.on_change('value', self.on_end_date_input_change)
        self.select_tick_btn.on_change('value', self.on_tick_selection_change)
        self.layout = layout([[self.select_tick_btn,
                               self.start_date_input,
                               self.end_date_input],
                              [self.plot_layout]])

    def normalize_name(self):
        self.df.columns = [c.lower().replace(' ', '_') for c in self.df.columns.values]
        self.df.index.names = [c.lower().replace(' ', '_') for c in self.df.index.names]

    def candle_plot(self, ticker, index_name='date'):
        self.df = core.market.get_ticker_stocks(ticker, self.start, self.end)

        self.normalize_name()
        self.df = self.df.set_index(index_name)
        index = self.df.index.get_level_values(index_name)
        stock_data = {index_name: index}

        for val in self.df.columns.values:
            stock_data[val] = self.df[val]

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
        columns = [TableColumn(field="date", title="date",
                               formatter=DateFormatter())]
        for key in stock_data.keys():
            if key != 'date':
                columns.append(TableColumn(field=key, title=key))

        data_table = DataTable(source=source, columns=columns, width=1600)
        layout = column(p, data_table)
        return layout

    # CALLBACK
    def on_tick_selection_change(self, attr, old, new):
        print('old', old, 'new', new)
        self.layout.children[1] = self.candle_plot(new)

    def on_start_date_input_change(self, attr, old, new):
        self.start = new
        self.layout.children[1] = self.candle_plot(self.select_tick_btn.value)

    def on_end_date_input_change(self, attr, old, new):
        self.end = new
        self.layout.children[1] = self.candle_plot(self.select_tick_btn.value)


def MainWindow():
    tab1 = Panel(child=Market().layout, title="Market")
    tabs = Tabs(tabs=[tab1])
    return tabs


curdoc().add_root(MainWindow())
