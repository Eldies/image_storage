ARG VERSION=production

FROM python:3.10-alpine as base
WORKDIR /src
COPY requirements.txt .
RUN pip install -r requirements.txt

FROM base as branch-env-production

FROM base as branch-env-testing
COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt
COPY ./tests tests

FROM branch-env-${VERSION} as final
COPY ./app app
EXPOSE 5000

CMD flask run --host=0.0.0.0
