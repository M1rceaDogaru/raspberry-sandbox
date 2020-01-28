import time
import RPi.GPIO as GPIO
import ptvsd

ptvsd.enable_attach()
ptvsd.wait_for_attach()

GPIO.setmode(GPIO.BOARD)
trigger = 16
echo = 18
led = 8

GPIO.setup(trigger, GPIO.OUT)
GPIO.setup(echo, GPIO.IN)
GPIO.setup(led, GPIO.OUT)

def calculate():
    GPIO.output(trigger, GPIO.HIGH)
    time.sleep(0.00001) 
    GPIO.output(trigger, GPIO.LOW)

    start = time.time() 
    stop = time.time()      
    while GPIO.input(echo) == 0:       
        start = time.time()

    while  GPIO.input(echo) == 1:       
        stop = time.time()

    duration = stop - start
    distance = 34300/2 * duration                
    
    if distance < 3400:       
        #display the distance in console       
        print ("Distance = %.2f" % distance)
    
    return distance

def blink(distance):
    sleepTime = 0.3

    if (distance > 20):
        sleepTime =0.3
    elif (distance > 10):
        sleepTime = 0.2
    elif (distance > 5):
        sleepTime = 0.1
    elif (distance > 1):
        sleepTime = 0.05

    GPIO.output(led, GPIO.HIGH)
    time.sleep(sleepTime)
    GPIO.output(led, GPIO.LOW)
    time.sleep(sleepTime)

try:
    while True:
        distance = calculate()
        blink(distance)
finally:
    GPIO.cleanup()