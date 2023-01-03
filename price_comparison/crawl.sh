#!/bin/sh
start_datetime=$(date '+%m_%d_%Y_%H_%M_%S')
echo "${start_datetime} - starting scrapping"
cd $(dirname price_comparison/) 
PATH=$PATH:$(dirname $(which scrapy))
export PATH

PYTHON=$(which python)
TIMEOUT=$(which timeout)
CRAWLER=$(readlink -f crawlerCommand.py)
DISCORD=$(readlink -f sendMessageToDiscord.py)
COMPARISON=$(readlink -f comparePrices.py )
$TIMEOUT 900 $PYTHON $CRAWLER
$PYTHON $COMPARISON
$PYTHON $DISCORD
