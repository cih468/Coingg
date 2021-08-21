import json
import pandas as pd
import datetime

with open('./tier_data/coin_tier.json', 'r') as f:
        json_data = json.load(f)
df = pd.DataFrame(json_data)
df['date'] = str(datetime.datetime.today()).split()[0]
df.to_csv('tier_data/dataframe/all.csv',mode='a',index=False)
df