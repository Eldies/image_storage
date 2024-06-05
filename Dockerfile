FROM python:3.10-alpine as base-poetry
RUN pip install poetry
RUN poetry config virtualenvs.create false
WORKDIR /src
COPY pyproject.toml ./
RUN poetry export --no-interaction --output requirements.txt

FROM base-poetry as dev
RUN poetry install --no-root --no-interaction --with test,dev

FROM python:3.10-alpine as prod
WORKDIR /src
COPY --from=base-poetry /src/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY ./app app
EXPOSE 5000
CMD uvicorn app.main:app --host 0.0.0.0 --port 5000 --use-colors
