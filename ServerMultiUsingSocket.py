import pygame  # pygame 모듈의 임포트
import sys  # 외장 모듈
from pygame.locals import *  # QUIT 등의 pygame 상수들을 로드한다.
import time
import threading
import re
import socket
import socket_adress

"""
socket_adress.py

IP = 'Server Internal IP'
PORT = Server port_number
SIZE = Size of sending data
ADDR = (IP, PORT)

"""


IP = socket_adress.IP
PORT = socket_adress.SERVER_PORT
SIZE = socket_adress.SIZE
ADDR = socket_adress.ADDR

width = 600  # 상수 설정
height = 400
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
fps = 60

pygame.init()  # 초기화

pygame.display.set_caption('Two Balls')
main_display = pygame.display.set_mode((width, height), 0, 32)
clock = pygame.time.Clock()  # 시간 설정

PIXEL_PER_METER = (10.0 / 0.2)  # 10 pixel 20 cm
RUN_SPEED_KMPH = 0.6  # Km / Hour
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

my_x_velo = 0
my_y_velo = 0
current_time = time.time()
my_x = 300
my_y = 200
othersX = 0
othersY = 0
frame_time = 0


def keyCheck():
    global my_x, my_y, my_x_velo, my_y_velo, current_time, frame_time
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    keys_press = pygame.key.get_pressed()
    if keys_press[pygame.K_LEFT]:
        my_x_velo -= RUN_SPEED_PPS
    if keys_press[pygame.K_RIGHT]:
        my_x_velo += RUN_SPEED_PPS
    if keys_press[pygame.K_UP]:
        my_y_velo -= RUN_SPEED_PPS
    if keys_press[pygame.K_DOWN]:
        my_y_velo += RUN_SPEED_PPS

    max = 100
    min = -100

    if my_x_velo >= max:
        my_x_velo = max
    elif my_x_velo <= min:
        my_x_velo = min
    if my_y_velo >= max:
        my_y_velo = max
    elif my_y_velo <= min:
        my_y_velo = min

    frame_time = time.time() - current_time
    current_time += frame_time

    my_x += my_x_velo * frame_time
    my_y += my_y_velo * frame_time

    if my_x >= width:
        my_x = width
        my_x_velo = 0
    elif my_x <= 0:
        my_x = 0
        my_x_velo = 0
    if my_y >= height:
        my_y = height
        my_y_velo = 0
    elif my_y <= 0:
        my_y = 0
        my_y_velo = 0


def receive():
    global othersX, othersY

    while True:
        client_location = client_socket.recv(SIZE)  # 클라이언트가 보낸 메시지 반환
        print('받은거 ' + client_location.decode())
        AllRex = r'^(.+)[ \t](.+)'
        RAll = re.compile(AllRex)
        MAll = RAll.search(client_location.decode())
        othersX = int(MAll.group(1))
        othersY = int(MAll.group(2))

        pygame.draw.circle(main_display, red, (othersX, othersY), 10)


def send():
    x = "%03d" % my_x
    y = "%03d" % my_y
    location = f'{x} {y}'
    print('보내는거 ' + location)
    client_socket.sendall(location.encode())


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind(ADDR)  # 주소 바인딩
    print('클라이언트를 기다리는 중')
    server_socket.listen()  # 클라이언트의 요청을 받을 준비
    client_socket, client_addr = server_socket.accept()
    print('준비완료')

    threading.Thread(target=receive).start()

    while True:
        main_display.fill(white)

        keyCheck()

        send()

        pygame.draw.circle(main_display, black, (my_x, my_y), 10)
        pygame.draw.circle(main_display, red, (othersX, othersY), 10)

        pygame.display.update()  # 화면을 업데이트한다
        clock.tick(fps)  # 화면 표시 회수 설정만큼 루프의 간격을 둔다
