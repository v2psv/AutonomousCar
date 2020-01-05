#-*- coding:UTF-8 -*-
import RPi.GPIO as GPIO
import time, datetime
import socket, pickle, struct, json
import picamera, cv2
from picamera.array import PiRGBArray
from threading import Thread
from motor import Motor
from distance import Ultrasonic
from obstacle import Obstacle

# socket config
SERVER_IP = '192.168.1.107'
SERVER_CMD_PORT = 9101
SERVER_IMAGE_PORT = 9102
SERVER_SENSOR_PORT = 9103

MSG_CMD_LENGTH = 64
IMAGE_RESOLUTION = (320, 240)
FPS = 2

STOP = False

class Camera(object):
    def __init__(self, ip, port):
        self.camera = picamera.PiCamera(resolution=IMAGE_RESOLUTION, framerate=FPS)
        self.rawCapture = PiRGBArray(self.camera, size=IMAGE_RESOLUTION)
        self.stream = self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, port))

    def pack_image(self, frame):
        image = cv2.imencode('.jpg', frame.array)[1]
        data = pickle.dumps(image, 0)
        msg_size = struct.pack(">L", len(data))
        msg = msg_size + data
        print("len msg: ", len(msg))
        return msg

    def send_image(self):
        sleep_time = 1. / FPS
        for frame in self.stream:
            time.sleep(sleep_time)
            msg = self.pack_image(frame)
            self.socket.sendall(msg)
            self.rawCapture.truncate(0)
            if STOP:
                return

    def __del__(self):
        self.camera.close()
        self.rawCapture.close()
        self.stream.close()
        self.socket.close()

class Sensor(object):
    def __init__(self, ip, port):
        self.ultrasonic = Ultrasonic()
        self.obstacle = Obstacle()
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.connect((ip, port))

    def sensor_data(self, interval=1):
        while True:
            time.sleep(interval)
            try:
                dis = self.ultrasonic.get_distance()
                obs = self.obstacle.detect()
                msg = {
                    "Time":str(datetime.datetime.now()),
                    "Distance": dis,
                    "LeftObstacle": obs[0],
                    "RightObstacle": obs[1]
                    }
                msg = json.dumps(msg).encode('utf-8')
                self.socket.send(msg)
                print(msg)
            except:
                print("Something wrong when reading sensor data!")

            if STOP:
                return

    def __del__(self):
        self.socket.close()

class Car(object):
    def __init__(self, ip, port):
        self.motor = Motor()
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.connect((ip, port))
        self.socket.setblocking(False)

    def recv_cmd(self, interval=0.2):
        while True:
            time.sleep(interval)
            try:
                cmd = self.socket.recv(MSG_CMD_LENGTH).decode('utf-8')[0]
            except:
                cmd = '-'
            print("Command: " + cmd)
            self.motor.run(cmd)

            if STOP:
                return

    def __del__(self):
        self.socket.close()

class Controler(object):
    def __init__(self):
        self.car = Car(SERVER_IP, SERVER_CMD_PORT)
        self.sensor = Sensor(SERVER_IP, SERVER_SENSOR_PORT)
        self.camera = Camera(SERVER_IP, SERVER_IMAGE_PORT)

    def main(self):
        t1 = Thread(target=self.car.recv_cmd, args=())
        t2 = Thread(target=self.sensor.sensor_data, args=())
        t3 = Thread(target=self.camera.send_image, args=())
        t1.daemon = True
        t2.daemon = True
        t3.daemon = True
        t1.start()
        t2.start()
        t3.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            STOP = True
            del self.car, self.sensor, self.camera
    
if __name__ == '__main__':
    con = Controler()
    con.main()