FROM python:3.12.7-slim-bookworm AS getaround-api

# ENV AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
# ENV AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
# ENV AWS_ARTIFACT_S3_URI=$AWS_ARTIFACT_S3_URI
ENV MLFLOW_TRACKING_URI=$MLFLOW_TRACKING_URI

ENV PIP_ROOT_USER_ACTION=ignore

WORKDIR /app

RUN apt-get update & apt-get clean

COPY requirements.txt /dependencies/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /dependencies/requirements.txt

COPY ./src /app/src

CMD uvicorn src.main:app --host 0.0.0.0 --port $PORT