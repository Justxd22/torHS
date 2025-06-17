#!/bin/bash
set -e

echo "Starting Flask app..."
python3 main.py &


chmod 700 /var/lib/tor/hidden_service
chown -R root:root /var/lib/tor/hidden_service


echo "Starting Tor..."
tor &

# Wait a few seconds for Tor to bootstrap
sleep 10

if [ -f /var/lib/tor/hidden_service/hostname ]; then
    echo -e "\n\n\n\n##############\n\nOnion address: http://$(cat /var/lib/tor/hidden_service/hostname)\n\n##############\n\n"

else
    echo "Onion address not found (Tor may not have generated it yet)."
fi


echo "Starting HAProxy..."
haproxy -f /etc/haproxy/haproxy.cfg -db