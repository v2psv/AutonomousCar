#-*- coding:UTF-8 -*-
import RPi.GPIO as GPIO
import socket, time
import datetime
from motor import Motor
from distance import Ultrasonic
from obstacle import Obstacle

# socket config
LISTEN_PORT = 9900
MSG_LENGTH = 64

class ServerSocket(object):
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('', LISTEN_PORT))
        self.server_socket.listen(MSG_LENGTH)

        self.client_socket, self.port_ip = self.server_socket.accept()
        self.client_socket.setblocking(False)
        print('Client connected, IP & Port: ' + str(self.port_ip))

    def recv_signal(self):
        try:
            signal = self.client_socket.recv(MSG_LENGTH).decode('utf-8')[0]
        except socket.error:
            signal = '-'
        return signal

    def __del__(self):
        self.client_socket.close()
        self.server_socket.close()

class Controler(object):
    def __init__(self):
        self.motor = Motor()
        self.ultrasonic = Ultrasonic()
        self.obstacle = Obstacle()
        self.socket = ServerSocket()

    def main(self, interval=0.2):
        while True:
            time.sleep(interval)
            distance = self.ultrasonic.get_distance()
            obs = self.obstacle.detect()
            signal = self.socket.recv_signal()
            print("[%s] Signal: %s, Distance: %.2f cm, Left: %d, Right: %d" % (datetime.datetime.now(), signal, distance, obs[0], obs[1]))
            # if(obs[0]==1 or obs[1]==1):
                # signal = '-'
            self.motor.run(signal)
    
if __name__ == '__main__':
    car = Controler()
    car.main()
