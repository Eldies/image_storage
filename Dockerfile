ARG VERSION=production

FROM python:3.10-alpine as base
WORKDIR /src
COPY requirements.txt .
RUN pip install -r requirements.txt

FROM base as branch-env-production

FROM base as branch-env-testing
COPY requirements-test.txt .
RUN pip install -r requirements.txt -r requirements-test.txt
COPY ./tests tests

FROM branch-env-${VERSION} as final
COPY ./app app
#ENV PYTHONPATH=/src/:/src/app
EXPOSE 5000

CMD flask run --host=0.0.0.0
