#!/usr/bin/env python
# coding: utf-8

# In[16]:


# !pip install pyjwt==1.6.4
from numpy import record
import getCoinInfo

import os
import jwt
import uuid
import hashlib
from urllib.parse import urlencode
import pandas as pd
import matplotlib.pyplot as plt

import requests
import warnings
warnings.filterwarnings('ignore')


# In[17]:


kor_name_dict = {}


# In[18]:


#종목 조회
url = "https://api.upbit.com/v1/market/all"

querystring = {"isDetails":"false"}

response = requests.request("GET", url, params=querystring)

coin_list = response.json()
coins = []
for coin in coin_list:
    if coin['market'].split('-')[0] =='KRW':
        kor_name_dict[coin['market']] = coin['korean_name']
        coins.append(coin['market'])
len(coins)


# In[19]:


url = "https://api.upbit.com/v1/candles/days"

query = {"count":"1","market": "KRW-BTC"}
# m = hashlib.sha512()
# m.update(urlencode(query).encode())
# query_hash = m.hexdigest()
# payload = {
#     'access_key': accessKey,
#     'nonce': str(uuid.uuid4()),
#     'query_hash': query_hash,
#     'query_hash_alg': 'SHA512'
# }

# jwt_token = jwt.encode(payload, secretKey)
# authorize_token = 'Bearer {}'.format(jwt_token)
# headers = {"Authorization": authorize_token}

response = requests.request("GET", url, params =  query)

print(response.text)


# In[20]:


from tqdm import tqdm

df = {}
for coin in tqdm(coins):
    df[coin] = getCoinInfo.getCoinDF(coin,30,200,size=24*2*7)
  
df['KRW-BTC']


# In[21]:


for coin in coins:
    df[coin] = df[coin].loc[::-1,:]
    df[coin] = df[coin].reset_index()
    df[coin].drop('index',inplace=True,axis=1)


# In[22]:


df['KRW-TFUEL']


# In[23]:


df_tier = pd.DataFrame(columns=['coin','rate','trade_price'])
df_tier['coin'] = coins
df_tier['name'] = df_tier['coin'].map(kor_name_dict)
df_tier['alias'] = df_tier['coin'].str.split('-').str[1]
df_tier.set_index('coin',inplace=True)


# In[24]:


for coin in coins:
    df_tier['rate'].loc[coin]= (df[coin]['trade_price'].loc[len(df[coin])-1] - df[coin]['opening_price'].loc[0])/df[coin]['opening_price'].loc[0] * 100
    df_tier['trade_price'].loc[coin] = df[coin]['candle_acc_trade_price'].mean()/pow(10,8)
    df_tier['tier_val'] = 10*df_tier['rate'] + df_tier['trade_price']
df_tier = df_tier.sort_values(by='tier_val',ascending=False)
df_tier[:20]


# In[25]:


import sklearn
from sklearn.cluster import KMeans
kmeans = KMeans(n_clusters=10, random_state=0).fit(df_tier[['tier_val']])
df_tier['tier'] = kmeans.labels_

tier_dict = {}
tier_num = 0

def getTier(x,tier_dict):
    global tier_num
    if not tier_dict.get(x):
        tier_dict[x] = tier_num
        tier_num+=1
    return tier_dict[x]

df_tier['tier']=df_tier['tier'].map(lambda x : getTier(x,tier_dict))
df_tier = df_tier.sort_values(by='tier')
df_tier[:20]



# In[27]:


from IPython.core.display import display, HTML
from copy import deepcopy

def makeTierMark(x):
    return '<img src= ' + 'static/image/icon-champtier-'+str(x)+'.png' + ' width=22 height=24>'

def makeHTML(feature_df) :    
    feature_df = deepcopy(feature_df)
    feature_df=feature_df.astype(str)
    #feature_df['img'] = 'https://ssl.pstatic.net/imgfinance/chart/mobile/candle/day/'+feature_df['단축코드']+'_end.png'
    #feature_df['img'] = '<img src = \'' + feature_df['img'] + '\' weight=300 height=200>'
    
    feature_df['티어'] =feature_df['티어'].map(lambda x : makeTierMark(x))

    for index,column in enumerate(feature_df.columns):
        feature_df[column] = 'col'+str(index+1)+feature_df[column]
    
    feature_df.columns = ['1 코인','2 상승률','3 거래액(억)','4 티어']

    f=open('./server/static/header.txt', 'r')
    header = f.read()

    f=open('./server/static/js.txt', 'r')
    js = f.read()

    df_html = feature_df.to_html(escape=False)

    df_html = header + df_html + js

    return df_html


# In[28]:


df_tier = df_tier.drop('tier_val',axis=1)
df_tier = df_tier.reset_index()
df_tier_view = df_tier[['name','rate','trade_price','tier']]


# In[29]:


df_tier_view['rate'] = df_tier_view['rate'].map(lambda x : round(x,2))
df_tier_view['trade_price'] = df_tier_view['trade_price'].map(lambda x : round(x,2))
df_tier_view.columns = ['코인','등락률','거래액(억)','티어']
html = makeHTML(df_tier_view[:20])
html = html.replace('<table border=\"1\" class=\"dataframe\">','<table>')
html=html.replace('<tr','<tr class=\"row100 body\"')

for index,column in enumerate(df_tier.columns):
    html=html.replace('<td>col'+str(index+1),'<td class=\"cell100 column'+str(index+1)+'\">')
    html=html.replace('<th>'+str(index+1)+' ','<th class=\"cell100 column'+str(index+1)+'\">')

# In[30]:


with open('./server/templates/coin_tier.html', 'w',encoding='utf-8') as f:
    f.write(html)

df_json = df_tier[['name','alias','rate','trade_price','tier']]
df_json_rank = df_json.reset_index()
df_json_rank.columns = ['rank','name','alias','rise','volume','tier']
df_json_rank['rank']+=1
df_json_rank = df_json_rank[['name','alias','rise','volume','rank','tier']]


with open('./tier_data/coin_tier.json', 'w', encoding='utf-8') as f:
    df_json_rank.to_json(f, force_ascii=False,orient='records')
