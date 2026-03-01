FROM python:3.10-alpine AS base-poetry
RUN pip install poetry==2.3.2
RUN poetry self add poetry-plugin-export
RUN poetry config virtualenvs.create false
WORKDIR /src
COPY pyproject.toml ./
RUN poetry export --no-interaction --output requirements.txt --without-hashes

FROM base-poetry AS dev
RUN poetry install --no-root --no-interaction --with test,dev

FROM python:3.10-alpine AS prod
WORKDIR /src
COPY --from=base-poetry /src/requirements.txt ./requirements.txt
RUN pip install --no-compile --no-cache-dir -r requirements.txt
COPY ./app app
EXPOSE 5000
CMD uvicorn app.main:app --host 0.0.0.0 --port 5000 --use-colors
