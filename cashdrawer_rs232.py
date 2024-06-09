import os
import time
import logging
import ssl
import serial
import configparser
from flask import Flask, jsonify, request, redirect, url_for, render_template
from OpenSSL import crypto
import serial.tools.list_ports

app = Flask(__name__)

# Get the directory of the executable
executable_dir = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(executable_dir, 'config.ini')

# Default configuration content
default_config_content = """; Configuration file for Cash Drawer Web Service

; [web_service] section defines settings for the web service
[web_service]
; Port number on which the web service should run. Default: 8443
port = 8443

[SSL]
certificate_path = 
certificate_key_path = 

[LOG]
; Enable or disable debug mode. Set to True for development, False for production. Default: True
debug = True

; Path to the log file. Specify the location where log messages should be written. Default: cash_drawer.log
log_file = cash_drawer.log

; Logging level for the application. Options: DEBUG, INFO, WARNING, ERROR, CRITICAL. Default: INFO
log_level = INFO

[cash_drawer_port]
; Description of the serial port where the cash drawer is connected. Default: USB-to-Serial
port_description = USB-to-Serial

; Command to open the cash drawer. Default: \x1B\x70\x00\x19\xFA
open_command = \x1B\x70\x00\x19\xFA

baud_rate = 9600

timeout = 1
"""

def read_config():
    # Check if the config file exists, if not, create a default one
    if not os.path.exists(config_file_path):
        with open(config_file_path, 'w') as config_file:
            config_file.write(default_config_content)
            logging.info(f"Default config file created at {config_file_path}")

    config = configparser.ConfigParser()
    config.read(config_file_path)
    return config

def save_config(config):
    with open(config_file_path, 'w') as config_file:
        config.write(config_file)
    logging.info("Config file updated")

def generate_self_signed_cert(cert_path, key_path):
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 2048)
    cert = crypto.X509()
    cert.get_subject().C = "TN"
    cert.get_subject().ST = "whatsup : +21650271737"
    cert.get_subject().L = "contact@icloud-solutions.net"
    cert.get_subject().O = "iCloud Solutions"
    cert.get_subject().OU = "icloud-solutions.net"
    cert.get_subject().CN = "localhost"
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(31536000)  # 1 year
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha256')

    with open(cert_path, "wt") as cert_file:
        cert_file.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode('utf-8'))
    with open(key_path, "wt") as key_file:
        key_file.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k).decode('utf-8'))
    logging.info(f"Self-signed certificate and key generated at {cert_path} and {key_path}")

def find_cash_drawer():
    config = read_config()
    port_description = config.get('cash_drawer_port', 'port_description', fallback='USB-to-Serial')
    baud_rate = config.getint('cash_drawer_port', 'baud_rate', fallback=9600)
    timeout = config.getint('cash_drawer_port', 'timeout', fallback=1)
    open_command = config.get('cash_drawer_port', 'open_command', fallback='\x1B\x70\x00\x19\xFA').encode()

    start_time = time.time()

    for port in serial.tools.list_ports.comports():
        if port_description in port.description:
            try:
                with serial.Serial(port.device, baud_rate, timeout=timeout) as ser:
                    ser.write(open_command)
                    ser.read(2)  # Adjust read size and timeout as needed
                execution_time = time.time() - start_time
                logging.info(f"Cash drawer opened successfully on port {port.device}. Execution time: {execution_time:.2f} seconds")
                return jsonify({'message': f"Cash drawer opened successfully on port {port.device}. Execution time: {execution_time:.2f} seconds"}), 200
            except Exception as e:
                logging.error(f"Error on port {port.device}: {e}")
                return jsonify({'error': f"Error on port {port.device}: {e}"}), 500

    execution_time = time.time() - start_time
    logging.error(f"Could not find the cash drawer. Execution time: {execution_time:.2f} seconds")
    return jsonify({'error': f"Could not find the cash drawer. Execution time: {execution_time:.2f} seconds"}), 404

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/config', methods=['GET', 'POST'])
def config():
    if request.method == 'POST':
        config_content = request.form['config']
        with open(config_file_path, 'w') as config_file:
            config_file.write(config_content)
        return redirect(url_for('config'))
    else:
        with open(config_file_path, 'r') as config_file:
            config_content = config_file.read()
        return render_template('config.html', config=config_content)

@app.route('/config/update', methods=['POST'])
def update_config():
    config = read_config()
    data = request.json

    for section, options in data.items():
        if section not in config:
            config.add_section(section)
        for option, value in options.items():
            config.set(section, option, str(value))

    save_config(config)
    return jsonify({'message': 'Configuration updated successfully'}), 200

@app.route('/config/reset', methods=['POST'])
def reset_config():
    with open(config_file_path, 'w') as config_file:
        config_file.write(default_config_content)
    logging.info("Config file reset")
    return jsonify({'message': 'Configuration reset successfully'}), 200

@app.route('/open_cash_drawer', methods=['GET'])
def open_cash_drawer():
    result, status_code = find_cash_drawer()
    return result, status_code

@app.route('/port')
def port():
    return render_template('port.html')

@app.route('/port/properties', methods=['GET'])
def get_port_properties():
    config = read_config()
    port_description = config.get('cash_drawer_port', 'port_description', fallback='USB-to-Serial')

    for port in serial.tools.list_ports.comports():
        if port_description in port.description:
            port_properties = {
                'name': port.name,
                'description': port.description,
                'device': port.device,
                'hwid': port.hwid,
                'vid': port.vid,
                'pid': port.pid,
                'serial_number': port.serial_number
            }
            return jsonify(port_properties), 200

    return jsonify({'error': 'Selected serial port not found.'}), 404

@app.route('/service')
def service():
    return render_template('service.html')

@app.route('/service/status', methods=['GET'])
def get_service_status():
    return jsonify({'status': 'The web service is running.'}), 200

if __name__ == '__main__':
    config = read_config()
    web_service_port = config.getint('web_service', 'port', fallback=8443)
    debug_mode = config.getboolean('web_service', 'debug', fallback=True)
    log_file_path = config.get('LOG', 'log_file', fallback=os.path.join(executable_dir, 'cash_drawer.log'))
    log_level = config.get('LOG', 'log_level', fallback='INFO')
    certificate_path = config.get('SSL', 'certificate_path', fallback=os.path.join(executable_dir, 'localhost+2.pem'))
    certificate_key_path = config.get('SSL', 'certificate_key_path', fallback=os.path.join(executable_dir, 'localhost+2-key.pem'))

    # Convert log level string to integer constant
    log_level = getattr(logging, log_level.upper(), logging.INFO)

    logging.basicConfig(filename=log_file_path, level=log_level,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    if not certificate_path or not os.path.exists(certificate_path) or not certificate_key_path or not os.path.exists(certificate_key_path):
        logging.warning("SSL certificate or key not found. Generating self-signed certificate.")
        if not certificate_path:
            certificate_path = os.path.join(executable_dir, 'localhost+2.pem')
        if not certificate_key_path:
            certificate_key_path = os.path.join(executable_dir, 'localhost+2-key.pem')
        generate_self_signed_cert(certificate_path, certificate_key_path)

    try:
        context.load_cert_chain(certfile=certificate_path, keyfile=certificate_key_path)
    except FileNotFoundError:
        logging.error("SSL certificate files not found.")
        raise
    except ssl.SSLError as e:
        logging.error(f"An error occurred while loading SSL certificates: {e}")
        raise

    app.run(debug=debug_mode, port=web_service_port, ssl_context=context)
