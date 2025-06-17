FROM python:3.11-slim

# install tor and haproxy
RUN apt-get update && apt-get install -y tor haproxy

# make the configs
RUN mkdir -p /usr/share/haproxy
RUN mkdir -p /var/lib/tor/hidden_service && \
    chown -R root:root /var/lib/tor
COPY ./haproxy.cfg /etc/haproxy/haproxy.cfg
COPY ./torrc /etc/tor/torrc

# Optional: Install Python deps
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy your Flask app
COPY . /app
WORKDIR /app

# Expose necessary ports (HAProxy, Flask, Tor)
EXPOSE 8080 8000 80

CMD ["bash", "start.sh"]