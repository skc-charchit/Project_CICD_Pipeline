#!/bin/bash

python mongodb.py
uvicorn src.main:app --host 0.0.0.0 --port 8001
