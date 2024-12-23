FROM python:3.12.7-slim-bookworm AS getaround-api-jedha

ENV MLFLOW_TRACKING_URI=$MLFLOW_TRACKING_URI

ENV PIP_ROOT_USER_ACTION=ignore

WORKDIR /app

RUN apt-get update && apt-get clean

COPY requirements.txt /dependencies/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /dependencies/requirements.txt

COPY ./src /app/src

CMD uvicorn src.main:app --host 0.0.0.0 --port $PORT