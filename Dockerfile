FROM python:3.12-slim-bookworm

ENV PYTHONBUFFERED=1

WORKDIR /app

COPY . /app

RUN pip install .

ENTRYPOINT ["python", "-m", "slack_mr_bot"]
