import TT
from TT import MACD,RSI,KDJ
import pandas as pd
from datetime import datetime, timedelta, date
import time, os
import argparse
import glob
import logging
from azure_api.send_email import send_email
logging_base_dir = f'../log/algo'
# formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
import sys
sys.path.insert(1, '..')

import plotly
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
# To plot the result
plot = True

# ta库
from ta.trend import MACD
from ta.momentum import StochasticOscillator

def generate_dates(start_date, end_date):
	"""Generate a list of dates between start_date and end_date (inclusive)."""
	start = datetime.strptime(start_date, '%Y-%m-%d') - timedelta(days=1)
	end = datetime.strptime(end_date, '%Y-%m-%d')

	# print(start,end)
	
	date_list = []
	delta = timedelta(days=1)
	while start <= end:
		date_list.append(start.strftime('%Y-%m-%d'))
		start += delta
	return date_list

def get_previous_date(date_string, period=20, date_format='%Y-%m-%d'):
	"""Given a string date, return the date of given days before."""
	original_date = datetime.strptime(date_string, date_format)
	previous_date = original_date - timedelta(days=period)
	return previous_date.strftime(date_format)

def is_valid_date(date_string, date_format='%Y-%m-%d'):
	"""Check if the given string is a valid date."""
	try:
		datetime.strptime(date_string, date_format)
		return True
	except ValueError:
		return False

def check_cross(line1, line2, m = 5):
	if len(line1) < m or len(line2) < m:
		raise ValueError(f"Both line1 and line2 should have at least {m} values.")

	for i in range(len(line1) - m + 1):
		subset_1 = line1[i:i+m]
		subset_2 = line2[i:i+m]

		# 查找初始金叉
		if subset_1[0] < subset_2[0] and subset_1[1] > subset_2[1]:
			trend = "gold"
			# 检查是否K始终大于D
			if all(k > d for k, d in zip(subset_1[1:], subset_2[1:])):
				return i+1, trend

		# 查找初始死叉
		elif subset_1[0] > subset_2[0] and subset_1[1] < subset_2[1]:
			trend = "dead"
			# 检查是否K始终小于D
			if all(k < d for k, d in zip(subset_1[1:], subset_2[1:])):
				return i+1, trend

	return None, None

def check_upper_ma(prices, realtime_prices, period, if_minute = False):
	unique_codes = prices['future_code'].unique()
	newest_prices = realtime_prices[["future_code", "newest_price"]]
	ma_selected_code = []
	for code in unique_codes:
		sub_df = prices[prices['future_code'] == code]
		if if_minute:
			close_prices = sub_df["newest_price"]
		else:
			close_prices = sub_df["close"]
		# print(close_prices)
		ma_value = TT.MA(close_prices, period)[-1]

		temp = newest_prices.loc[newest_prices["future_code"] == code,"newest_price"]
		if len(temp) >0:
			if ma_value < temp.item():
				ma_selected_code.append(code)	

	return ma_selected_code


def check_daily_kdj(daily_prices, codes, tor = 1):
	selected_code = []
	print(f'x-x-x-x-x')
	print(daily_prices)

	for code in codes:
		sub_df = daily_prices[daily_prices["future_code"] == code]
		print(sub_df)
		# sub_df.to_csv("./sub_df.csv", index=False, encoding="gbk")	
		close, high, low = sub_df['close'], sub_df['high'], sub_df['low']
		K, D, J = KDJ(close, high, low)

		if len(K) >= tor and len(D) >= tor:
			_, res = check_cross(K, D)

			if res == "gold":
				selected_code.append(code)

	return selected_code

