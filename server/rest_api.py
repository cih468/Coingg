from flask import Flask
from flask import jsonify
from flask import render_template
import json
import getCoinDataFromDB

app = Flask (__name__)
app.config['JSON_AS_ASCII'] = False


@app.route('/') 
def coin_tier_view():
    return render_template('coin_tier.html')
 
@app.route('/coin/tierlist',methods=['GET'])
def coinTier():
    with open('./tier_data/coin_tier.json', 'r') as f:
        json_data = json.load(f)
    return json.dumps(json_data,ensure_ascii=False)

@app.route('/coin/<coinName>',methods=['GET'])
def coinData(coinName):
    return getCoinDataFromDB.getCoinData(coinName)
    
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000)