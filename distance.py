#-*- coding:UTF-8 -*-
import RPi.GPIO as GPIO
import time

# 舵机引脚和频率定义
SERVO_PIN = 23
SERVO_FREQUENCY = 50
# 超声波距离传感器引脚定义
ULTRASONIC_TRIG = 1
ULTRASONIC_ECHO = 0

def init():
    GPIO.cleanup()
    #设置GPIO口为BCM编码方式
    GPIO.setmode(GPIO.BCM)
    #忽略警告信息
    GPIO.setwarnings(False)

class Servo:
    def __init__(self, bias_deg=30, max_deg=30):
        GPIO.setup(SERVO_PIN, GPIO.OUT)
        self.bias_deg = bias_deg
        self.max_deg = max_deg
        self.pwm_servo = GPIO.PWM(SERVO_PIN, SERVO_FREQUENCY)
        self.pwm_servo.start(0)
        self.restore()
        print("[Servo] start! channel=%d, bias_deg=%f, frequency=%d" %(SERVO_PIN, self.bias_deg, SERVO_FREQUENCY))

    def get_dc(self, deg):
        return 2.5 + 10 * deg / 180

    def turn(self, deg):
        if -self.max_deg <= deg <= self.max_deg:
            deg += self.bias_deg
            step = 3 if deg > self.curr_deg else -3
            for i in range(self.curr_deg, deg, step):
                self.pwm_servo.ChangeDutyCycle(self.get_dc(i))
                time.sleep(0.01)
            if i != deg:
                self.pwm_servo.ChangeDutyCycle(self.get_dc(deg))

            self.curr_deg = deg
            time.sleep(0.5)
        else:
            deg = max(deg, self.max_deg)
            deg = min(deg, -self.max_deg)
            self.turn(deg)

    def turn_left(self):
        self.turn(self.max_deg)

    def turn_right(self):
        self.turn(-self.max_deg)

    def restore(self):
        # 恢复初始状态，转动到偏置角度
        self.curr_deg = self.bias_deg
        self.pwm_servo.ChangeDutyCycle(self.get_dc(self.curr_deg))

    def stop(self):
        self.pwm_servo.stop()

class Ultrasonic:
    def __init__(self):
        GPIO.setup(ULTRASONIC_TRIG, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(ULTRASONIC_ECHO, GPIO.IN)

    def get_distance(self):
        GPIO.output(ULTRASONIC_TRIG, GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(ULTRASONIC_TRIG, GPIO.LOW)

        start = end = time.time()
        while GPIO.input(ULTRASONIC_ECHO) == 0:
            start = time.time()

        while GPIO.input(ULTRASONIC_ECHO) == 1:
            end = time.time()
        return (end - start) * 340 * 100 / 2


if __name__ == "__main__":
    print('Initializing...')
    init()
    s = Servo()
    s.restore()
    u = Ultrasonic()
    time.sleep(1)

    try:
        while True:
            d1 = u.get_distance()
            s.turn_left()
            d2 = u.get_distance()
            s.turn_right()
            d3 = u.get_distance()
            s.restore()
            print("Distance: {:.2f} cm, {:.2f} cm, {:.2f} cm".format(d1, d2, d3))
            time.sleep(0.5)
    except KeyboardInterrupt:
        #GPIO.cleanup()
        pass
