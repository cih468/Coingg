import pandas as pd
import json

def getCoinData(coin_alias):
    df = pd.read_csv('tier_data/dataframe/all.csv')
    df_coin = df[df['alias']==coin_alias]
    df_coin = df_coin[['rise','volume']]

    json_dict = {}
    for col in df_coin.columns:
        json_dict[col] = json.dumps(list(df_coin[col]))
    return json.dumps(json_dict,ensure_ascii=False)
