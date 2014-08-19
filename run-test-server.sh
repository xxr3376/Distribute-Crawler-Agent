#!/bin/bash
. sample-server/.env/bin/activate
. .env/bin/activate

python test-server.py
