# Python-Azure-sensor-communication
## Wat is het?
Het hoofd script is meting.py. Deze ontvangt een aantal metingen en zal dan kijken of de sensor gekoppeld is en al in Azure voorkomt. Dat staat in de code uitgelegd.
Daarna zal het een ander script importen en kijken of er een alarm overschreden wordt.
Vervolgens zal het elke meting doorsturen naar Azure.

## Installation
Before running the scripts, you must first ensure that you have the following components installed.
* Azure Python SDK
* GPIO
* ...

next you must create a hotspot on which the sensor data can be sended to the Raspberry Pi from an arduino for example. This script uses UDP over a secured Wi-Fi signal.
After that you should run ??? and then you can edit meting.py with your connection string.
Finally, you can run meting.py and check if everything works.

### Checklist
* 1
* 2
* 3