def draw_candle_kdj_macd_volumes(daily_prices,code,K,D,J):
	# fig = go.Figure()
	fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
	# 蜡烛图
	print(daily_prices)
	fig.add_trace(go.Candlestick(name='candle',x=daily_prices.date,
				open=daily_prices['open'],
				high=daily_prices['high'],
				low=daily_prices['low'],
				close=daily_prices['close']), row=1, col=1)
	# KDJt图
	fig.add_trace(go.Scatter(name='K',x=daily_prices.date,
                         y=K,
                         line=dict(color='black', width=2)
                        ), row=2, col=1)
	fig.add_trace(go.Scatter(name='D',x=daily_prices.date,
                         y=D,
                         line=dict(color='blue', width=1)
                        ), row=2, col=1)
	fig.add_trace(go.Scatter(name='J',x=daily_prices.date,
                         y=J,
                         line=dict(color='red', width=1)
                        ), row=2, col=1)
	# 去除空日期
	# build complete timeline from start date to end date
	dt_all = pd.date_range(start=daily_prices.date.iloc[0],end=daily_prices.date.iloc[-1])
	# retrieve the dates that ARE in the original datset
	dt_obs = [d.strftime("%Y-%m-%d") for d in pd.to_datetime(daily_prices.date)]
	# define dates with missing values
	dt_breaks = [d for d in dt_all.strftime("%Y-%m-%d").tolist() if not d in dt_obs]
	fig.update_layout(title=f"{code}")
	fig.update_layout(height=900, width=1200,
                  showlegend=True,
                  xaxis_rangeslider_visible=False,
                  xaxis_rangebreaks=[dict(values=dt_breaks)])
	fig.update_yaxes(title_text="candle", row=1, col=1)
	fig.update_yaxes(title_text="KDJ", row=2, col=1)
	fig.show()



def _check_daily_kdj(daily_prices, code, tor = 1):
	selected_code = []
	print(f'x-x-x-x-x')
	daily_prices = daily_prices.reset_index(drop=True)
	print(daily_prices)

	# sub_df.to_csv("./sub_df.csv", index=False, encoding="gbk")	
	close, high, low = daily_prices['close'], daily_prices['high'], daily_prices['low']
	K, D, J = KDJ(close, high, low)

	if len(K) >= tor and len(D) >= tor:
		_, res = check_cross(K, D)

		if res == "gold":
			if plot:
				draw_candle_kdj_macd_volumes(daily_prices,code,K,D,J)
			return True
		else:
			return False



def check_hourly_kdj(daily_prices, code, tor = 2):
	daily_prices.to_csv("./daily_prices.csv", index=False)	
	status = False
	daily_prices['hour'] = daily_prices['clock'] // 10000  # 将 230000 转换为 23，210000 转换为 21 等

	# 根据 future_code 和每小时进行分组，并聚合
	hourly_prices = daily_prices.groupby(['future_code', 'date', 'hour']).agg({
		'newest_price': ['last', 'max', 'min'],
		'future_code': 'first',
		'date': 'first',
		'clock': 'last'
	}).reset_index()
	hourly_prices.to_csv("./hourly_df.csv", index=False, encoding="gbk")	

	# 调整列名
	hourly_prices.columns = ['future_code', 'date', 'hour', 'close', 'high', 'low', 'future_code_', 'date_', 'clock_']
	hourly_prices = hourly_prices[['future_code', 'date', 'clock_', 'close', 'high', 'low']]
	hourly_prices.columns = ['future_code', 'date', 'clock', 'close', 'high', 'low']

	hourly_prices = hourly_prices.sort_values(by=["future_code","date","clock"], ascending=[True, True, True])
	hourly_prices.to_csv("./hourly_df2.csv", index=False, encoding="gbk")	

	selected_code = []

	close, high, low = hourly_prices['close'], hourly_prices['high'], hourly_prices['low']
	K, D, J = KDJ(close, high, low)

	if len(K) >= tor and len(D) >= tor:
		_, res = check_cross(K, D)

		if res == "gold":
			status = True

	return status

def load_minutes_data(daily_price_folder, dateslist, code, surfix = "-daily.csv", max_length = 1500):
	# 实时数据
	# dateslist = dateslist[::-1]
	df = pd.DataFrame()
	for date in dateslist:
		file_path = os.path.join(daily_price_folder,date,code + surfix)
		if os.path.exists(file_path) and len(df) < max_length:
			df_temp = pd.read_csv(file_path)
			df = pd.concat([df, df_temp], ignore_index=True)

	# print(len(df))
	# print(df.head)
	df = df.sort_values(by=['date', 'clock'], ascending=[True, True])
	# df.groupby('clock', group_keys=False).apply(lambda x: x.loc[x.B.idxmax()])
	# df_60mins = df.iloc[::-1].iloc[::60].iloc[::-1]

	return df


