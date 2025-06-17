from flask import Flask, request
import ipaddress
import html
import logging
from datetime import datetime
import os

app = Flask(__name__)

# Configure logging
if not os.path.exists('logs'):
    os.makedirs('logs')

# Configure the logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/requests.log'),
        logging.StreamHandler()  # Also log to console
    ]
)
logging.getLogger('werkzeug').setLevel(logging.ERROR)

def extract_circuit_id(proxy_ip):
    try:
        ip = ipaddress.IPv6Address(proxy_ip)
        # Last 32 bits
        words = ip.exploded.split(":")[-2:]
        hex_val = "".join(words)
        return int(hex_val, 16)
    except Exception as e:
        return f"invalid ({e}) Are you sure haproxy is running??"

@app.route('/me')
def me():
    headers = dict(request.headers)
    
    # Extract circuit ID
    tor_circuit_ip_str = headers.get('X-Tor-Circuit-Id')
    circuit_id = extract_circuit_id(tor_circuit_ip_str) if tor_circuit_ip_str else None
    
    # Check for errors
    error = None
    if isinstance(circuit_id, str) and "invalid" in circuit_id:
        error = circuit_id
    
    # Log the request
    app.logger.info(f"Request - {request.path} - {request.remote_addr} - Circuit ID: {circuit_id}")

    if error:
        return error
    
    # Build HTML response
    html_response = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Hidden Service CircuitID</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f4; color: #333; }
            .container { max-width: 800px; margin: auto; background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
            h1, h2 { color: #0056b3; }
            pre { background-color: #eee; padding: 10px; border-radius: 4px; overflow-x: auto; }
            ul { list-style-type: none; padding: 0; }
            li { margin-bottom: 5px; }
            .info-box { background-color: #e9f7ef; border-left: 5px solid #28a745; padding: 15px; margin-top: 20px; border-radius: 4px; }
            .error-box { background-color: #ffeaea; border-left: 5px solid #dc3545; padding: 15px; margin-top: 20px; border-radius: 4px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Helooo there</h1>
            <p>This from python backend served as Tor Hidden Service.</p>
            <h2>Incoming HTTP Headers</h2>
            <p>These are the headers received by the Flask application (after HAProxy has processed them and added the X-Tor-Circuit-ID Header):</p>
            <ul>
    """
    
    # Add each header as a list item
    for key, value in headers.items():
        html_response += f"                <li><strong>{html.escape(key)}:</strong> {html.escape(value)}</li>\n"
    
    html_response += """
            </ul>
    """
    
    # Add Tor Circuit ID Information
    html_response += f"""
            <h2>Tor Circuit ID Information</h2>
            <div class="info-box">
                <p>HAProxy reported Tor Circuit IP: <strong>{html.escape(tor_circuit_ip_str or 'N/A')}</strong></p>
                <p>Extracted Circuit ID: <strong>{circuit_id}</strong></p>
                <p>Request logged at: <strong>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</strong></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_response

@app.route('/')
def root():
    headers = dict(request.headers)
    
    # Extract circuit ID for logging
    tor_circuit_ip_str = headers.get('X-Tor-Circuit-Id')
    circuit_id = extract_circuit_id(tor_circuit_ip_str) if tor_circuit_ip_str else None
    app.logger.info(f"Request - {request.path} - {request.remote_addr} - Circuit ID: {circuit_id}")

    
    response_string = f"Hellooo, there!\n\nIncoming Headers:\n"
    for key, value in headers.items():
        response_string += f"{key}: {value}\n"
    
    return response_string

@app.route('/logs')
def view_logs():
    """Endpoint to view recent logs (for debugging)"""
    try:
        with open('logs/requests.log', 'r') as f:
            logs = f.readlines()[-50:]  # Last 50 lines
        
        log_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Request Logs</title>
            <style>
                body { font-family: monospace; margin: 20px; background-color: #f4f4f4; }
                .container { background-color: #fff; padding: 20px; border-radius: 8px; }
                pre { background-color: #000; color: #fff; padding: 15px; border-radius: 4px; overflow-x: auto; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Recent Request Logs</h1>
                <pre>
        """
        
        for log_line in logs:
            log_html += html.escape(log_line)
        
        log_html += """
                </pre>
            </div>
        </body>
        </html>
        """
        
        return log_html
        
    except FileNotFoundError:
        return "No logs found yet."


@app.route('/onion')
def show_onion():
    try:
        with open('/var/lib/tor/hidden_service/hostname', 'r') as f:
            onion = f.read().strip()
            return f"Your Onion Address: <a href='http://{onion}'>{onion}</a>"
    except Exception as e:
        return f"Unavailable (error: {e})"


if __name__ == "__main__":
    app.run(port=8000)