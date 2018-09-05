# mooc-flask-api

This repository contains the flask application used to run the back-end application to the [Glasgow MOOC Visualisation Application](https://questionmarcus.github.io/mooc-visualisation-app)

The current API is hosted at [PythonAnywhere](https://questionmarcus.pythonanywhere.com)

You can see some example data [here](https://questionmarcus.pythonanywhere.com/studypath/2017)

## Requirements
1. The `Flask` and `numpy` libraries
2. JSON data returned from the [server parsing tools](https://www.github.com/questionmarcus/haskellmooc_logfiles)

## Getting started
For local development:
1. Set your flask environment to development: `export FLASK_ENV=development`
2. Make sure you are in the parent directory of this project (the one above the directory with `app.py`)
3. Run `FLASK_APP=mooc-flask-api/app.py flask run` to start the localhost development server
