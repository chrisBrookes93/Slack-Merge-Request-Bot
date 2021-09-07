FROM python:3.8-slim-buster

ENV PYTHONBUFFERED=1

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt && pip install .

ENTRYPOINT ["python", "-m", "slack_mr_bot"]
