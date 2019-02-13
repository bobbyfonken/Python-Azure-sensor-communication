import RPi.GPIO as GPIO
import time

buzzer_pin = 27

notes = {
    'B0' : 31,
    'C1' : 33, 'CS1' : 35,
    'D1' : 37, 'DS1' : 39,
    'E1' : 41,
    'F1' : 44, 'FS1' : 46,
    'G1' : 49, 'GS1' : 52,
    'A1' : 55, 'AS1' : 58,
    'B1' : 62,
    'C2' : 65, 'CS2' : 69,
    'D2' : 73, 'DS2' : 78,
    'E2' : 82,
    'F2' : 87, 'FS2' : 93,
    'G2' : 98, 'GS2' : 104,
    'A2' : 110, 'AS2' : 117,
    'B2' : 123,
    'C3' : 131, 'CS3' : 139,
    'D3' : 147, 'DS3' : 156,
    'E3' : 165,
    'F3' : 175, 'FS3' : 185,
    'G3' : 196, 'GS3' : 208,
    'A3' : 220, 'AS3' : 233,
    'B3' : 247,
    'C4' : 262, 'CS4' : 277,
    'D4' : 294, 'DS4' : 311,
    'E4' : 330,
    'F4' : 349, 'FS4' : 370,
    'G4' : 392, 'GS4' : 415,
    'A4' : 440, 'AS4' : 466,
    'B4' : 494,
    'C5' : 523, 'CS5' : 554,
    'D5' : 587, 'DS5' : 622,
    'E5' : 659,
    'F5' : 698, 'FS5' : 740,
    'G5' : 784, 'GS5' : 831,
    'A5' : 880, 'AS5' : 932,
    'B5' : 988,
    'C6' : 1047, 'CS6' : 1109,
    'D6' : 1175, 'DS6' : 1245,
    'E6' : 1319,
    'F6' : 1397, 'FS6' : 1480,
    'G6' : 1568, 'GS6' : 1661,
    'A6' : 1760, 'AS6' : 1865,
    'B6' : 1976,
    'C7' : 2093, 'CS7' : 2217,
    'D7' : 2349, 'DS7' : 2489,
    'E7' : 2637,
    'F7' : 2794, 'FS7' : 2960,
    'G7' : 3136, 'GS7' : 3322,
    'A7' : 3520, 'AS7' : 3729,
    'B7' : 3951,
    'C8' : 4186, 'CS8' : 4435,
    'D8' : 4699, 'DS8' : 4978
}

underworld_melody = [
  notes['C4'], notes['C5'], notes['A3'], notes['A4'],
  notes['AS3'], notes['AS4'], 0,
  0,
  notes['F3'], notes['F4'], notes['D3'], notes['D4'],
  notes['DS3'], notes['DS4'], 0,
  0, notes['DS4'], notes['CS4'], notes['D4'],
  notes['CS4'], notes['DS4'],
  notes['DS4'], notes['GS3'],
  notes['G3'], notes['CS4'],
  notes['C4'], notes['FS4'], notes['F4'], notes['E3'], notes['AS4'], notes['A4'],
  notes['GS4'], notes['DS4'], notes['B3'],
  notes['AS3'], notes['A3'], notes['GS3'],
  0, 0, 0
]

underworld_tempo = [
  12, 12, 12, 12,
  12, 12, 6,
  3,
  12, 12, 12, 12,
  12, 12, 6,
  6, 18, 18, 18,
  6, 6,
  6, 6,
  6, 6,
  18, 18, 18, 18, 18, 18,
  10, 10, 10,
  10, 10, 10,
  3, 3, 3
]

def buzz(frequency, length, pin):     #create the function "buzz" and feed it the pitch and duration)

    if(frequency==0):
        time.sleep(length)
        return
    period = 1.0 / frequency          #in physics, the period (sec/cyc) is the inverse of the frequency (cyc/sec)
    delayValue = period / 2         #calcuate the time for half of the wave
    numCycles = int(length * frequency)     #the number of waves to produce is the duration times the frequency

    for i in range(numCycles):        #start a loop from 0 to the variable "cycles" calculated above
        GPIO.output(pin, True)     #set pin 27 to high
        time.sleep(delayValue)        #wait with pin 27 high
        GPIO.output(pin, False)        #set pin 27 to low
        time.sleep(delayValue)        #wait with pin 27 low

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
    pause = 0.1
    replays = lenght / pause
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
    #play_mario(underworld_melody,underworld_tempo,  pin, 0.800)
    play_sirene(pin, lenght)