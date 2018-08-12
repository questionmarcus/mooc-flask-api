from flask import Flask, jsonify, make_response, url_for
import json
import os
import numpy as np
from collections import Counter

app = Flask(__name__)

proj_dir = os.path.realpath(os.path.dirname(__name__))

log2016path = os.path.join(proj_dir, "mooc-flask-api","static", "2016-MOOC-logdata.json")
log2017path = os.path.join(proj_dir, "mooc-flask-api","static", "2017-MOOC-logdata.json")
sessions2016path = os.path.join(proj_dir, "mooc-flask-api","static", "2016-MOOC-UserSessions.json")
sessions2017path = os.path.join(proj_dir, "mooc-flask-api","static", "2017-MOOC-UserSessions.json")

logData2016 = json.load(open(log2016path,"r"))
logData2017 = json.load(open(log2017path, "r"))

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

@app.route('/')
def index():
    return "Welome to the Glasgow Haskell MOOC statistics server"

@app.route('/histogram/<year>')
def hist(year):
    nCodeLines = []
    if year == "2016":
        for user in logData2016:
            nCodeLines.append(len(logData2016[user]))
    elif year == "2017":
        for user in logData2017:
            nCodeLines.append(len(logData2017[user]))
    elif year == "All":
        for user in logData2016:
            nCodeLines.append(len(logData2016[user]))
        for user in logData2017:
            nCodeLines.append(len(logData2017[user]))
    else:
        return make_response(("Invalid year entry",404))
    upperLimit = np.max(nCodeLines)
    if upperLimit > 500:
        upperLimitNearestTwenty = np.ceil(upperLimit/20).astype(int)*20
        hist = np.histogram(nCodeLines, np.arange(0,upperLimitNearestTwenty,20))
    else:
        upperLimitNearestTen = np.ceil(upperLimit/10).astype(int)*10
        hist = np.histogram(nCodeLines, np.arange(0,upperLimitNearestTen,10))
    resp = make_response(jsonify({"data":hist[0].tolist(), "bins":hist[1].tolist()}))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@app.route('/studypath/<year>')
def userPath(year):
    count = Counter()
    if year == "2016":
        for user in logData2016:
            count.update(pathCount(logData2016[user]))
    elif year == "2017":
        for user in logData2017:
            count.update(pathCount(logData2017[user]))
    elif year == "All":
        for user in logData2016:
            count.update(pathCount(logData2016[user]))
        for user in logData2017:
            count.update(pathCount(logData2017[user]))
    else:
        return make_response("Invalid year entry", 404)
    out = {"nodes":[
            {"name": "Tutorial11"},
            {"name": "Tutorial12"},
            {"name": "Tutorial2"},
            {"name": "Tutorial22"},
            {"name": "Tutorial23"},
            {"name": "Tutorial31"},
            {"name": "Tutorial32"}
        ], "links":[]}
    nodeDic = {"tutorial11":0, "tutorial12":1, "tutorial2":2,
            "tutorial22":3, "tutorial23":4, "tutorial31":5, "tutorial32":6}
    for sourceTarget, val in count.items():
        if sourceTarget[0] < sourceTarget[1]:
            out["links"].append({
                "source":nodeDic[sourceTarget[0]],
                "target":nodeDic[sourceTarget[1]],
                "value":val})
    resp = make_response(jsonify(out))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@app.route('/studypath/<year>/reverse')
def userReversePath(year):
    count = Counter()
    if year == "2016":
        for user in logData2016:
            count.update(pathCount(logData2016[user]))
    elif year == "2017":
        for user in logData2017:
            count.update(pathCount(logData2017[user]))
    elif year == "All":
        for user in logData2016:
            count.update(pathCount(logData2016[user]))
        for user in logData2017:
            count.update(pathCount(logData2017[user]))
    else:
        return make_response("Invalid year entry", 404)
    out = {"nodes":[
            {"name": "Tutorial11"},
            {"name": "Tutorial12"},
            {"name": "Tutorial2"},
            {"name": "Tutorial22"},
            {"name": "Tutorial23"},
            {"name": "Tutorial31"},
            {"name": "Tutorial32"}
        ], "links":[]}
    nodeDic = {"tutorial11":0, "tutorial12":1, "tutorial2":2,
            "tutorial22":3, "tutorial23":4, "tutorial31":5, "tutorial32":6}
    for sourceTarget, val in count.items():
        if sourceTarget[0] > sourceTarget[1]:
            out["links"].append({
                "source":nodeDic[sourceTarget[0]],
                "target":nodeDic[sourceTarget[1]],
                "value":val})
    resp = make_response(jsonify(out))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@app.route("/timeline/<year>")
def timeline(year):
    timestamps = []
    if year == "2016":
        for user in logData2016:
            temp = []
            for obj in logData2016[user]:
                temp.append(obj["timestamp"][:10])
            timestamps.extend(set(temp))
    elif year == "2017":
        for user in logData2017:
            temp = []
            for obj in logData2017[user]:
                temp.append(obj["timestamp"][:10])
            timestamps.extend(set(temp))
    elif year == "All":
        for user in logData2016:
            temp = []
            for obj in logData2016[user]:
                temp.append(obj["timestamp"][:10])
            timestamps.extend(set(temp))
        for user in logData2017:
            temp = []
            for obj in logData2017[user]:
                temp.append(obj["timestamp"][:10])
            timestamps.extend(set(temp))
    else:
        return make_response("Invalid year entry", 404)
    counts = Counter(timestamps)
    output = []
    for (d,val) in counts.items():
        output.append({"date":d,"value":val})

    resp = make_response(jsonify(output))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@app.route("/tutorialcompletion/<year>")
def completion(year):
    allTutorials = set(["tutorial11","tutorial12","tutorial2",
        "tutorial22","tutorial23","tutorial31","tutorial32"])
    count = Counter()
    if year == "2016":
        for user in logData2016:
            accessed = set(
                [x["exercise"]["tutorial"] for x in logData2016[user] if x["exercise"] != None]
                )
            if accessed == allTutorials:
                accessed.add("All")
            count.update(accessed)
        numUsers = len(logData2016)
    elif year == "2017":
        for user in logData2017:
            accessed = set(
                [x["exercise"]["tutorial"] for x in logData2017[user] if x["exercise"] != None]
                    )
            if accessed == allTutorials:
                accessed.add("All")
            count.update(accessed)
        numUsers = len(logData2017)
    elif year == "All":
        for user in logData2016:
            accessed = set(
                [x["exercise"]["tutorial"] for x in logData2016[user] if x["exercise"] != None]
                    )
            if accessed == allTutorials:
                accessed.add("All")
            count.update(accessed)
        for user in logData2017:
            accessed = set(
                [x["exercise"]["tutorial"] for x in logData2017[user] if x["exercise"] != None]
                    )
            if accessed == allTutorials:
                accessed.add("All")
            count.update(accessed)
        numUsers = len(logData2016) + len(logData2017)
    else:
        return make_response(("Invalid year entry",404))
    output = {}
    countArr = [{"name":x[0], "num_accessed":x[1]} for x in count.items()]
    output["tutorial_numbers"] = countArr
    output["total_users"] = numUsers
    resp = make_response(jsonify(output))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

if __name__ == "__main__":
    app.run();
