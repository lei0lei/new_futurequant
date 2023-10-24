import datetime
import logging
# import azure.functions as func

import requests
import os
import datetime
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import trange
import pymongo

import requests
import pandas as pd
import sys
sys.path.insert(1, '..')
import csv

import schedule
import datetime,time
from sina_utils import *
from azure_api.future_code import get_all_future_code
from utils.ex_dir import file_exists,make_csv_file
all_future_code = get_all_future_code(download=False)


# import os

# proxy = 'https://localhost:7890'
# os.environ['http_proxy'] = proxy 
# os.environ['HTTP_PROXY'] = proxy
# os.environ['https_proxy'] = proxy
# os.environ['HTTPS_PROXY'] = proxy

DCE_DB_NAME = "DCEdb"
DCE_FUTURE_CODE = "DCEFutureCodeDb"
DAILY_FUTURE_DB = 'DailyFutureDb'

COSMOS_CONNECTION_STRING = 'mongodb://lei:jDa0YcHR5WpGRQUaCsK5ZzObqJpjbiEwYF4S8FfbbWWMkqV1HTtVzWFkF8U0lqRXRbLZfVJtyIYoACDbqnzU3w==@lei.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@lei@'

client = pymongo.MongoClient(COSMOS_CONNECTION_STRING)
DCEdb = client[DCE_DB_NAME]

date =  datetime.date(2023,10,20)-datetime.timedelta(days=800)

# app = func.FunctionApp()

start = str(date)
end = str(datetime.date.today())
# 需要其他期货数据，修改此处代码

# ---------------------------------------------------
# @app.schedule(schedule="0 0 8 * * 2-6", arg_name="myTimer", run_on_startup=True,
#               use_monitor=False) 
# def DailyFutureCrawler(myTimer: func.TimerRequest) -> None:
#     utc_timestamp = datetime.datetime.utcnow().replace(
#         tzinfo=datetime.timezone.utc).isoformat()

    # if myTimer.past_due:
    #     logging.info('The timer is past due!')

    # logging.info('Python timer trigger function ran at %s', utc_timestamp)
# -----------------------------------------

def run():
    # codes = get_future_code()
    # DCE_future_daily_collection = DCEdb[DAILY_FUTURE_DB]
    codes = get_future_code()
    for code in codes:
        blanklist = []
        for p in range(30):
            
            page_url = f'https://vip.stock.finance.sina.com.cn/q/view/vFutures_History.php?page='+str(p+1)+'&breed='+code+'&type=inner&start='+start+'&end='+end
            # page_url = f'https://vip.stock.finance.sina.com.cn/q/view/vFutures_History.php?page=1&breed=C2111&type=inner&start=20230920&end=20230920'
            print(page_url)
            r = requests.get(page_url)
            soup = BeautifulSoup(r.text.encode('utf8'), 'html.parser')
            table = soup.find_all("div", class_="historyList")
            if len(table)<1:
                continue
            table = BeautifulSoup(table[0].prettify().encode('utf8'), 'html.parser')
            a = pd.read_html(table.prettify())
            if a[0].shape[0]<2:
                break
            # print(a[0])
            # print(a[0].shape[0])
            for index,row in a[0].iterrows():
                # print(row)
                if index == 0:
                    continue
                if index>=1:
                # if index>=1:
                    # pass
                    # if DCE_future_daily_collection.find_one({'$and':[{'date':row[0]},{'future_code':code}]}):
                    # continue

                    # else:
                    blanklist.append({'date':row[0],
                                        'future_code':code,
                                        'close':float(row[1]),
                                        'open':float(row[2]),
                                        'high':float(row[3]),
                                        'low':float(row[4]),
                                        'deal':int(row[5]),
                                        'categoryID':str(datetime.date.today())})
                    print(f'x')
                else:
                    print(f'z')
                    break
        if len(blanklist)==0:
            continue
        csv_path = future_daily_price_path(blanklist[0]['future_code'])
        keys = blanklist[0].keys()
        if not file_exists(csv_path):
            with open(csv_path, 'a', newline='',encoding="utf-8") as output_file:
                dict_writer = csv.DictWriter(output_file, keys)
                dict_writer.writeheader()
        with open(csv_path, 'a', newline='',encoding="utf-8") as output_file:
            w = csv.DictWriter(output_file,keys)
            w.writerows(blanklist)
        # DCE_future_daily_collection.insert_many(blanklist)
        logging.info(f'{code} daily info add to db DailyFutureDb')
def get_future_code():
    DCE_future_code_collection = DCEdb[DCE_FUTURE_CODE]
    return DCE_future_code_collection.find({}).sort('update_time',pymongo.DESCENDING)[0]['future_code']
    

if __name__ == '__main__':
    run()