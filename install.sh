#!/bin/bash

docker build -t assignment_image .
docker run -dti --name assignment_container assignment_image
docker exec -ti assignment_container bash -c "./start.py"