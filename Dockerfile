FROM python:3.10-slim-bullseye

ENV PATH="${PATH}:/root/.local/bin"

WORKDIR /cosmetics_universe

COPY . /cosmetics_universe

RUN apt update && apt install -y default-libmysqlclient-dev python-dev gcc libpq-dev

RUN pip install --no-cache-dir poetry

RUN poetry config virtualenvs.create false

RUN cd app && poetry install