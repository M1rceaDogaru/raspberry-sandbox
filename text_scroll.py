import time
import RPi.GPIO as GPIO
import ptvsd

# ptvsd.enable_attach()
# ptvsd.wait_for_attach()

GPIO.setmode(GPIO.BCM)

switch = 12 #GPIO12
dataPin = 18 #GPIO18
latchPin = 15 #GPIO15
clockPin = 14 #GPIO14

GPIO.setup(switch, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(dataPin, GPIO.OUT)
GPIO.setup(latchPin, GPIO.OUT)
GPIO.setup(clockPin, GPIO.OUT)

GPIO.output(dataPin, GPIO.LOW)
GPIO.output(latchPin, GPIO.LOW)
GPIO.output(clockPin, GPIO.LOW)

#declare variables that will be send to the first shift
#register and turn on the LED segments and show a digit
#from 0 to 9, with or without the dot
charactersBuffer = {
    '0': 63,         
    '1': 6,
    '2': 91,
    '3': 79,
    '4': 102,
    '5': 109,
    '6': 125,
    '7': 7,
    '8': 127,
    '9': 111,
    ' ': 0,
    'a': 119,       #0b01110111
    'b': 127,       #0b01111111
    'c': 57,
    'd': 63,
    'e': 121,
    'f': 113,       #0b01110001
    'g': 125,
    'h': 118,
    'i': 6,
    'j': 30,       #0b00011110
    'k': 112,          #0b01110000
    'l': 56,       #0b00111000
    'm': 55,
    'n': 55,         #0b00110111
    'o': 63,
    'p': 115,      #0b01110011
    'r': 119,
    's': 109,
    't': 7,
    'u': 62,
    'v': 62,          #0b00111110    
    'x': 118,
    'y': 102,
    'z': 91           
}

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
timeSinceLastShift = time.time()
shiftDelaySeconds = 0.5
userInput = ""
valueToDisplay = ""
digitIndex = 1

def initialDisplay():
    # select all digits
    setDigit(5)
    # send underscore buffer to all digits
    shift(underscore)

def checkSwitch():
    global switchPressed

    if GPIO.input(switch) == GPIO.LOW and switchPressed == False:
        switchPressed = True
        getUserInput()
    elif GPIO.input(switch) == GPIO.HIGH and switchPressed == True:
        switchPressed = False

def getUserInput():
    global userInput, digitIndex
    userInput = input("Type string to display and hit Enter: ").lower()
    digitIndex = 1

def displayValue(value):
    bufferToDisplay = []
    for character in value:
        bufferToDisplay.append(charactersBuffer[character])

    shiftBuffer(bufferToDisplay)

def shiftBuffer(bufferToDisplay):
    index = 1
    for bufferCharacter in bufferToDisplay:
        setDigit(index)
        shift(bufferCharacter)
        index += 1

def shiftUserInput():
    global valueToDisplay, digitIndex
    startIndex = digitIndex - 4
    valueToDisplay = ""

    for value in range(startIndex, digitIndex):
        if value < 1 or value > len(userInput):
            valueToDisplay += " "
        else:
            valueToDisplay += userInput[value - 1]
    
    digitIndex += 1
    if digitIndex - 4 > len(userInput):
        digitIndex = 1

def prepareInput():
    global timeSinceLastShift
    currentTime = time.time()
    if len(userInput) > 0 and currentTime - timeSinceLastShift > shiftDelaySeconds:
        timeSinceLastShift = time.time()
        shiftUserInput()
    
    displayValue(valueToDisplay)

try:  
    #pass
    initialDisplay()
    
    while True:
        checkSwitch()                    
        prepareInput()
finally:
    digit = 0
    shift(0)
    GPIO.cleanup()
    print("Execution complete")