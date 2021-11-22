#!/bin/bash
# expected to be run via cron, cron doesn't include /usr/sbin which is where SS lives
PATH=$PATH:/usr/sbin

APPDIR={{ app_dir }}

source ${APPDIR}/venv/bin/activate
python ${APPDIR}/get_connections.py