FROM python:3.11-slim

# install tor and haproxy
RUN apt-get update && apt-get install -y tor haproxy

# make the configs
COPY ./haproxy.cfg /etc/haproxy/haproxy.cfg
COPY ./torrc /etc/tor/torrc

# Optional: Install Python deps
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy your Flask app
COPY main.py /app
WORKDIR /app

# Expose necessary ports (HAProxy, Flask, Tor)
EXPOSE 8080 8000 80

CMD ["bash", "start.sh"]