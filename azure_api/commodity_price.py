import requests



def get_commodity_price(code,start,end):
    endpoint = 'https://getdailycommodityprice.azurewebsites.net/api/GetDailyCommodityPrice'
    # POST: {"code":"CU",
    #         "start_date":"2023-08-01",
    #         "end_date":"2023-09-11"}
    return requests.post(endpoint,json = {'code':code,'start_date':start,'end_date':end}).json()