FROM python:3.12.7-slim-bookworm AS getaround-dashboard-jedha

WORKDIR /app

RUN apt-get update && apt-get install -y curl && apt-get clean

COPY . /app

RUN pip install -r requirements.txt

CMD streamlit run src/streamlit_app.py --server.port $PORT --server.address=0.0.0.0