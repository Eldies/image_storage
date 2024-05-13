FROM python:3.10-alpine as base
WORKDIR /src

RUN pip install "poetry==1.5.1"
RUN poetry config virtualenvs.create false
COPY pyproject.toml ./
RUN poetry install --no-root --no-interaction

FROM base as dev
RUN poetry install --no-root --no-interaction --with test,dev

FROM base as prod
COPY ./app app
#ENV PYTHONPATH=/src/:/src/app/
EXPOSE 5000
CMD flask run --host=0.0.0.0
