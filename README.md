### English

# Cash Drawer Web Service

This project is a Flask web service designed to control a cash drawer via a serial port.

## Prerequisites

Before running this service, make sure you have installed the following dependencies:

- Python 3.x
- Flask
- pySerial
- ...

You can install these dependencies by running the following command:

```bash
pip install flask pyserial

```
## Features :

# Directory Setup and Configuration Management:
The application initializes directories for configuration, certificates, and logs under the user's home directory.
It sets up a default configuration file if it doesn't exist.

# Configuration Handling:
Functions are provided to read and write the configuration file (read_config and save_config).
The configuration file holds settings for the web service, SSL, logging, and cash drawer communication.

# SSL Certificate Management:
A function to generate a self-signed SSL certificate if one isn't provided or found.

# Cash Drawer Communication:
The find_cash_drawer function scans serial ports to find the cash drawer based on a description in the configuration and sends a command to open it.

## Configuration
The service uses a config.ini configuration file to define various parameters. The configuration file is automatically created if it does not exist, with default values.

```bash
; Configuration file for Cash Drawer Web Service

[web_service]
port = 8443
debug = True
log_file = cash_drawer.log
log_level = INFO

[cash_drawer]
port_description = USB-to-Serial
```
You can customize these parameters according to your needs.

## Usage
To run the service, simply execute script. The service will listen by default on port 8443. You can modify the port in the configuration file if necessary.

## API Endpoints
GET /open_cash_drawer : open the cash drawer.

GET /config: Récupère la configuration actuelle du service.

POST /config: Met à jour la configuration du service en fonction des données JSON fournies.

POST /config/reset: Réinitialise la configuration aux valeurs par défaut.
# Routes:

Home: Renders the home page.
View Config: Displays the current configuration in JSON format.
Update Config: Updates the configuration from a JSON payload.
Reset Config: Resets the configuration to default values.
Open Cash Drawer: Attempts to open the cash drawer.
Get Port Properties: Returns properties of the serial port matching the description.




## TODO Endpoints
verify and adjust root and webpages home, service, config..


