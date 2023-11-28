'''
program to craw everyday future info from http://vip.stock.finance.sina.com.cn/
by: lei.lei.fan.meng@gmail.com
update: 2023-10-10
'''

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
# all_future_code = get_all_future_code(download=False)


CODE_DIR = '../dataset/daily_data_1/2023-10-25'
all_future_code = [i.split('-')[0] for i in os.listdir(CODE_DIR)]



out_dir = '../dataset/daily_data_1'
def sina_future_crawler():
    print(f'------------')
    if datetime.datetime.today().weekday() >4:
        logging.info(f'oops, today is weekend')
        return None
    logging.info(f'craw in time {datetime.datetime.utcnow()}')
    # request header and endpoint
    Referer = 'https://finance.sina.com.cn/futures/quotes.shtml'
    Host = 'hq.sinajs.cn'
    code_prefix = 'nf_'
    code_str = ''
    today = str(datetime.date.today())
    # 新建每日存放目录
    if not file_exists(os.path.join(out_dir,today)):
        os.mkdir(os.path.join(out_dir,today))
    print(today)

    # all_future_code = get_all_future_code(download=False)
    for k in all_future_code:
        code_str+=code_prefix
        code_str+=k
        code_str+=','

    query_str = 'https://hq.sinajs.cn/?_='+str(int(time.time()*1000))+'/$list='+code_str

    # check csv file exists
    csv_file = future_csv_path(today)
    if file_exists(csv_file):
        pass 
    else:
        csv_file = make_csv_file(csv_file)

    response = requests.get(query_str,headers={'Referer':Referer,'Host':Host})
    
    t = response.text.splitlines()
    ft = [i.split('_')[-1] for i in t]

    # write future price to csv file every 5 minutes
    to_insert_items = []
    for i in ft:
        
        to_insert_item = {}
        
        to_insert_item['future_code'] = i.split('=')[0]
        future_code_list =[p for p in  to_insert_item['future_code'] if p>='A' and p<='Z']
        future_code_str = ''.join(future_code_list)
        if future_code_str in DCEmkt:
            to_insert_item['market'] = 'DCE'
        elif future_code_str in CZCEmkt:
            to_insert_item['market'] = 'CZCE'
        elif future_code_str in CFFEXmkt:
            to_insert_item['market'] = 'CFFEX'
        elif future_code_str in GFEXmkt:
            to_insert_item['market'] = 'GFEX'
        elif future_code_str in SHFEmkt:
            to_insert_item['market'] = 'SHFE'
        else:
            to_insert_item['market'] = None
        # print(to_insert_item['future_code'])
        _items = i.split('"')[1]
        # print(_items)
        items = _items.split(',')
        # print(items)
        # print(len(items))
        if len(items)==1:
            continue
        if int(items[1]) < 90000 or 112900<int(items[1])<120000 or  145900<int(items[1])<170000 or int(items[1])>225900:
            continue
        to_insert_item['future_name'] = items[0]
        to_insert_item['clock'] = int(items[1])
        to_insert_item['date'] = items[17]
        to_insert_item['categoryID'] = items[17]
        to_insert_item['open_price'] = float(items[2])
        to_insert_item['max_price'] = float(items[3])
        to_insert_item['min_price'] = float(items[4])
        to_insert_item['close_price'] = float(items[5])
        to_insert_item['yesterday_price'] = float(items[10])
        to_insert_item['buy_price'] = float(items[6])
        to_insert_item['sell_price'] = float(items[7])
        to_insert_item['newest_price'] = float(items[8])
        to_insert_item['buy_amount'] = float(items[11])
        to_insert_item['sell_amount'] = float(items[12])
        to_insert_item['amount'] = float(items[14])
        to_insert_item['volume'] = float(items[13])
        to_insert_item['everage_price'] = float(items[27])

        # 写入csv
        # keys = to_insert_item.keys()
        if not file_exists(os.path.join(out_dir,to_insert_item['date'],to_insert_item['future_code']+'-daily.csv')):
            with open(os.path.join(out_dir,to_insert_item['date'],to_insert_item['future_code']+'-daily.csv'), 'a', newline='',encoding="utf-8") as output_file:
                writer = csv.writer(output_file)
                writer.writerow(["future_code","market","future_name","clock","date","categoryID","open_price","max_price","min_price","close_price","yesterday_price","buy_price","sell_price","newest_price","buy_amount","sell_amount","amount","volume","everage_price"])
        with open(os.path.join(out_dir,to_insert_item['date'],to_insert_item['future_code']+'-daily.csv'), 'a', newline='',encoding="utf-8") as f1:
            dict_writer = csv.DictWriter(f1, to_insert_item.keys())
            dict_writer.writerow(to_insert_item)
    #     to_insert_items.append(to_insert_item)
    # keys = to_insert_items[0].keys()



    # with open(csv_file, 'a', newline='',encoding="utf-8") as output_file:
    #     dict_writer = csv.DictWriter(output_file, keys)
    #     dict_writer.writeheader()
    #     dict_writer.writerows(to_insert_items)

# run every minute
if __name__ == '__main__':
    schedule.every(1).minutes.do(sina_future_crawler)
    while True:
        schedule.run_pending()
        time.sleep(1)