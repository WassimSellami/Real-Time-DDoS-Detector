FROM python:3.9.21-alpine3.20

RUN apk add --no-cache \
    iputils \
    net-tools

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "display_app.py"]
