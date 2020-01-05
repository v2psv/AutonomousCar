#-*- coding: utf8 -*-
import pygame
import socket, json, time, struct
import sys, subprocess, pickle
from PIL import Image
from threading import Thread
import cv2

# socket config
CAR_IP = "192.168.1.118"
SERVER_CMD_PORT = 9101
SERVER_IMAGE_PORT = 9102
SERVER_SENSOR_PORT = 9103
MSG_SENSOR_LENGTH = 1024

IMAGE_RESOLUTION = (320, 240)

STOP = False

class SendCommand(object):
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('0.0.0.0', SERVER_CMD_PORT))
        self.socket.listen(1)
        self.conn, self.client_addr = self.socket.accept()
        print('Client connected, IP & Port: ' + str(self.client_addr))

    def up_socket(self):
        self.conn.sendall('F'.encode('utf-8'))

    def down_socket(self):
        self.conn.sendall('B'.encode('utf-8'))

    def left_socket(self):
        self.conn.sendall('L'.encode('utf-8'))

    def right_socket(self):
        self.conn.sendall('R'.encode('utf-8'))

    def __del__(self):
        self.conn.close()
        self.socket.close()

class VideoStream(object):
    def __init__(self, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('0.0.0.0', port))

        cmdline = ['vlc', '--demux', 'h264', '-']
        #cmdline = ['mplayer', '-fps', '25', '-cache', '1024', '-']
        self.player = subprocess.Popen(cmdline, stdin=subprocess.PIPE)

    def display_stream(self):
        try:
            while True:
                data = self.socket.recv(65536) # 64KB
                if not data:
                    break
                self.player.stdin.write(data)
        finally:
            self.__del__()

    def __del__(self):
        self.socket.close()
        self.player.terminate()

class DisplayImage(object):
    def __init__(self, screen):
        self.screen = screen
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('0.0.0.0', SERVER_IMAGE_PORT))
        self.socket.listen(1)
        self.conn, self.client_addr = self.socket.accept()
        print('Client connected, IP & Port: ' + str(self.client_addr))

    def recv_image(self):
        payload_size = struct.calcsize(">L")
        buffer_size = 128 * 1024  # 128 KB
        while True:
            time.sleep(0.2)
            try:
                data = b''
                data += self.conn.recv(buffer_size)
                msg_size = struct.unpack(">L", data[:payload_size])[0]
                print("msg_size: {}".format(msg_size))

                data = data[payload_size:]
                while len(data) < msg_size:
                    data += self.conn.recv(buffer_size)
                data = data[:msg_size]
                frame = pickle.loads(data)
                frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
                frame = pygame.surfarray.make_surface(frame)
            except:
                frame = None
            if frame is not None:
                self.screen.blit(frame, (0,0))
                pygame.display.update()
        return

    def __del__(self):
        sele.conn.close()
        self.socket.close()

class PrintSensor(object):
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('0.0.0.0', SERVER_SENSOR_PORT))
        self.socket.listen(1)
        self.conn, self.client_addr = self.socket.accept()
        print('Client connected, IP & Port: ' + str(self.client_addr))

    def print_sensor(self, interval=0.2):
        while True:
            time.sleep(interval)
            try:
                sensor = self.conn.recv(MSG_SENSOR_LENGTH).decode('utf-8')
                # print(sensor)
                sensor = json.loads(sensor)
            except:
                sensor = ''
        return

    def __del__(self):
        self.conn.close()
        self.socket.close()

class Controler(object):
    def __init__(self):
        pygame.init()
        pygame.key.set_repeat(100, 100)
        screen = pygame.display.set_mode((640, 480), 0)
        pygame.display.set_caption('Remote Webcam Viewer')
        clock = pygame.time.Clock()

        self.cmd = SendCommand()
        self.sensor = PrintSensor()
        self.image = DisplayImage(screen)

    def game_over(self):
        pygame.quit()
        sys.exit()

    def start(self):
        t1 = Thread(target=self.sensor.print_sensor, args=())
        t2 = Thread(target=self.image.recv_image, args=())
        t1.daemon = True
        t2.daemon = True
        t1.start()
        t2.start()

        try:
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            self.cmd.up_socket()
                        elif event.key == pygame.K_DOWN:
                            self.cmd.down_socket()
                        elif event.key == pygame.K_LEFT:
                            self.cmd.left_socket()
                        elif event.key == pygame.K_RIGHT:
                            self.cmd.right_socket()
                    elif event.type == pygame.QUIT:
                        self.game_over()
                    time.sleep(0.1)
        except KeyboardInterrupt:
            self.game_over()

if __name__ == '__main__':
    con = Controler()
    con.start()
