#!/bin/bash
docker build -t philosophyapi:latest . &&

docker run --privileged -it --rm \
    --name philosophyapi \
    -p 5000:5000 \
    --network host \
    philosophyapi:latest 