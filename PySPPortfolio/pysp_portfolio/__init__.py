# -*- coding: utf-8 -*-
"""
Authors: Hung-Hsin Chen <chenhh@par.cse.nsysu.edu.tw>
License: GPL v2
"""

import os
import platform
from datetime import date

PROJECT_DIR = os.path.abspath(os.path.curdir)

# directory of storing stock data
SYMBOLS_CSV_DIR =os.path.join(PROJECT_DIR, 'data', 'tej')
SYMBOLS_PKL_DIR = os.path.join(PROJECT_DIR, 'data', 'pkl')

# operating system
os_type = platform.system()
if os_type == 'Linux':
    EXP_SP_PORTFOLIO_DIR = os.path.join(r'/home/chenhh/Dropbox',
                                  'financial_experiment', 'pysp_portfolio')

elif os_type == 'Windows':
    EXP_SP_PORTFOLIO_DIR = os.path.join(r'C:\Users\chen1\Dropbox',
                                  'financial_experiment',
                                  'pysp_portfolio')
else:
    raise ValueError('unknown os platform:{}'.format(os_type))

if not os.path.exists(EXP_SP_PORTFOLIO_DIR):
    os.makedirs(EXP_SP_PORTFOLIO_DIR)

# experiment global setting
DEFAULT_SOLVER = 'cplex'
BUY_TRANS_FEE = 0.001425
SELL_TRANS_FEE = 0.004425
START_DATE = date(2005, 1, 1)
END_DATE = date(2014, 12, 31)
N_SCENARIO = 200
WINDOW_LENGTH = 200


EXP_SYMBOLS = [
    "2330", "2412", "2882", "6505", "2317",
    "2303", "2002", "1303", "1326", "1301",
    "2881", "2886", "2409", "2891", "2357",
    "2382", "3045", "2883", "2454", "2880",
    "2892", "4904", "2887", "2353", "2324",
    "2801", "1402", "2311", "2475", "2888",
    "2408", "2308", "2301", "2352", "2603",
    "2884", "2890", "2609", "9904", "2610",
    "1216", "1101", "2325", "2344", "2323",
    "2371", "2204", "1605", "2615", "2201",
]

__all__ = ['PROJECT_DIR', 'SYMBOLS_CSV_DIR', 'SYMBOLS_PKL_DIR',
           'EXP_SP_PORTFOLIO_DIR',
           'DEFAULT_SOLVER', 'BUY_TRANS_FEE', 'SELL_TRANS_FEE',
           'START_DATE', 'END_DATE', "N_SCENARIO", 'WINDOW_LENGTH',
           'EXP_SYMBOLS']
