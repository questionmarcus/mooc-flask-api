from flask import Flask, jsonify, make_response, url_for
import json
import numpy as np
from collections import Counter

app = Flask(__name__)

logData2016 = json.load(open("static/2016-MOOC-logdata.json","r"))
logData2017 = json.load(open("static/2017-MOOC-logdata.json", "r"))

@app.route('/')
def index():
    return "Welome to the Glasgow Haskell MOOC statistics server"

@app.route('/histogram/<int:year>')
def hist(year):
    nCodeLines = []
    if year == 2016:
        for user in logData2016:
            nCodeLines.append(len(logData2016[user]))
    elif year == 2017:
        for user in logData2017:
            nCodeLines.append(len(logData2017[user]))
    else:
        return make_response(("Invalid year entry",404))
    upperLimit = np.max(nCodeLines)
    upperLimitNearestTen = np.ceil(upperLimit/10).astype(int)*10
    hist = np.histogram(nCodeLines, np.arange(0,upperLimitNearestTen,10))
    resp = make_response(jsonify({"data":hist[0].tolist(), "bins":hist[1].tolist()}))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@app.route('/studypath/<int:year>')
def userPath(year):
    count = Counter()
    def pathCount(user):
        nonesRemoved = [x["exercise"]["tutorial"] for x in user if x["exercise"] != None]
        if len(nonesRemoved) != 0:
            path = []
            prev = nonesRemoved[0]
            for tut in nonesRemoved[1:]:
                if tut != prev:
                    path.append((prev,tut))
                    prev = tut
            return path
    if year == 2016:
        for user in logData2016:
            count.update(pathCount(logData2016[user]))
    elif year == 2017:
        for user in logData2017:
            count.update(pathCount(logData2017[user]))
    else:
        return make_response("Invalid year entry", 404)
    out = {"nodes":[
            {"node":0, "name": "Tutorial11"},
            {"node":1, "name": "Tutorial12"},
            {"node":2, "name": "Tutorial2"},
            {"node":3, "name": "Tutorial22"},
            {"node":4, "name": "Tutorial23"},
            {"node":5, "name": "Tutorial31"},
            {"node":6, "name": "Tutorial32"}
        ], "links":[]}
    nodeDic = {"tutorial11":0, "tutorial12":1, "tutorial2":2,
            "tutorial22":3, "tutorial23":4, "tutorial31":5, "tutorial32":6}
    for sourceTarget, val in count.items():
        out["links"].append({
            "source":nodeDic[sourceTarget[0]],
            "target":nodeDic[sourceTarget[1]],
            "value":val})
    return jsonify(out)

if __name__ == "__main__":
    app.run();
