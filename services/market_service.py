#!/usr/bin/env python3
import os
import sys

project_path = os.path.realpath(os.path.dirname(__file__) + '/..')
sys.path.append(project_path)

import core.market

sp500 = core.market.SP500()
print(sp500.get_table_header("efault"))
print(sp500.get_tables_name())

# print(sp500.get_webistes()
