FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    net-tools \
    iproute2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ENTRYPOINT [ "python" ]

CMD ["main.py"]
