import os
from flask import Flask, jsonify, request
import serial
import serial.tools.list_ports
import time
import logging
import configparser
import ssl
from OpenSSL import crypto

app = Flask(__name__)

# Get the directory of the executable
executable_dir = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(executable_dir, 'config.ini')

# Default configuration content
default_config_content = """; Configuration file for Cash Drawer Web Service

; [web_service] section defines settings for the Flask web service
[web_service]
; Port number on which the web service should run
; Default: 8443
port = 8443

[SSL]
certificate_path = 
certificate_key_path = 

; Enable or disable debug mode
; Set to True for development, False for production
; Default: True
debug = True

; Path to the log file
; Specify the location where log messages should be written
; Default: cash_drawer.log
log_file = cash_drawer.log

; Logging level for the application
; Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
; Default: INFO
log_level = INFO

; [cash_drawer] section defines settings specific to the cash drawer
[cash_drawer]
; Description of the serial port where the cash drawer is connected
; This should match the description of the USB-to-Serial port
; Default: USB-to-Serial
port_description = USB-to-Serial
"""

def read_config():
    # Check if the config file exists
    if not os.path.exists(config_file_path):
        # Create a default config file if it doesn't exist
        with open(config_file_path, 'w') as config_file:
            config_file.write(default_config_content)
            logging.info("Default config file created at {}".format(config_file_path))

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
    cash_drawer_port_description = config.get('cash_drawer', 'port_description', fallback='USB-to-Serial')
    
    # Start timing
    start_time = time.time()
    
    # Iterate over all available serial ports
    for port in serial.tools.list_ports.comports():
        # Check if the port description contains the desired string
        if cash_drawer_port_description in port.description:
            try:
                # Open serial port
                ser = serial.Serial(port.device, 9600, timeout=1)
                
                # The command to open the cash drawer.
                # This command may vary depending on the manufacturer.
                command = b'\x1B\x70\x00\x19\xFA'
                
                # Send the command to the cash drawer
                ser.write(command)
                
                # Read response or wait to ensure command execution
                response = ser.read(2)  # Adjust read size and timeout as needed
                
                # Close the serial port
                ser.close()
                
                # Stop timing
                end_time = time.time()
                execution_time = end_time - start_time
                
                logging.info(f"Cash drawer opened successfully on port {port.device}. Execution time: {execution_time:.2f} seconds")
                return jsonify({'message': f"Cash drawer opened successfully on port {port.device}. Execution time: {execution_time:.2f} seconds"}), 200
            
            except Exception as e:
                logging.error(f"Error on port {port.device}: {e}")
                return jsonify({'error': f"Error on port {port.device}: {e}"}), 500
    
    # If cash drawer is not found
    end_time = time.time()
    execution_time = end_time - start_time
    logging.error(f"Could not find the cash drawer. Execution time: {execution_time:.2f} seconds")
    return jsonify({'error': f"Could not find the cash drawer. Execution time: {execution_time:.2f} seconds"}), 404

@app.route('/config', methods=['GET'])
def view_config():
    config = read_config()
    return jsonify(config._sections), 200

@app.route('/config', methods=['POST'])
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

@app.route('/port', methods=['GET'])
def get_port_properties():
    config = read_config()
    cash_drawer_port_description = config.get('cash_drawer', 'port_description', fallback='USB-to-Serial')
    
    for port in serial.tools.list_ports.comports():
        if cash_drawer_port_description in port.description:
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

@app.route('/status', methods=['GET'])
def get_service_status():
    return jsonify({'status': 'The web service is running.'}), 200

if __name__ == '__main__':
    config = read_config()
    web_service_port = config.getint('web_service', 'port', fallback=8443)
    debug_mode = config.getboolean('web_service', 'debug', fallback=True)
    log_file_path = config.get('web_service', 'log_file', fallback=os.path.join(executable_dir, 'cash_drawer.log'))
    log_level = config.get('web_service', 'log_level', fallback='INFO')
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
