from flask import Flask, jsonify, make_response, url_for
import os
import json
import numpy as np

app = Flask(__name__)

logData2016 = json.load(open("static/2016-MOOC-UserSessions.json","r"))

@app.route('/')
def index():
    return "Welome to the Glasgow Haskell MOOC statistics server"

@app.route('/histogram')
def hist():
    nCodeLines = []
    for user in logData2016:
        nCodeLines.append(len(logData2016[user]))
    upperLimit = np.max(nCodeLines)
    upperLimitNearestTen = np.ceil(upperLimit/10).astype(int)*10
    hist = np.histogram(nCodeLines, np.arange(0,upperLimitNearestTen,10))
    resp = make_response(jsonify({"data":hist[0].tolist(), "bins":hist[1].tolist()}))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

if __name__ == "__main__":
    app.run();
