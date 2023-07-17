FROM python:3.10-alpine

WORKDIR /stage

COPY . .
RUN pip install --upgrade pip wheel build
RUN pip install --no-cache-dir .

WORKDIR /app/beaker
RUN rm -rf /stage
