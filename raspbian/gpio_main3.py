# PUSHBUTTON RGB LED Control
# - -> 오른쪽 3
# R,G,B -> 왼쪽 10, 11 , 12
import RPi.GPIO as GPIO
import time

BUTTON = 3
RED = 11
GREEN = 12
BLUE = 13

GPIO.setmode(GPIO.BOARD)
GPIO.setup(RED, GPIO.OUT)
GPIO.setup(GREEN, GPIO.OUT)
GPIO.setup(BLUE, GPIO.OUT)
GPIO.setup(BUTTON, GPIO.IN)

is_click = False

def button_push(val) :
    global is_click
    if is_click == True :
        GPIO.output(RED, GPIO.HIGH)
        GPIO.output(GREEN, GPIO.HIGH)
        GPIO.output(BLUE, GPIO.HIGH)
        time.sleep(0.5)
    else :
        GPIO.output(RED, GPIO.LOW)
        GPIO.output(GREEN, GPIO.LOW)
        GPIO.output(BLUE, GPIO.LOW)
        time.sleep(0.5)

    is_click = not is_click

while True :
    GPIO.wait_for_edge(BUTTON, GPIO.RISING, bouncetime = 100)
    time.sleep(0.1)

    button_push(GPIO.input(BUTTON))

    
