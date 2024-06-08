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
You can customize these parameters according to your needs.

## Usage
To run the service, simply execute the app.py script. The service will listen by default on port 8443. You can modify the port in the configuration file if necessary.

## API Endpoints

GET /open_cash_drawer

## TODO Endpoints
GET /config: Récupère la configuration actuelle du service.

POST /config: Met à jour la configuration du service en fonction des données JSON fournies.

POST /config/reset: Réinitialise la configuration aux valeurs par défaut.

### Français
# Service Web du Tiroir-Caisse

Ce projet consiste en un service web Flask conçu pour contrôler un tiroir-caisse via un port série.

## Prérequis
Avant d'exécuter ce service, assurez-vous d'avoir installé les dépendances suivantes :

Python 3.x
Flask
pySerial
Vous pouvez installer ces dépendances en exécutant la commande suivante :

```bash
pip install flask pyserial
```

## Configuration
Le service utilise un fichier de configuration config.ini pour définir différents paramètres. Le fichier de configuration est créé automatiquement s'il n'existe pas, avec des valeurs par défaut.

exemple de fichier de configuration :

```bash
; Fichier de configuration pour le Service Web du Tiroir-Caisse

[web_service]
port = 8443
debug = True
log_file = cash_drawer.log
log_level = INFO

[cash_drawer]
port_description = USB-to-Serial
```
Vous pouvez personnaliser ces paramètres selon vos besoins.

## Utilisation
Pour exécuter le service, lancez simplement le script app.py. Le service écoutera par défaut sur le port 8443. Vous pouvez modifier le port dans le fichier de configuration si nécessaire.

## Endpoints de l'API
GET /open_cash_drawer

## TODO Endpoints
GET /config: Récupère la configuration actuelle du service.

POST /config: Met à jour la configuration du service en fonction des données JSON fournies.

POST /config/reset: Réinitialise la configuration aux valeurs par défaut.
