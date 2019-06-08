#!/bin/bash

sudo pkill -9 python3
sudo systemctl stop distributedtwitter.service
sudo systemctl start distributedtwitter.service

