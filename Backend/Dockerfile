FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    iputils-ping \
    sudo \
    libpcap-dev \ 
    python3-pip \
    net-tools \
    iptables \
    && apt-get clean && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

WORKDIR /app

COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt \
    && rm -rf /root/.cache/pip/*

COPY . .

RUN chmod +x main.py

CMD ["python", "main.py"]