"""
	Here, 'end_date_string' typically represents today. 
	However, 'end_date' should be adjusted to be one day ahead ('end_date_ahead') for easier calculations, 
	especially when computing indicators such as MA and KDJ.
"""
def get_name_list(end_date_string, daily_commodity_price_folder,\
	daily_future_price_folder, \
	daily_price_folder, \
	period = 20, period_minute = 20, threshold = 0.05):
	end_date = datetime.strptime(end_date_string, "%Y-%m-%d")
	# WARNING: NOT USED END_DATE_AHEAD
	end_date_ahead = end_date - timedelta(days=1)
	end_date_ahead_string = end_date_ahead.strftime('%Y-%m-%d')  # 格式为 YYYY-MM-DD

	if is_valid_date(end_date_string):
		"""
			C1: 正基差过滤
			注意: C1部分代码无法进行回溯,过滤时会默认已知截至当前的所有数据；
				end_date更改成任何日期都不会影响这部分算法的结果。
		"""
		basis_codes = []
		csv_files = glob.glob(os.path.join(daily_commodity_price_folder, '*.csv'))
		# print(csv_files)

		if len(csv_files) > 0:
			for csv_file in csv_files:
				cur_df = pd.read_csv(csv_file)
				# 如果进行回溯，此处应该用date添加一步过滤
				cur_df = cur_df.sort_values(by=['date', 'main_future_code'], \
					ascending=[False, False])

				# Boyan : uncomment the conidtion here
				# if cur_df.iloc[0]["main_cf_basis_percent"] >= 0:
				if cur_df.iloc[0]["main_cf_basis_percent"] >= threshold:
					basis_codes.append(cur_df.iloc[0]["main_future_code"])
		else:
			print("wrong commodity price foler, pls check and rerun the code.")
			sys.exit(0)

		"""
			C2: 价格高于20日均线，且日KDJ交金叉
		"""
		upper_20dailyma_codes = []
		kdjdaily_codes = []

		# A larger date range (2*period) to ensure there's no data shortage 
		# due to non-trading days on weekends (Saturday and Sunday).
		start_date_string = get_previous_date(date_string = end_date_string, period=period*2+1) 
		dates_list = generate_dates(start_date_string, end_date_string)
		# 每日的价格信息应从今天向前推一天
		dates_list = dates_list[:-1]
		# print(dates_list)
		print(f'codes selected by C1')
		print(basis_codes)
		if len(basis_codes) >0:
			for code in basis_codes:
				print(code)
				if not os.path.exists(os.path.join(daily_future_price_folder,code+".csv")):
					print(f'no history daily future price code')
					continue
				daily_price = pd.read_csv(os.path.join(daily_future_price_folder,code+".csv"))
				# print("daily_price",daily_price.columns) # ['date', 'future_code', 'close', 'open', 'high', 'low', 'deal','categoryID']
				# print(daily_price)
				# 将 daily_price 的 'date' 列转换为正确的格式
				daily_price['date'] = pd.to_datetime(daily_price['date'], format='%Y-%m-%d').dt.strftime('%Y-%m-%d')

				# extract the data in the date list
				print(dates_list)
				filtered_daily_data = daily_price[daily_price['date'].isin(dates_list)]

				# dataframe有重复行
				filtered_daily_data = filtered_daily_data.sort_values(by=['date'], ascending = True).drop_duplicates()
				# print("filtered_daily_data",filtered_daily_data.columns) # 'date', 'future_code', 'close', 'open', 'high', 'low', 'deal', 'categoryID']
				if not os.path.exists(os.path.join(daily_price_folder,end_date_string,code+"-daily.csv")):
					continue
				df_daily_price = pd.read_csv(os.path.join(daily_price_folder,end_date_string,code+"-daily.csv"))
				"""
				[	'future_code', 'market', 'future_name', 'clock', 'date', 'open_price',
				   'max_price', 'min_price', 'close_price', 'yesterday_price', 'buy_price',
				   'sell_price', 'newest_price', 'buy_amount', 'sell_amount', 'amount',
				   'volume', 'everage_price']
				"""
				# print(df_daily_price.columns)

				latest_price = df_daily_price.iloc[-1]["newest_price"]
				print(df_daily_price)
				print(f'xxx')
				print(filtered_daily_data)
				print(f'----')
				print(df_daily_price.iloc[-1])
				print(f'--------')
				ma_value = TT.MA(filtered_daily_data["close"], period)[-1]
				print(ma_value)
				if ma_value< latest_price:
					upper_20dailyma_codes.append(code)
					if _check_daily_kdj(filtered_daily_data,code,tor = 1):
						kdjdaily_codes.append(code)
			# CHANGED:
			# if len(upper_20dailyma_codes) > 0:
			# 	# check daily kdj
			# 	kdjdaily_codes = check_daily_kdj(filtered_daily_data, upper_20dailyma_codes, tor = 1)

		"""
			C3: 价格高于60分钟-20均线，且60分钟-KDJ交金叉
		"""
		t5 = time.time()

		upper_60minsma_codes = []
		kdj60min_codes = []

		if len(kdjdaily_codes)>0:
			for code in kdjdaily_codes:
				cur_df = load_minutes_data(daily_price_folder, dates_list, code, surfix = "-daily.csv")

				df_60mins = cur_df.iloc[::-1].iloc[::60].iloc[::-1]
				ma_60mins = TT.MA(df_60mins["newest_price"], period_minute)[-1]
				if ma_60mins< cur_df.iloc[-1]["newest_price"]:
					upper_60minsma_codes.append(code)

				code_status = check_hourly_kdj(cur_df, code, tor = 2)

				if code_status:
					kdj60min_codes.append(code)

		# 创建空的 DataFrame
		final_codes = list(set(kdjdaily_codes) & set(kdj60min_codes))
		final_results = pd.DataFrame(columns=['评估指标','评估结果'])
		final_results.loc[0] = ["正基差", basis_codes]
		final_results.loc[1] = ["价格高于20日均线，且日KDJ交金叉", kdjdaily_codes]
		final_results.loc[2] = ["价格高于60分钟-20均线，且60分钟-KDJ交金叉", kdj60min_codes]
		with open(os.path.join(logging_base_dir,end_date_string+'.txt'),'a', newline='',encoding="utf-8") as f:
			result_message = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} : basis_codes: {basis_codes}\n                      kdjdaily_codes: {kdjdaily_codes}\n                      kdj60min_codes: {kdj60min_codes}\n'
			f.write(result_message)
		final_results.loc[3] = ["综合结果", final_codes]
		# final_results.to_csv("./final_results.csv", index=False, encoding="gbk")
		import pprint as pp
		pp.pprint(final_results)
		return final_results
	else:
		print("错误日期信息")
		return None




