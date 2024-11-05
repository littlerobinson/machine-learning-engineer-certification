FROM python:3.12.7-slim-bookworm AS getaround-mlflow-jedha

ENV PIP_ROOT_USER_ACTION=ignore

# Update and install needed packages
RUN apt-get update
RUN apt-get install -y curl unzip git

WORKDIR /mlflow

# Install mlflow and dependencies
COPY requirements.txt .
RUN pip install -r ./requirements.txt


CMD mlflow server --port $PORT \
    --host 0.0.0.0