# This script checks if the measurement trips an alert
# I left in the prints in comments for debug purposes

import time
import json
from datetime import datetime
import RPi.GPIO as GPIO
import threading
import buzzers

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Numbers 1 - 6 Are LED's | Numbers 7 - 10 are buzzers
alarmDict = {"1": 14, "2": 15, "3": 18, "4": 23, "5": 24, "6": 25, "7": 8, "8": 7, "9": 12, "10": 16}

# Dictionary used to store the state of the previous alerts. This is needed so that the alert does not get switched off when checking the next alert
previousAlert = {}

# Defination to control the buzzers
def buzzer(pin, songLenght):
	# You can add your buzzer sound in buzzer.py, this way you can give extra variable that would determine the sound played, for PoC we used one sound
	buzzers.main_buzz(int(pin), songLenght)


# Definition that put on certain light
def light(pin, state):
	GPIO.setup(pin, GPIO.OUT)
	GPIO.output(pin, state)


# Definition that checks the alerts previous state and then gives one when necessary
def check_alert(alarmID, state, songLenght):
	##print(state)
	# Check if alert has already been given, if it hasn't give alert, else we do nothing
	if alarmID not in previousAlert and state == 1:
		if int(alarmID) >= 7:
			# Let buzzer run in a thread in the backgorund while script continous
			thread = threading.Thread(target=buzzer, args=(alarmDict[alarmID], songLenght,))
			# Daemonize thread
			thread.daemon = True
			thread.start()
			##buzzer(alarmDict[alarmID])
		else:
			light(alarmDict[alarmID], state)

		# Store the state of the alarmId
		previousAlert[alarmID] = 1
		##print("GPIO: " + str(alarmDict[alarmID]) + " aan")
	##print(previousAlert)


# Main definition that gets called in the other script
def check_alerts(metingen):
	#Variables
	# Dictionary that holds the received measurements
	metingenDict = {}
	# Dictionary to hold the checks of the sensor bounderies
	alertCheck = {}
	# Count to check if alert needs to be given
	countIgnore = 0
	countWarn = 0
	countCrit = 0
	metingen = json.loads(metingen)

	# print the observed measurements
	##print("-----------------------")
	##print("Ontvangen metingen: ")
	for meting in metingen['metingen']:
		if int(meting['status']) == 1:
			metingenDict[meting['sensorId']] = meting['waarde']
			##print(meting['sensorId'] + ": " + str(metingenDict[meting['sensorId']]))

	##print("\n")

	# Lenght variable used for determining the duration of the buzzer
	songLenght = len(metingenDict)

	# Read the alerts that are from Azure Cosmos DB "alarmeringen" collectie
	json_data=open('alerts.json').read()
	JSON = json.loads(json_data)

	##print("Te checken alarmering:")
	# Loop trough the alarmeringen
	for alarm in JSON:

		##print("Naam: " + alarm['naam'])

		# Loop trough the observed measurements
		for k, v in metingenDict.items():
			# Loop trough every sensor in the alarmering and check the bounderies
			# Store result in dictionary: alertCheck
			for grens in alarm['sensoren']:
				if grens['sensorId'] == k:
					# Check for critical first
					if grens['grensKritiekMin'] < v and grens['grensKritiekMax'] > v:
						##kritiek = False
						alertCheck[grens['sensorId']] = "nothing"
					else:
						##kritiek = True
						alertCheck[grens['sensorId']] = True

					# Check for warning, if critical is already true skip else check warning
					# If warning is true set the sensorId key value to false to indicate this further down the script
					# Else we keep it on "nothing"
					if alertCheck[grens['sensorId']] != True:
						if grens['grensMin'] < v and grens['grensMax'] > v:
							##waarschuwing = False
							alertCheck[grens['sensorId']] = "nothing"
						else:
							##waarschuwing = True
							alertCheck[grens['sensorId']] = False

		##print(alertCheck)

		##print("Alarmen die dienen af te gaan:")
		# If alertCheck is empty don't check the alarmering
		if len(alertCheck) != 0:
			for k, v in alertCheck.items():
				if v is True:
					countCrit += 1
				elif v is False:
					countWarn += 1
				else:
					countIgnore += 1

			if alarm['ANDOperator']:
				for soort in alarm['alarmen']:
					if soort['kritiek']:
						# Set alarm off if all are critical or a combination of critical and warning
						if countCrit + countWarn == len(alertCheck) and countIgnore == 0:
							##print("id: " + soort['alarmId'] + "	-> kritiek!")
							# Check alert for its previous state and activate it if necessary with current state
							check_alert(soort['alarmId'], 1, songLenght)
						else:
							check_alert(soort['alarmId'], 0, songLenght)
					elif soort['waarschuwing']:
						# Set alarm of if all warning
						if countWarn == len(alertCheck):
							##print("id: " + soort['alarmId'] + "	-> warning!")
							check_alert(soort['alarmId'], 1, songLenght)
						# Happens when value is critical, so also warning, but critical = false and warning = true. This is because of the count system I use.
						elif countCrit + countWarn == len(alertCheck) and countIgnore == 0:
							check_alert(soort['alarmId'], 1, songLenght)
						else:
							check_alert(soort['alarmId'], 0, songLenght)

			if alarm['ANDOperator'] is False:
				for soort in alarm['alarmen']:
					if soort['kritiek']:
						if countCrit >= 1:
							##print("id: " + soort['alarmId'] + "	-> kritiek!")
							check_alert(soort['alarmId'], 1, songLenght)
						else:
							check_alert(soort['alarmId'], 0, songLenght)
					elif soort['waarschuwing']:
						if countWarn >= 1 or countCrit >= 1:
							##print("id: " + soort['alarmId'] + "	-> warning!")
							check_alert(soort['alarmId'], 1, songLenght)
						else:
							check_alert(soort['alarmId'], 0, songLenght)

			# Reset these variables each alarmering
			alertCheck = {}
			countIgnore = 0
			countWarn = 0
			countCrit = 0
		##print("\n")
	# Reset the previousAlert dict for when the next measurements comes
	previousAlert.clear()