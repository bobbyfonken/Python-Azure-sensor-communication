import RPi.GPIO as GPIO
import time

def buzz(frequency, length, pin):     	#create the function "buzz" and feed it the pitch and duration)

	if(frequency==0):
		time.sleep(length)
		return
	period = 1.0 / frequency          	#in physics, the period (sec/cyc) is the inverse of the frequency (cyc/sec)
	delayValue = period / 2         	#calcuate the time for half of the wave
	numCycles = int(length * frequency)	#the number of waves to produce is the duration times the frequency

	for i in range(numCycles):			#start a loop from 0 to the variable "cycles" calculated above
		GPIO.output(pin, True)			#set pin 27 to high
		time.sleep(delayValue)			#wait with pin 27 high
		GPIO.output(pin, False)			#set pin 27 to low
		time.sleep(delayValue)			#wait with pin 27 low

def setup(pin):
	GPIO.setup(pin, GPIO.IN)
	GPIO.setup(pin, GPIO.OUT)

def play_mario(melody, tempo, pin, pace=0.800):

	for i in range(0, len(melody)):        # Play song

		noteDuration = pace/tempo[i]
		buzz(melody[i],noteDuration, pin)    # Change the frequency along the song note

		pauseBetweenNotes = noteDuration * 1.30
		time.sleep(pauseBetweenNotes)


def play_sirene(pin, lenght):
	# We rekenen 1 seconde per sensor: After choosing the pause, in this case 0.2 seconde we divide lenght by this and that is the amount of replays to get a nice sound lasting the amount of sensors
	count = 0
	pause = 0.15
	replays = (lenght / pause) + 4 # Add reserve 2 for extra lenght
	pitch = 1000
	duration = 0.1
	period = 1.0 / pitch					#in physics, the period (sec/cyc) is the inverse of the frequency (cyc/sec)
	delay = period / 2						#calcuate the time for half of the wave
	cycles = int(duration * pitch)			#the number of waves to produce is the duration times the frequency

	while count <= replays:
		for i in range(cycles):				#start a loop from 0 to the variable "cycles" calculated above
			GPIO.output(pin, True)			#set pin 18 to high
			time.sleep(delay)				#wait with pin 18 high
			GPIO.output(pin, False)			#set pin 18 to low
			time.sleep(delay)				#wait with pin 18 low
		count += 1
		time.sleep(pause)


def main_buzz(pin, lenght):
	setup(pin)
	play_sirene(pin, lenght)