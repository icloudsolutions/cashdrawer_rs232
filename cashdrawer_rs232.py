import os
from flask import Flask, jsonify
import serial
import serial.tools.list_ports
import time
import logging
import configparser

app = Flask(__name__)

# Get the directory of the executable
executable_dir = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(executable_dir, 'config.ini')

def read_config():
    # Check if the config file exists
    if not os.path.exists(config_file_path):
        # Create a default config file if it doesn't exist
        with open(config_file_path, 'w') as config_file:
            config_file.write("""; Configuration file for Cash Drawer Web Service

; [web_service] section defines settings for the Flask web service
[web_service]
; Port number on which the web service should run
; Default: 8443
port = 8443

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
""")
            logging.info("Default config file created at {}".format(config_file_path))

    config = configparser.ConfigParser()
    config.read(config_file_path)
    return config

def find_cash_drawer():
    config = read_config()
    web_service_port = config.getint('web_service', 'port', fallback=8443)
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

@app.route('/open_cash_drawer', methods=['GET'])
def open_cash_drawer():
    result, status_code = find_cash_drawer()
    return result, status_code

if __name__ == '__main__':
    config = read_config()
    web_service_port = config.getint('web_service', 'port', fallback=8443)
    debug_mode = config.getboolean('web_service', 'debug', fallback=True)
    log_file_path = config.get('web_service', 'log_file', fallback=os.path.join(executable_dir, 'cash_drawer.log'))
    log_level = config.get('web_service', 'log_level', fallback='INFO')
    
    # Convert log level string to integer constant
    log_level = getattr(logging, log_level.upper(), logging.INFO)
    
    logging.basicConfig(filename=log_file_path, level=log_level,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    
    app.run(debug=debug_mode, port=web_service_port)
