#!/bin/bash

# make sure line endings are set to LF

cd /app
/usr/local/bin/python3 manage.py ingest_csv