def main():

	parser = argparse.ArgumentParser(description="A simple script with args.")
	parser.add_argument("--data_dir", default = "../", type=str, help="data folder")
	parser.add_argument("--daily_commodity_price_data", default = "dataset/daily_commodity_price_data", type=str, help="daily_commodity_price_data folder")
	parser.add_argument("--daily_future_price_data", default = "dataset/daily_future_price_data", type=str, help="daily_future_price_data folder")
	parser.add_argument("--daily", default = "dataset/daily_data_1", type=str, help="daily price folder")
	parser.add_argument("--plot", default = False, type=bool, help="plot algo result")
	
	args = parser.parse_args()

	daily_commodity_price_folder = os.path.join(args.data_dir, args.daily_commodity_price_data)
	daily_future_price_folder = os.path.join(args.data_dir, args.daily_future_price_data)
	daily_price_folder = os.path.join(args.data_dir, args.daily)
	
	today_date = date.today()
	today_string = today_date.strftime('%Y-%m-%d')  # 格式为 YYYY-MM-DD
	
	today_string = "2023-10-26" 
	logging.basicConfig(level=logging.INFO,#控制台打印的日志级别
                    filename='new.log',
                    filemode='a',##模式，有w和a，w就是写模式，每次都会重新写日志，覆盖之前的日志
                    #a是追加模式，默认如果不写的话，就是追加模式
                    format=
                    '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
                    #日志格式
                    )
	results = get_name_list(end_date_string = today_string,\
		daily_commodity_price_folder = daily_commodity_price_folder, \
		daily_future_price_folder = daily_future_price_folder, \
		daily_price_folder = daily_price_folder, \
		period = 20, threshold = 0.05)

	return results

if __name__ == "__main__":
	main()
