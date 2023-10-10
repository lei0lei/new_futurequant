import requests
import json


def get_all_future_code(download = False):
    endpoint = 'https://getfuturecode.azurewebsites.net/api/GetFutureCode'
    
    return requests.get(endpoint).json()['codes']