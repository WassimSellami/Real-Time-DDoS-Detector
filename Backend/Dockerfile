FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    iputils-ping \
    net-tools \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/cache/apt/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && rm -rf /root/.cache/pip/*

COPY . .

CMD ["python", "main.py"]
