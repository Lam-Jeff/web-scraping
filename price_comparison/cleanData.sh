#!/bin/sh
start_datetime=$(date '+%m_%d_%Y_%H_%M_%S')
echo "${start_datetime} - starting cleaning"
find data/* -mtime +7 -exec rm {} \;
find logs/* -mtime +7 -exec rm {} \;