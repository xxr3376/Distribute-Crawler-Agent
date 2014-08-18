#!/bin/bash
source .env/bin/activate
exec python app.py $1
