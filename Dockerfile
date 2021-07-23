# Container image that runs your code
FROM python:3.8-alpine
# installs git on container
RUN apk update
RUN apk add git
# Copies your code file from your action repository to the filesystem path `/` of the container
COPY . /action
RUN pip install -r /action/requirements.txt

# Code file to execute when the docker container starts up (`entrypoint.sh`)
ENTRYPOINT ["/action/entrypoint.sh"]
