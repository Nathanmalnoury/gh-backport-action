# Container image that runs your code
FROM python:3.8-slim-buster

# Copies your code file from your action repository to the filesystem path `/` of the container
COPY src/main.py /main.py

# Code file to execute when the docker container starts up (`entrypoint.sh`)

ENTRYPOINT ["python", "main.py"]
