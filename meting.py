# This receives the messages from the Arduino hub and processes each message.
# It sends it to the receive.py script to determine the activation of the light or buzzer
# It then sends the message to IoT Hub for storage in Cosmos DB and to display in the dashboard

# Necessary imports
from iothub_client import IoTHubClient, IoTHubTransportProvider, IoTHubMessage
import time
import socket
import json
from datetime import datetime
import os.path
import RPi.GPIO as GPIO

# Temp variables for testing
sensorenJSON = {}

# Variables fot the connection to the wifi module hub
localIP     = "10.3.141.1"
Port1       = 4001
bufferSize  = 1024
count = 0

# Variables for the connection to Azure IoT Hub
CONNECTION_STRING = "HostName=secodaHub.azure-devices.net;DeviceId=secodaPib;SharedAccessKey=4OS5jUxsttf4ouMY0CdPxnI4cz+k36TDt+SHR6KnguI="
PROTOCOL = IoTHubTransportProvider.MQTT

# Create a datagram socket
UDPServerSocket1 = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
##UDPServerSocket1.bind((localIP, Port1))


# Shows the feedback result from Azure IoT Hub - 'OK' is the feedback you want
def send_confirmation_callback(message, result, user_context):
	print("Confirmation received for message with result = %s" % (result))


# Converts a date so it can be JSON serialized
def date_converter(o):
    if isinstance(o, datetime):
        return o.__str__()

# Sends the json to azure IoT Hub
def send_azure_message(azureJSON):
	# Establish the connection binding
	##ORIGINAL##client = IoTHubClient(CONNECTION_STRING, PROTOCOL)

	##client = IoTHubClient(CONNECTION_STRING, PROTOCOL)
	##message = IoTHubMessage(azureJSON)
	##client.send_event_async(message, send_confirmation_callback, None)
	print("Message transmitted to IoT Hub")
	print("Message that was send: {}".format(azureJSON))
	time.sleep(1)


# Checks if the sensors are connected or not and updates Azure accordingly
def CheckSensors(messages):
	# This will check the following scenario's
	# 1: sensorId in file and status: 1 		--> Connected and present in Azure Cosmos DB		--> Move on
	# 2: sensorId in file and status: 0 		--> Not connected and present in Azure Cosmos DB	--> Update Azure
	# 3: sensorId not in file and status: 1		--> Newly connected not present in Azure Cosmos DB	--> Update Azure
	# 4: sensorId not in file and status: 0		--> Not connected and not present in Azure Cosmos	--> Move on
	## A connected sensor should always display scenario 1, after going trough scenario 3
	## A disconnected sensor should always display scenario 4, after going trough scenario 2

	# Variables
	countInFile = 0
	countNotInFile = 0
	sensorFileDict = {}

	# Checks first if the file exist. If not created new and put first sensor in it
	# If it already exists, move trough the usual path
	fileCheck = os.path.isfile('sensor.json')
	##print(fileCheck)

	if fileCheck is False:
		for meting in messages['metingen']:
			if meting['status'] == 1:
				sensorenJSON[meting['sensorId']] = "Connected"

		# Write the data to a local file
		with open('sensor.json', 'w') as outfile:
			json.dump(sensorenJSON, outfile)
			# Also update Azure
	else:
		# Read the data from a local file
		with open('sensor.json') as f:
			current = json.loads(f.read())
			print(current)
			##print ("\n")

		for meting in messages['metingen']:
			for k, v in current.items():
				if meting['status'] == 1:
					if meting['sensorId'] == k:
						countInFile += 1
					else:
						countNotInFile += 1
				else:
					if meting['sensorId'] == k:
						countInFile -= 1
					else:
						countNotInFile -= 1
			if countInFile == 1:
				## This can be ignored, nothing needs to be done
				##print(meting['sensorId'] + ": scenario 1")
				sensorFileDict[meting['sensorId']] = "Connected"
			elif countNotInFile > 1:
				## Add sensor to file and send update to Azure
				##print(meting['sensorId'] + ": scenario 3")
				sensorFileDict[meting['sensorId']] = "Connected"
			#elif countInFile == -1:
				## Remove sensor from file and send update to Azure
				##print(meting['sensorId'] + ": scenario 2")
			#elif countNotInFile < - 1:
				## This can be ignored, nothing needs to be done
				##print(meting['sensorId'] + ": scenario 4")

			# Reset variables
			countInFile = 0
			countNotInFile = 0

		with open('sensor.json', 'w') as resultFile:
			json.dump(sensorFileDict, resultFile)
			##print(sensorFileDict)
		##print("\n")


print("UDP server up and listening")

# Main method
if __name__ == '__main__':
	try:
		while(True):
			# This waits untill a message is received, only then it will go further with the other code
			##bytesAddressPair1 = UDPServerSocket1.recvfrom(bufferSize)
			# This contains the JSON send from all the sensors at a given time
			##resultJSON = bytesAddressPair1[0]
			# This contains the address and port the message came from
			##address1 = bytesAddressPair1[1]
			JSONTemp = {"metingen":[{"sensorId":"t1","waarde":25, "status": 1},{"sensorId":"a1","waarde":23.70, "status": 1},{"sensorId":"h1","waarde":27.30, "status": 1}]}
			JSON = json.dumps(JSONTemp)

			# Check if the message is the test message to establish connection ("AT"), if so ignore it
			if JSON[:1] != 'A':
				# Convert the received message in JSON that Python can read
				JSONP = json.loads(JSON)

				# Use function in other script to evaluate the alerts
				# This only evaluates the messages where the sensorId status = 1
				import alerts
				alerts.check_alerts(JSONP)
				##count += 1

				# Check local file to see if a sensor has already been connected
				CheckSensors(JSONP)

				##time.sleep(2)

				# Iterate over the different measurements and convert them to an Azure JSON format
				for meting in JSONP['metingen']:
					# status 1 means the sensor is connected
					if meting['status'] == 1:
						#print(meting)

						#Define variables to send with each measurement
						date = datetime.now()
						messageId = str(meting['sensorId']) + date.strftime("%Y%m%d%H%M%S%f").translate(None, ':-').replace(" ", "")

						# Convert the Arduino JSON to Azure JSON and add some values according 
						AzureJSON = {'messageId': messageId, 'sensorId': meting['sensorId'], 'waarde': meting['waarde'], 'tijdstip': date, 'status': meting['status']}

						# Convert the AzureJSON to JSON that Azure can send
						result = json.dumps(AzureJSON, default = date_converter)

						##clientIP1  = "Client IP Address:{}".format(address1)
						##print("\n")
						##print("Message received from: {}".format(clientIP1))

						# Establish the connection binding
						##client = IoTHubClient(CONNECTION_STRING, PROTOCOL)
						##message = IoTHubMessage(result)
						##client.send_event_async(message, send_confirmation_callback, None)
						##print("Message transmitted to IoT Hub")
						##print("Message that was send: {}".format(result))

						## NEW TESTED WAY TO SEND TO AZURE
						send_azure_message(result)
						print("\n")

						# Sleep 1 second between sending messages
						# This has two benefits: you don't overload IoTHub and you make sure the messageId is truly unique
						# Normally the messageId is unique because it is a combination of the sensorId and the date down to the millisecond in numbers
						# But you can never be to sure
						time.sleep(1)

				##print(str(count))

			else:
				print("Ignored message")
				print("\n")

	except KeyboardInterrupt:
		GPIO.cleanup()
		print("\n")
		print ("Program Executed")
