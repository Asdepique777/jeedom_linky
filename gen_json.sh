#!/bin/sh
#BASE_DIR="/home/pi/jeedom_linky"
BASE_DIR="./"
export BASE_DIR

. $BASE_DIR/credentials
python3 $BASE_DIR/linky_json.py -o "$BASE_DIR" >> $BASE_DIR/linky.log 2>&1
