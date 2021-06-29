#!/bin/sh
export FLASK_APP=Client.py
export FLASK_ENV=deployment
python3 -m flask run -p 30003
