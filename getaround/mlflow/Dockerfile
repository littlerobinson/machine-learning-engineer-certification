FROM python:3.12.7-slim-bookworm

# ENV variables
ENV AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
ENV AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
ENV AWS_ARTIFACT_S3_URI=$AWS_ARTIFACT_S3_URI
ENV BACKEND_STORE_URI=$BACKEND_STORE_URI
ENV PIP_ROOT_USER_ACTION=ignore


# Update and install needed packages
RUN apt-get update
RUN apt-get install -y curl unzip git

WORKDIR /mlflow

# Install mlflow and dependencies
COPY requirements.txt .
RUN pip install -r ./requirements.txt

# Install AWS CLI for remote use
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscli.zip"
RUN unzip awscli.zip
RUN ./aws/install
RUN rm awscli.zip
RUN rm -rf ./aws

CMD mlflow server --port $PORT \
    --host 0.0.0.0 \
    --backend-store-uri $BACKEND_STORE_URI \
    --default-artifact-root $AWS_ARTIFACT_S3_URI