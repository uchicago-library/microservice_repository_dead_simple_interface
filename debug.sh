#!/bin/sh

APP_SAVE=$FLASK_APP
export FLASK_APP=dead_simple_interface
python -m flask run
export FLASK_APP=$APP_SAVE
