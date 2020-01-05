import RPi.GPIO as GPIO
import time
 
OBSTACLE_LEFT = 12
OBSTACLE_RIGHT = 17

class Obstacle:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup((OBSTACLE_LEFT, OBSTACLE_RIGHT), GPIO.IN)

    def detect(self):
        l, r = 0, 0
        if(GPIO.input(OBSTACLE_LEFT)==0):
            l = 1
        if(GPIO.input(OBSTACLE_RIGHT)==0):
            r = 1
        return l, r

if __name__ == "__main__":
    obs = Obstacle()
    while True:
        print(obs.detect())
        time.sleep(0.1)
