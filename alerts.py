# This script checks if the measurement trips an alert
# I left in the prints in comments for debug purposes

import time
import json
from datetime import datetime
import RPi.GPIO as GPIO
import threading
import buzzers
import configmail
import os.path
from twilio.rest import Client

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Twilio variables
account_sid = 'AC1ec93f6749d8550149b9ac36dbcea09c'	# Found on Twilio Console Dashboard
auth_token = '706f5182bb49697264d802cb469477aa'		# Found on Twilio Console Dashboard
myPhone = '+32478774497'							# Phone number you used to verify your Twilio account
TwilioNumber = '+32460207640'						# Phone number given to you by Twilio
client = Client(account_sid, auth_token)			# Initialize the connection

# Numbers 1 - 6 Are LED's | Numbers 7 - 10 are buzzers
alarmDict = {"1": 14, "2": 15, "3": 18, "4": 23, "5": 24, "6": 25, "7": 8, "8": 7, "9": 12, "10": 16}

# Dictionary used to store the state of the previous alerts. This is needed so that the alert does not get switched off when checking the next alert
previousAlert = {}

# Dictionary that holds the alarmeringen that have had an email send while it is still not in normal values
alarmeringenJSON = {}

# Definition to control the buzzers
def buzzer(pin, songLenght):
	# You can add your buzzer sound in buzzer.py, this way you can give extra variable that would determine the sound played, for PoC we used one sound
	buzzers.main_buzz(int(pin), songLenght)


# Definition that put on certain light
def light(pin, state):
	GPIO.setup(pin, GPIO.OUT)
	GPIO.output(pin, state)


# Definition used for sending an e-mail
def send_email(subject, msg):
    try:
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.ehlo()
        server.starttls()
        server.login(configmail.EMAIL_ADDRESS, configmail.PASSWORD)
        message = 'Subject: {}\n\n{}'.format(subject, msg)
        server.sendmail(configmail.EMAIL_ADDRESS, 'bobby1fonken@gmail.com', message)
        server.quit()
        print("Success: Email sent!")
    except:
        print("Email failed to send.")
	time.sleep(1)


# Definition that checks and builds the necessary e-mail body and then sends it
def check_email(alarmNaam, sensorWaarden):
	sbjct = alarmNaam
	message = "Beste\nAlarmering: " + alarmNaam + ", is afgegaan.\nVolgende sensoren hebben hun grens overschreden:\n"
	for k, v in sensorWaarden.items():
		message += str(k) + ": " + str(v) + "\n"
	message += "\nGa naar LINK voor verdere opvolging!"
	print(message)
	send_email(sbjct, message)

# Definition that sends a text message with Twilio
def send_sms(msg):
	sms = client.messages.create(
		to=myPhone,
		from_=TwilioNumber,
		body= msg + ' ' + u'\U0001f680')
	print(sms.sid)


# Definition that builds the sms body and then sends it
def check_sms(alarmNaam, sensorWaarden):
	message = "Beste\nAlarmering: " + alarmNaam + ", is afgegaan.\nVolgende sensoren hebben hun grens overschreden:\n"
	for k, v in sensorWaarden.items():
		message += str(k) + ": " + str(v) + "\n"
	message += "\nGa naar LINK voor verdere opvolging!"
	print(message)
	send_sms(message)


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
		else:
			light(alarmDict[alarmID], state)

		# Store the state of the alarmId
		previousAlert[alarmID] = 1
		##print("GPIO: " + str(alarmDict[alarmID]) + " aan")
	##print(previousAlert)


