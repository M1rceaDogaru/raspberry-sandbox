from time import sleep
import RPi.GPIO as GPIO
#import ptvsd

#ptvsd.enable_attach()
#ptvsd.wait_for_attach()

GPIO.setmode(GPIO.BOARD)

speed = 8
forward = 10
reverse = 22

GPIO.setup(speed, GPIO.OUT)
GPIO.setup(forward, GPIO.OUT)
GPIO.setup(reverse, GPIO.OUT)

motorPwm = GPIO.PWM(speed, 100)
motorPwm.start(0)

def move(cycle, isForward):
    print("Move")
    motorPwm.ChangeDutyCycle(cycle)
    if isForward == True:
        GPIO.output(forward, GPIO.HIGH)
        GPIO.output(reverse, GPIO.LOW)
    else:
        GPIO.output(forward, GPIO.LOW)
        GPIO.output(reverse, GPIO.HIGH)

try:
    count = 0
    while True:
        count += 1
        speed = int(input("Enter speed (0-100): "))
        move(speed, True)

finally:
    GPIO.cleanup()