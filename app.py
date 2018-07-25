from flask import Flask, jsonify, make_response
import json
import numpy as np

app = Flask(__name__)

with open("data/logdata.json", "r") as f1:
    data = json.loads(f1.readlines()[0])

@app.route('/')
def index():
    return "Welome to the Glasgow Haskell MOOC statistics server"

@app.route('/histogram')
def hist():
    nCodeLines = []
    for user in data:
        nCodeLines.append(len(data[user]))
    upperLimit = np.max(nCodeLines)
    upperLimitNearestTen = np.ceil(upperLimit/10).astype(int)*10
    hist = np.histogram(nCodeLines, np.arange(0,upperLimitNearestTen,10))
    resp = make_response(jsonify({"data":hist[0].tolist(), "bins":hist[1].tolist()}))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp
    

if __name__ == "__main__":
    app.run();
