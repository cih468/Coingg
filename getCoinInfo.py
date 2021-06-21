# !pip install pyjwt==1.6.4
import os
import jwt
import uuid
import hashlib
from urllib.parse import urlencode
import pandas as pd
import matplotlib.pyplot as plt

import requests


def getCoinDF(market, timedelta, count,size):
    url = f"https://api.upbit.com/v1/candles/minutes/{timedelta}"

    query = {"market":f"{market}", "count":f"{count}"}

    df = []
    while True:
        response = requests.request("GET", url, params=query)
        if response.text != "Too many API requests." :
            df = pd.read_json(response.text)
            break

    while(len(df)<size):
        if len(df)%1000==0:
            print(len(df))
        ts = df['timestamp'].iloc[-1]
        last = f'{ts.year:02d}-{ts.month:02d}-{ts.day:02d} {ts.hour:02d}:{ts.minute:02d}:{round(ts.second):02d}'
        url = f"https://api.upbit.com/v1/candles/minutes/{timedelta}"

        querystring = {"market":f"{market}","count":f"{count}",'to':last}

        response = requests.request("GET", url, params=querystring)
        if response.text == "Too many API requests." :
            continue

        df_app = pd.read_json(response.text)
        df = pd.concat([df,df_app], ignore_index=True)

    return df