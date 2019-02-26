# This is a script that listens for messages on IoT Hub, it receives the collections: alarmeringen and gebruikers, in JSON format and stores it in azure/<collection>.json

# Necessary imports
import time
import sys
import iothub_client
from iothub_client import IoTHubClient, IoTHubClientError, IoTHubTransportProvider, IoTHubClientResult
from iothub_client import IoTHubMessage, IoTHubMessageDispositionResult, IoTHubError
import json
import gnupg
import getpass

# Used counters
RECEIVE_CONTEXT = 0
WAIT_COUNT = 10
RECEIVED_COUNT = 0
RECEIVE_CALLBACKS = 0

# Variable to use gnupg
gpg = gnupg.GPG()

# Choose AMQP or AMQP_WS as transport protocol
PROTOCOL = IoTHubTransportProvider.AMQP

def write_json_encrypted(JSON, Password, soort):
	soort = 'azure/' + soort + '.json.gpg'
	# Encrypt the information
	JSONEncrypted = gpg.encrypt(JSON, None, passphrase=Password, symmetric=True)
	# Write the information to a file
	with open(soort, 'w') as outfile:
		outfile.write(str(JSONEncrypted))

	print("Message is stored in: "+ soort)
	print("\n")
	# Prints debug information
	print 'ok: ', JSONEncrypted.ok
	print 'status: ', JSONEncrypted.status
	print 'stderr: ', JSONEncrypted.stderr

def receive_message_callback(message, counter):
	global RECEIVE_CALLBACKS
	message_buffer = message.get_bytearray()
	size = len(message_buffer)
	# print ( "Received Message [%d]:" % counter )
	print("Message received")
	print(message_buffer[:size].decode('utf-8'))
	# Write the JSON to the correct file
	ReceivedJSON = json.loads(message_buffer[:size].decode('utf-8'))

	# Check if the JSON is from the collection "gebruikers" or "alarmeringen"
	if len(ReceivedJSON) != 0:
		if 'alarmen' in ReceivedJSON[0]:
			# Write to alerts.json.gpg
			write_json_encrypted(json.dumps(ReceivedJSON), AlertsPass, 'alerts')
		else:
			# Write to users.json.gpg
			write_json_encrypted(json.dumps(ReceivedJSON), UsersPass, 'users')

	# Part of the original script from azure python sdk github, print the message and other properties the message has
	## print ( "    Data: <<<%s>>> & Size=%d" % (message_buffer[:size].decode('utf-8'), size) )
	## map_properties = message.properties()
	## key_value_pair = map_properties.get_internals()
	## print ( "    Properties: %s" % key_value_pair )
	## counter += 1
	## RECEIVE_CALLBACKS += 1
	## print ( "    Total calls received: %d" % RECEIVE_CALLBACKS )
	return IoTHubMessageDispositionResult.ACCEPTED


def iothub_client_init():
	client = IoTHubClient(str(CONNECTION_C2D), PROTOCOL)

	client.set_message_callback(receive_message_callback, RECEIVE_CONTEXT)

	return client


def print_last_message_time(client):
	try:
		last_message = client.get_last_message_receive_time()
		print ( "Last Message: %s" % time.asctime(time.localtime(last_message)) )
		print ( "Actual time : %s" % time.asctime() )
	except IoTHubClientError as iothub_client_error:
		if iothub_client_error.args[0].result == IoTHubClientResult.INDEFINITE_TIME:
			print ( "No message received" )
		else:
			print ( iothub_client_error )


def iothub_client_sample_run():
	try:
		client = iothub_client_init()

		while True:
			print ( "IoTHubClient waiting for commands, press Ctrl-C to exit" )

			status_counter = 0
			while status_counter <= WAIT_COUNT:
				status = client.get_send_status()
				print ( "Send status: %s" % status )
				time.sleep(10)
				status_counter += 1

	except IoTHubError as iothub_error:
		print ( "Unexpected error %s from IoTHub" % iothub_error )
		return
	except KeyboardInterrupt:
		print ( "IoTHubClient sample stopped" )

	print_last_message_time(client)


if __name__ == '__main__':
	# Get the necessary connection string from the gpg encrypted file config/config.json.gpg
	gpgPass = getpass.getpass("Please provide the passphrase to the gpg encrypted config file: ")
	print("\n")
	# Read the file
	with open('config/config.json.gpg', 'rb') as f:
		# decrypt the file, then get value by turning into string, then loading it as JSON
		d = json.loads(str(gpg.decrypt_file(f, passphrase=gpgPass)))
		for value in d:
			# Needed variables
			CONNECTION_C2D = value['CONNECTION_C2D']
			AlertsPass = value['alertsJson']
			UsersPass = value['usersJson']
	print(CONNECTION_C2D)
	print("Listening for messages on IoT Hub...")
	##print ( "    Connection string=%s" % CONNECTION_C2D )

	iothub_client_sample_run()