import csv

import pandas as pd
import sys
sys.path.insert(1, '..')
sys.path.insert(1, '../spider')
import csv
import os

import datetime,time
from sina_utils import *

def file_exists(path):
    if os.path.exists(path):
        return True
    else:
        return False

def make_csv_file(path):
    with open(path, 'w'): pass
    return path

base_dir = '../dataset/daily_data'
out_dir = '../dataset/daily_data_1'

files = [i for i in os.listdir(base_dir) if i.endswith('.csv')]

for i in files:
    in_csv_path = os.path.join(base_dir,i)
    out_csv_dir = os.path.join(out_dir,i.split('.')[0])
    if not file_exists(out_csv_dir):
        os.mkdir(out_csv_dir)
    # csv_path = make_csv_file(os.path.join(out_csv_dir,i.split('.')[0]+'-daily.csv'))
    # with open(csv_path,'w', newline='') as f:
    #     writer = csv.writer(f)

    #     writer.writerow(["future_code","market","future_name","clock","date","open_price","max_price","min_price","close_price","yesterday_price","buy_price","sell_price","newest_price","buy_amount","sell_amount","amount","volume","everage_price"])

    with open(os.path.join(base_dir,i),'r',encoding='UTF-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            date = row['date']
            future_code = row['future_code']
            if not file_exists(os.path.join(out_csv_dir,future_code+'-daily.csv')):
                with open(os.path.join(out_csv_dir,future_code+'-daily.csv'), 'a', newline='',encoding="utf-8") as f1:
                    writer = csv.writer(f1)
                    writer.writerow(["future_code","market","future_name","clock","date","open_price","max_price","min_price","close_price","yesterday_price","buy_price","sell_price","newest_price","buy_amount","sell_amount","amount","volume","everage_price"])


            with open(os.path.join(out_csv_dir,future_code+'-daily.csv'), 'a', newline='',encoding="utf-8") as output_file:
                dict_writer = csv.DictWriter(output_file, row.keys())
                # dict_writer.writeheader()
                dict_writer.writerow(row)