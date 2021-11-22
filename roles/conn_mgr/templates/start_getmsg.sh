#!/bin/bash

APPDIR={{ app_dir }}

source ${APPDIR}/venv/bin/activate
python ${APPDIR}/threaded_getmsg.py