from bokeh.io import curdoc
from bokeh.models.widgets import Panel, Tabs
import stock


def MainWindow():
    tab1 = Panel(child=stock.Market().layout, title="Market")
    tab2 = Panel(child=stock.Market().layout, title="Twitter")
    tabs = Tabs(tabs=[tab1, tab2])
    return tabs


curdoc().add_root(MainWindow())
