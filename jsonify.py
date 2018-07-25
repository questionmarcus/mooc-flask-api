#!/usr/bin/env python3
import sys
import json
import datetime
from requests import get

def main():
    args = sys.argv[1:]
    if args[0] == "--web":
        if len(args) == 1:
            urls = ['https://raw.githubusercontent.com/jeremysinger/haskellmooc_logfiles/master/server0.log', 'https://raw.githubusercontent.com/jeremysinger/haskellmooc_logfiles/master/server1.log', 'https://raw.githubusercontent.com/jeremysinger/haskellmooc_logfiles/master/server2.log']
            d = webParse(urls)
        else:
            d = webParse(args[1:])
    else:
        d = logfileParser(sys.argv[1:])
    saveAsJSON("data/logdata.json", d)
    US = userSessions(d)
    saveAsJSON("data/UserSessions.json", US)

def webParse(urls):
    if type(urls) is not list:
        return webParse([urls])
    else:
        data = {}
        for url in urls:
            response = get(url)
            for line in response.text.split("\n")[:-1]:
                user,logdata = lineParser(line)
                if user not in data:
                    data[user] = []
                data[user].append(logdata)
        return data

def logfileParser(files):
    """
    Transforms log data contained in multiple files into a python
    dictionary format in the format:
    {
        "user id0":[{timestamp0, input0},...,{timestampN,inputN}],
        ...
        "user idN":[{timestamp0, input0},...,{timestampN,inputN}]
    }
    
    Keyword Arguments:
    files -- A single file name, or a list of files.
    """
    if type(files) is not list:
        return logfileParser([files])
    else:
        data = {}
        for filepath in files:
            with open(filepath, 'r') as f:
                for line in f:
                    user,logdata = lineParser(line)
                    if user not in data:
                        data[user] = []
                    data[user].append(logdata)
        return data

def lineParser(line):
    """
    Converts individual lines of log files into constituent components.
    Returns the user ID and an opject containing the timestamp and the 
    code written.

    Keyword Arguments:
    line -- String containing a single line from the log file
    """
    try:
        userDate,code = line.split(" > ", 1)
        date,time,tz,user = userDate.split(" ")
    except ValueError:
        print("Unable to split line: "+line)

    # Convert time to ISO8601 datetime string (assume all times UTC)
    datetimeString = '{0}T{1}+0000'.format(date, time)
    return user,{"timestamp":datetimeString,"input":code.strip()}
                
def saveAsJSON(filename, values):
    """
    Creates a file in JSON format from python dictionary object.

    Keyword Arguments:
    filename -- String containing the name of the file (includes filetype)
    values -- Dictionary object containing data to be written to file
    """
    with open(filename, "w") as output:
        output.write(
                json.dumps(
                    values, separators=(',',':')
                    )
                )

def userSessions(data, max_pause_length=10):
    """
    Creates a Python Dictionary object that seperates inputs into sessions
    where the user took a break no longer than the [max_pause_length] minutes

    Keyword Arguments:
    logdata -- Values to break into sessions
    max_pause_length -- Maximum time between inputs (in minutes) before new
    input is start of new session. Optional, defaults to 10 minutes.
    """
    userSessions = {}
    for user in data:
        # Create List of timestamps as datetime objects, which can be sorted
        timestamps = []
        for obj in data[user]:
            # timestamp strings in ISO format
            timestamps.append(datetime.datetime.strptime(
                obj['timestamp'], "%Y-%m-%dT%H:%M:%S.%f%z"
                ))

        # Create variables needed
        sessStart = currTime = prevTime = None
        n = 0
        sessions = []
        session = {}

        # Go through every timestamp in order of appearance
        for time in sorted(timestamps):
            currTime = time
            if not sessStart:
                # if session start not define, (at start of data) define it
                sessStart = currTime
            if prevTime:
                # Once there are two times to compare, calc inter event time
                IET = currTime - prevTime # IET (Inter Event Time)
                if IET > datetime.timedelta(0,60*max_pause_length):
                    # if IET > 10 minutes (600 seconds)
                   n += 1
                   sessTime = prevTime - sessStart
                   session['start'] = sessStart.isoformat()
                   session['end'] = prevTime.isoformat()
                   session['inputs'] = n
                   session['duration (s)'] = (prevTime - sessStart).total_seconds()
                   sessStart = currTime
                   n = 1
                   sessions.append(session)
                   session = {}
                else:
                    n += 1
            prevTime = currTime
        # Once last input is record, define this as end of the session
        session['start'] = sessStart.isoformat()
        session['end'] = prevTime.isoformat()
        session['inputs'] = n
        session['duration (s)'] = (prevTime - sessStart).total_seconds()
        sessions.append(session)
        
        # Add session to dict
        userSessions[user] = sessions
    return userSessions


if __name__ == "__main__":
    main()