# Definition that checks if a notification in the form of an e-mail or SMS needs to be send
def check_notification(alarmAND, alarmid, alarmNaam, sensorWaarden, sensorStaat, countCrit, countWarn, countIgnore, mailCrit, mailWarn, smsCrit, smsWarn):
	# Temp variables
	previousNotification = True
	# Checks first if the file exist. If not created new and put current alarmid in it, this way you don't get spammed
	# If it already exists, move trough the usual path
	# This file is remade each check. This way it will not send a notification as long as the state is one of the following:
	## State 0: means no notification has been send since the previous check their where no sensors triggered
	## State 1: This means previously a message was sent when a warning point was triggered
	## State 2: This means previously a message was sent when a critical point was triggered
	# We keep one for mail and sms and join them as a string in the file
	fileCheck = os.path.isfile('temp/previousAlarm.json')

	## Debug prints
	##print(len(sensorWaarden))
	##print(sensorWaarden)
	##print(sensorStaat)
	##print(alarmAND)
	##print(str(countCrit) + ":" + str(countWarn) + ":" + str(countIgnore) + ":")
	##print(str(mailCrit) + ":" + str(mailWarn) + ":" + str(smsCrit) + ":" + str(smsWarn))

	# If there are no sensor values in this dict, it means that their in the correct range, so no checks have to be done, the state can be set to 0
	if len(sensorWaarden) != 0:
		if fileCheck is False:
			# Check if all sensor must be tripped before checkingif a message needs to be sent
			if alarmAND:
				if mailCrit is True:
					# Send notification if all are critical or a combination of critical and warning
					if countCrit + countWarn == len(sensorStaat) and countIgnore == 0 and countCrit != 0:
						print("send email - crit")
						check_email(alarmNaam, sensorWaarden)
						stateMail = "2"
				elif mailWarn is True:
					if countWarn == len(sensorStaat):
						print("send mail - warn")
						check_mail(alarmNaam, sensorWaarden)
						stateMail = "1"
					elif countCrit + countWarn == len(sensorStaat) and countIgnore == 0:
						print("send mail - warn")
						check_mail(alarmNaam, sensorWaarden)
						stateMail = "1"

				if smsCrit is True:
					# Send notification if all are critical or a combination of critical and warning
					if countCrit + countWarn == len(sensorStaat) and countIgnore == 0 and countCrit != 0:
						print("send sms - crit")
						check_sms(alarmNaam, sensorWaarden)
						stateSms = "2"
				elif smsWarn is True:
					if countWarn == len(sensorStaat):
						print("send sms - warn")
						check_sms(alarmNaam, sensorWaarden)
						stateSms = "1"
					elif countCrit + countWarn == len(sensorStaat) and countIgnore == 0:
						print("send sms - warn")
						check_sms(alarmNaam, sensorWaarden)
						stateSms = "1"

			if alarmAND is False:
				if mailCrit is True:
					if countCrit >= 1:
						print("send email - crit")
						check_email(alarmNaam, sensorWaarden)
						stateMail = "2"
				elif mailWarn is True:
					if countWarn >= 1 or countCrit >= 1:
						print("send email - warn")
						check_email(alarmNaam, sensorWaarden)
						stateMail = "1"

				if smsCrit is True:
					if countCrit >= 1:
						print("send sms - crit")
						check_sms(alarmNaam, sensorWaarden)
						stateSms = "2"
				elif smsWarn is True:
					if countWarn >= 1 or countCrit >= 1:
						print("send sms - warn")
						check_sms(alarmNaam, sensorWaarden)
						stateSms = "1"
		else:
			# Read the data from a local file
			with open('temp/previousAlarm.json') as f:
				current = json.loads(f.read())
				f.close()
				##print(current)
				##print ("\n")
			# We first assume nothing has been send before
			stateMail = "0"
			stateSms = "0"
			for k, v in current.items():
				# If the file exist and the alarmeringid is present in the file with 1 as its value, it means that previously a notification has been send
				if k == alarmid:
					if (v[:1] == "1" or v[:1] == "2") or (v[1:] == "1" or v[1:] == "2"):
						previousNotification = True
						stateMail = v[:1]
						stateSms = v[1:]
					else:
						previousNotification = False
				else:
					# Reput the other alarmeringen that are logged back in the dictionary that gets written to the file
					alarmeringenJSON[k] = v
					# Happens when an alarmering is not in the file
					if stateMail == "0" or stateSms == "0":
						previousNotification = False
			# Check if all sensor must be tripped before checkingif a message needs to be sent
			if alarmAND:
				if mailCrit is True:
					# Send notification if all are critical or a combination of critical and warning
					if countCrit + countWarn == len(sensorStaat) and countIgnore == 0 and countCrit != 0:
						# If the previousNotification is False we can send a notification again if necessary
						if previousNotification is False or stateMail != "2":
							print("send email - crit")
							check_email(alarmNaam, sensorWaarden)
							stateMail = "2"
				elif mailWarn is True:
					if countWarn == len(sensorStaat):
						# If the previousNotification is False we can send a notification again if necessary
						if previousNotification is False or stateMail == "0":
							print("send mail - warn")
							check_mail(alarmNaam, sensorWaarden)
							stateMail = "1"
					elif countCrit + countWarn == len(sensorStaat) and countIgnore == 0:
						# If the previousNotification is False we can send a notification again if necessary
						if previousNotification is False or stateMail == "0":
							print("send mail - warn")
							check_mail(alarmNaam, sensorWaarden)
							stateMail = "1"

				if smsCrit is True:
					# Send notification if all are critical or a combination of critical and warning
					if countCrit + countWarn == len(sensorStaat) and countIgnore == 0 and countCrit != 0:
						# If the previousNotification is False we can send a notification again if necessary
						if previousNotification is False or stateSms != "2":
							print("send sms - crit")
							check_sms(alarmNaam, sensorWaarden)
							stateSms = "1"
				elif smsWarn is True:
					if countWarn == len(sensorStaat):
						# If the previousNotification is False we can send a notification again if necessary
						if previousNotification is False or stateSms == "0":
							print("send sms - warn")
							check_sms(alarmNaam, sensorWaarden)
							stateSms = "1"
					elif countCrit + countWarn == len(sensorStaat) and countIgnore == 0:
						# If the previousNotification is False we can send a notification again if necessary
						if previousNotification is False or stateSms == "0":
							print("send sms - warn")
							check_sms(alarmNaam, sensorWaarden)
							stateSms = "1"

			if alarmAND is False:
				if mailCrit is True:
					if countCrit >= 1:
						# If the previousNotification is False we can send a notification again if necessary
						if previousNotification is False or stateMail != "2":
							print("send email - crit")
							check_email(alarmNaam, sensorWaarden)
							stateMail = "2"
				elif mailWarn is True:
					if countWarn >= 1 or countCrit >= 1:
						# If the previousNotification is False we can send a notification again if necessary
						if previousNotification is False or stateMail == "0":
							print("send email - warn test")
							check_email(alarmNaam, sensorWaarden)
							stateMail = "1"

				if smsCrit is True:
					if countCrit >= 1:
						# If the previousNotification is False we can send a notification again if necessary
						if previousNotification is False or stateSms != "2":
							print("send sms - crit")
							check_sms(alarmNaam, sensorWaarden)
							stateSms = "2"
				elif smsWarn is True:
					if countWarn >= 1 or countCrit >= 1:
						# If the previousNotification is False we can send a notification again if necessary
						if previousNotification is False or stateSms == "0":
							print("send sms - warn")
							check_sms(alarmNaam, sensorWaarden)
							stateSms = "1"
	else:
		# If there are sensor in sensorWaarden it means that a boundery has been reached
		stateMail = "0"
		stateSms = "0"
	# Put the alarmid in the file and check it as already send. When the sensor goes to normal values it will set it to zero, this indicates that next time a notification can be send again
	##print(stateMail + ":" + stateSms)
	alarmeringenJSON[alarmid] = stateMail + stateSms
	# Write the data to a local file
	with open('temp/previousAlarm.json', 'w') as outfile:
		json.dump(alarmeringenJSON, outfile)
		outfile.close()


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
	json_data=open('azure/alerts.json').read()
	JSON = json.loads(json_data)

	##print("Te checken alarmering:")
	# Loop trough the alarmeringen
	for alarm in JSON:
		# Dictionary that holds the sensors that went off
		sensorTripped = {}
		##print("Naam: " + alarm['naam'])

		# Loop trough the observed measurements
		for k, v in metingenDict.items():
			# Loop trough every sensor in the alarmering and check the bounderies
			# Store result in dictionary: alertCheck
			for grens in alarm['sensoren']:
				if grens['sensorId'] == k:
					# Check for critical first
					if int(grens['grensKritiekMin']) < v and int(grens['grensKritiekMax']) > v:
						##kritiek = False
						alertCheck[grens['sensorId']] = "nothing"
					else:
						##kritiek = True
						alertCheck[grens['sensorId']] = True
						# This stores the value of the sensor to give with an e-mail or SMS
						sensorTripped[grens['sensorId']] = v

					# Check for warning, if critical is already true skip else check warning
					# If warning is true set the sensorId key value to false to indicate this further down the script
					# Else we keep it on "nothing"
					if alertCheck[grens['sensorId']] != True:
						if int(grens['grensMin']) < v and int(grens['grensMax']) > v:
							##waarschuwing = False
							alertCheck[grens['sensorId']] = "nothing"
						else:
							##waarschuwing = True
							alertCheck[grens['sensorId']] = False
							# This stores the value of the sensor to give with an e-mail or SMS
							sensorTripped[grens['sensorId']] = v

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
						if countCrit + countWarn == len(alertCheck) and countIgnore == 0 and countCrit != 0:
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
						# Happens when value is critical, so also warning, but critical = false and warning = true. This is because of the count system in this script
						elif countCrit + countWarn == len(alertCheck) and countIgnore == 0:
							##print("id: " + soort['alarmId'] + "	-> warning!")
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

		##print("\n")
		# This will check if an e-mail/sms needs to be send
		check_notification(alarm['ANDOperator'], alarm['id'], alarm['naam'], sensorTripped, alertCheck, countCrit, countWarn, countIgnore, alarm['mail']['kritiek'], alarm['mail']['waarschuwing'], alarm['sms']['kritiek'], alarm['sms']['waarschuwing'])
		# Reset these variables each alarmering
		countIgnore = 0
		countWarn = 0
		countCrit = 0
		alertCheck = {}
	# Reset the previousAlert dict for when the next measurements comes
	previousAlert.clear()
