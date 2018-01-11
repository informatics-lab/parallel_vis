#! /bin/bash


dask-scheduler --port 8786 &

if [ -z "$PUBLIC_IP" ]
then
    bokeh serve --port 8888 /opt/app/app/documents/*
else
    bokeh serve --allow-websocket-origin $PUBLIC_IP:8888 --port 8888 /opt/app/app/documents/*
fi