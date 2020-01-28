import time
import threading
import RPi.GPIO as GPIO
import ptvsd
import Adafruit_DHT

#ptvsd.enable_attach()
#ptvsd.wait_for_attach()

GPIO.setmode(GPIO.BCM)
dhtDevice = Adafruit_DHT.DHT11

switch = 12 #GPIO12
dhtInput = 25 #GPIO25

dataPin = 18 #GPIO18
latchPin = 15 #GPIO15
clockPin = 14 #GPIO14

GPIO.setup(switch, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(dhtInput, GPIO.IN)
GPIO.setup(dataPin, GPIO.OUT)
GPIO.setup(latchPin, GPIO.OUT)
GPIO.setup(clockPin, GPIO.OUT)

GPIO.output(dataPin, GPIO.LOW)
GPIO.output(latchPin, GPIO.LOW)
GPIO.output(clockPin, GPIO.LOW)

#declare variables that will be send to the first shift
#register and turn on the LED segments and show a digit
#from 0 to 9, with or without the dot
numbersBuffer = {
    '0': 63,        
    '0.': 191,      
    '1': 6,
    '1.': 134,
    '2': 91,
    '2.': 219,
    '3': 79,
    '3.': 207,
    '4': 102,
    '4.': 230,
    '5': 109,
    '5.': 237,
    '6': 125,
    '6.': 253,
    '7': 7,
    '7.': 135,
    '8': 127,
    '8.': 255,
    '9': 111,
    '9.': 239
}

letter_c = 57      #0b00111001
letter_h = 118     #0b01110110
underscore = 8     #0b00001000

#declare a variable that will store the current digits active
digit = 0

def setDigit(x):
    global digit
    if x == 1:
        digit = 14 #0b00001110
    elif x == 2:
        digit = 13 #0b00001101
    elif x == 3:
        digit = 11 #0b00001011
    elif x == 4:
        digit = 7 #0b00000111
    elif x == 5:
        digit = 0 #0b00000000

#function to send the values to the shift registers
def shift(buffer):
    #make the global variable available
    global digit

	#send the bits to the second shift register
    for i in range(0,8):
        GPIO.output(dataPin, (128 & (digit << i)))
        GPIO.output(clockPin, GPIO.HIGH)
        #time.sleep(0.001)
        GPIO.output(clockPin, GPIO.LOW)

	#send the bits to the first shift register
    for i in range(0,8):
        GPIO.output(dataPin, (128 & (buffer << i)))
        GPIO.output(clockPin, GPIO.HIGH)
        #time.sleep(0.001)
        GPIO.output(clockPin, GPIO.LOW)

	#shift the bits
    GPIO.output(latchPin, GPIO.HIGH)
    #time.sleep(0.001)
    GPIO.output(latchPin, GPIO.LOW)

switchPressed = False
displayTemp = True
bufferTemp = 0
bufferHumidity = 0

def initialDisplay():
    # select all digits
    setDigit(5)
    # send underscore buffer to all digits
    shift(underscore)

def checkSwitch():
    global switchPressed, displayTemp

    if GPIO.input(switch) == GPIO.LOW and switchPressed == False:
        switchPressed = True
        displayTemp = not displayTemp
    elif GPIO.input(switch) == GPIO.HIGH and switchPressed == True:
        switchPressed = False

def checkDhtSensor():
    global bufferTemp, bufferHumidity
    timeToSleepSeconds = 1

    while True:
        humidity, temperature = Adafruit_DHT.read(dhtDevice, dhtInput)
        if humidity is not None and temperature is not None:
            timeToSleepSeconds = 5
            bufferTemp = temperature
            bufferHumidity = humidity

            if displayTemp == True:
                print('Temperature = {:.1f}'.format(temperature))
            else:
                print('Humidity = {:.1f}'.format(humidity))

        time.sleep(timeToSleepSeconds)

def displayValue(value, endLetter):
    if value <= 0:
        initialDisplay()
        return

    characters = '{:.1f}'.format(value)
    index = 0
    bufferToDisplay = []
    for character in characters:
        if character == '.':
            continue

        bufferCharacter = character
        if characters[index + 1] == '.':
            bufferCharacter += '.'

        bufferToDisplay.append(numbersBuffer[bufferCharacter])
        index += 1

    bufferToDisplay.append(endLetter) 
    shiftBuffer(bufferToDisplay)

def shiftBuffer(bufferToDisplay):
    index = 1
    for bufferCharacter in bufferToDisplay:
        setDigit(index)
        shift(bufferCharacter)
        index += 1

def displaySensorData():
    if displayTemp == True:
        displayValue(bufferTemp, letter_c)
    else:
        displayValue(bufferHumidity, letter_h)

try:  
    #pass
    initialDisplay()      
    checkDhtSensorThread = threading.Thread(target=checkDhtSensor)
    checkDhtSensorThread.start()
    
    while True:
        checkSwitch()                    
        displaySensorData()
finally:
    digit = 0
    shift(0)
    GPIO.cleanup()
    print("Execution complete")