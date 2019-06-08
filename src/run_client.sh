#!/bin/bash

cd /twitter/
sudo systemctl stop distributedtwitter.service
sudo pkill -9 python3
sudo python3 run_client.py
