#!/bin/sh

echo "Waiting for redis..."
sleep 5
uvicorn main:app --host 0.0.0.0 --port 8000