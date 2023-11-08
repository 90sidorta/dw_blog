# Dockerfile

# pull the official docker image
FROM python:3.10-slim-bullseye

# set work directory
WORKDIR /fastapi_sqlmodel

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
COPY pyproject.toml .
RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install

# copy project
COPY . .