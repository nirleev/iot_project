#!/bin/bash
username=""
password=""
[ -z "$password" ] && echo please set credentials in script && exit 1
data="date=`date +'%Y-%m-%d %H:%M:%S'`&temperature=${1-$(($RANDOM % 50 + 50))}"
echo "Data: $data"
curl -d "$data" -u "$username:$password" localhost:8080/temp
