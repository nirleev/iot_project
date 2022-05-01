#!/bin/bash
data="date=`date +'%Y-%m-%d %H:%M:%S'`&temperature=${1-$(($RANDOM % 50 + 50))}"
echo "Data: $data"
curl -d "$data" localhost:8080/temp
