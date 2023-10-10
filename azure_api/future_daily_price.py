import requests


def get_daily_future_price(code,start,end):
    endpoint = 'https://getdailyfutureprice.azurewebsites.net/api/GetDailyFuturePrice'
        # {"code":"CU2311",
        # "start_date":"2023-08-01",
        # "end_date":"2023-09-11"}

    return requests.post(endpoint,json = {'code':code,'start_date':start,'end_date':end}).json()