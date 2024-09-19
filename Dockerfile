FROM python:3.11-slim as python3
SHELL ["/bin/bash", "-c"]
ADD dist/SuricataLog-*-py3-none-any.whl .
RUN <<CMD
pip install --no-cache SuricataLog-*-py3-none-any.whl
rm -f SuricataLog-*-py3-none-any.whl
CMD
VOLUME /suricatalogs
ENTRYPOINT exec /bin/bash -c $*
LABEL "author"="Jose Vicente Nunez <kodegeek.com@protonmail.com>"
