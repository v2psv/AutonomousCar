#-*- coding:UTF-8 -*-
import RPi.GPIO as GPIO
import os, sys, time

#电机引脚
IN1 = 20
IN2 = 21
IN3 = 19
IN4 = 26
ENA = 16
ENB = 13
MOTOR_FREQUENCY = 2000

class Motor:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup((IN1, IN2, IN3, IN4, ENA, ENB), GPIO.OUT)
        self.pwm_ENA = GPIO.PWM(ENA, MOTOR_FREQUENCY)
        self.pwm_ENB = GPIO.PWM(ENB, MOTOR_FREQUENCY)
        self.pwm_ENA.start(0)
        self.pwm_ENB.start(0)

    def change_speed(self, dc):
        self.pwm_ENA.ChangeDutyCycle(dc)
        self.pwm_ENB.ChangeDutyCycle(dc)

    def run(self, signal):
        if signal == 'F':
            self.forward()
            self.change_speed(70)
        if signal == 'B':
            self.backward()
            self.change_speed(70)
        elif signal == 'L':
            self.left()
        elif signal == 'R':
            self.right()
        elif signal == '-':
            self.stop()

    def forward(self):
        GPIO.output((IN1, IN3), GPIO.HIGH)
        GPIO.output((IN2, IN4), GPIO.LOW)

    def backward(self):
        GPIO.output((IN1, IN3), GPIO.LOW)
        GPIO.output((IN2, IN4), GPIO.HIGH)

    def left(self):
        GPIO.output((IN1, IN2, IN4), GPIO.LOW)
        GPIO.output(IN3, GPIO.HIGH)

    def right(self):
        GPIO.output((IN2, IN3, IN4), GPIO.LOW)
        GPIO.output(IN1, GPIO.HIGH)

    def stop(self):
        GPIO.output((IN1, IN2, IN3, IN4), GPIO.LOW)

    def __del__(self):
        self.pwm_ENA.stop()
        self.pwm_ENB.stop()

if __name__ == '__main__':
    motor = Motor()
    motor.run('F')
    time.sleep(0.5)
    motor.run('-')
