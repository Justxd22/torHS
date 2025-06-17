#!/bin/bash
set -e

echo "Starting Flask app..."
python3 main.py &

echo "Starting Tor..."
sudo tor &

# Wait a few seconds for Tor to bootstrap
sleep 5

if [ -f /var/lib/tor/hidden_service/hostname ]; then
    echo "Onion address: http://$(cat /var/lib/tor/hidden_service/hostname)"
else
    echo "Onion address not found (Tor may not have generated it yet)."
fi


echo "Starting HAProxy..."
haproxy -f /etc/haproxy/haproxy.cfg -db