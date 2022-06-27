# RGB LED ON/OFF
import RPi.GPIO as GPIO
import time


RED = 11
GREEN = 12
BLUE = 13

GPIO.setmode(GPIO.BOARD)
GPIO.setup(RED, GPIO.OUT)
GPIO.setup(GREEN, GPIO.OUT)
GPIO.setup(BLUE, GPIO.OUT)

# GPIO.output(RED, GPIO.LOW)

try :
    while True :
        GPIO.output(RED, GPIO.HIGH)
        GPIO.output(GREEN, GPIO.LOW)
        GPIO.output(BLUE, GPIO.LOW)
        time.sleep(0.5)

        GPIO.output(RED, GPIO.LOW)
        GPIO.output(GREEN, GPIO.HIGH)
        GPIO.output(BLUE, GPIO.LOW)
        time.sleep(0.5)

        GPIO.output(RED, GPIO.LOW)
        GPIO.output(GREEN, GPIO.LOW)
        GPIO.output(BLUE, GPIO.HIGH)
        time.sleep(0.5)

        GPIO.output(RED, GPIO.HIGH)
        GPIO.output(GREEN, GPIO.HIGH)
        GPIO.output(BLUE, GPIO.HIGH)
        time.sleep(0.5)

except KeyboardInterrupt :
    GPIO.output(RED, GPIO.LOW)
    GPIO.output(GREEN, GPIO.LOW)
    GPIO.output(BLUE, GPIO.LOW)
    GPIO.cleanup()

