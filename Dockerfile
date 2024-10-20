# You can also build a container using the whell house from Pypi, see below
FROM python:3.11-slim as python3
SHELL ["/bin/bash", "-c"]
ADD dist/SuricataLog-*-py3-none-any.whl .
RUN <<CMD
pip install --no-cache SuricataLog-*-py3-none-any.whl
rm -f SuricataLog-*-py3-none-any.whl
# pip install --no-cache SuricataLog
CMD
VOLUME /suricatalog
RUN ["python3"]
WORKDIR /suricatalog
LABEL "author"="Jose Vicente Nunez <kodegeek.com@protonmail.com>"
