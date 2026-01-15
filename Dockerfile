FROM python:3.14-slim-trixie

ENV PYTHONBUFFERED=1

WORKDIR /app

COPY . /app

RUN pip install .

ENTRYPOINT ["python", "-m", "slack_mr_bot"]
