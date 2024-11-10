# The Docker container needs an pre-build image. It can come from your local filesystem or from Pypi.org
# Please check the DOCKER.md file for building instructions.
#
FROM python:3.11-slim as python3
SHELL ["/bin/bash", "-c"]
ADD dist/SuricataLog-*-py3-none-any.whl .
RUN <<CMD
apt-get update -y
apt-get upgrade -y
apt-get dist-upgrade -y
pip install --no-cache --upgrade setuptools
pip install --no-cache SuricataLog-*-py3-none-any.whl
rm -f SuricataLog-*-py3-none-any.whl
# pip install --no-cache SuricataLog
CMD
VOLUME /suricatalog
RUN ["python3"]
WORKDIR /suricatalog
LABEL "author"="Jose Vicente Nunez <kodegeek.com@protonmail.com>"
