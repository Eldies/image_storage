ARG VERSION=production

FROM python:3.10-alpine as base

FROM base as branch-env-production
COPY requirements.txt .
RUN pip install -r requirements.txt

FROM base as branch-env-testing
COPY requirements.txt .
COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt

FROM branch-env-${VERSION} as final
COPY . .
EXPOSE 5000
CMD flask run --host=0.0.0.0
