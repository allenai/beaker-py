FROM python:3.10-alpine

WORKDIR /stage

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install --no-deps .

WORKDIR /app/beaker
RUN rm -rf /stage
