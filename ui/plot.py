import numpy as np


def datetime(x):
    return np.array(x, dtype=np.datetime64)


def normalize_name(dataframe):
    dataframe.columns = [c.lower().replace(' ', '_') for c in dataframe.columns.values]
    dataframe.index.names = [c.lower().replace(' ', '_') for c in dataframe.index.names]
    return dataframe
