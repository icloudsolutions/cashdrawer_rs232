### English

# Cash Drawer Web Service

This project is a Flask web service designed to control a cash drawer via a serial port.

## Prerequisites

Before running this service, make sure you have installed the following dependencies:

- Python 3.x
- Flask
- pySerial

You can install these dependencies by running the following command:

```bash
pip install flask pyserial

```

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

