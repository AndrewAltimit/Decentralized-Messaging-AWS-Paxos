#!/bin/bash

sudo systemctl stop distributedtwitter.service
sudo /usr/bin/pkill -9 python3
sudo /usr/bin/python3 /twitter/src/run_client.py


