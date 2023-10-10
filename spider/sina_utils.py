import datetime
import logging

import time
import requests

import os
import sys
from random import randint
import pandas as pd
import datetime
# from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List

# 期货代码前缀信息
DCEmkt = ['V','P','B','M','I','JD','L','PP','FB','BB','Y','C','A','J','JM','CS','EG','RR','EB','PG','LH']
CZCEmkt=['TA','OI','RS','RM','ZC','WH','JR','SR','RI','CF','MA','FG','LR','SF','SM','CY','AP','CJ','UR','SA','PF','PK']
CFFEXmkt=['IF','TF','T','IH','IC','TS','IM']
GFEXmkt=['SI','LC']
SHFEmkt=['FU','SC','AL','RU','ZN','CU','AU','RB','WR','PB','AG','BU','HC','SN','NI','SP','NR','SS','LU','BC','AO','BR','EC']



def future_csv_path(date):
    return os.path.join('../dataset/daily_data',date+'.csv')