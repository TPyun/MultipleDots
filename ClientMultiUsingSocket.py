import pygame  # pygame 모듈의 임포트
import sys  # 외장 모듈
from pygame.locals import *  # QUIT 등의 pygame 상수들을 로드한다.
import time
import threading
import re
import socket
import socket_adress
import math

"""
socket_adress.py

SERVER_IP = 'Server External IP'
SERVER_PORT = Server port_number
SIZE = Size of sending data
SERVER_ADDR = (SERVER_IP, SERVER_PORT)

"""

SERVER_IP = socket_adress.SERVER_IP
SERVER_PORT = socket_adress.SERVER_PORT
SIZE = socket_adress.SIZE
SERVER_ADDR = socket_adress.SERVER_ADDR

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
RUN_SPEED_PPS = int(RUN_SPEED_MPS * PIXEL_PER_METER)

FRICTION = int(RUN_SPEED_MPS / 3 * PIXEL_PER_METER)

my_x_velo = 0
my_y_velo = 0
current_time = time.time()
my_x = 300
my_y = 200
othersX = 0
othersY = 0
SIGHT = 270
WAY_TO_SEE = 5
othersSight = 0


def keyCheck():
    global my_x, my_y, my_x_velo, my_y_velo, current_time, SIGHT
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

    if my_x_velo > 0:
        my_x_velo -= FRICTION
    elif my_x_velo < 0:
        my_x_velo += FRICTION
    if my_y_velo > 0:
        my_y_velo -= FRICTION
    elif my_y_velo < 0:
        my_y_velo += FRICTION

    max_vel = 100
    min_vel = -100

    if my_x_velo >= max_vel:
        my_x_velo = max_vel
    elif my_x_velo <= min_vel:
        my_x_velo = min_vel
    if my_y_velo >= max_vel:
        my_y_velo = max_vel
    elif my_y_velo <= min_vel:
        my_y_velo = min_vel

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

    if keys_press[pygame.K_a]:
        SIGHT -= WAY_TO_SEE
    if keys_press[pygame.K_d]:
        SIGHT += WAY_TO_SEE

    degree = SIGHT / 360

    if degree < 0:
        SIGHT += 360
    elif degree > 1:
        SIGHT -= 360


def receive():
    global othersX, othersY, othersSight
    while True:
        server_location = server_socket.recv(SIZE)  # 서버가 보낸 메시지 반환
        # print('받은거 ' + server_location.decode())
        AllRex = r'^(.+)[ \t](.+)[ \t](.+)'
        RAll = re.compile(AllRex)
        MAll = RAll.search(server_location.decode())
        othersX = int(MAll.group(1))
        othersY = int(MAll.group(2))
        othersSight = int(MAll.group(3))

        pygame.draw.circle(main_display, red, (othersX, othersY), 10)


def send():
    while True:
        x = "%03d" % my_x
        y = "%03d" % my_y
        s = "%03d" % SIGHT
        location = f'{x} {y} {s}'
        # print('보내는거 ' + location)
        server_socket.send(location.encode())
        time.sleep(0.005)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.connect(SERVER_ADDR)  # 서버에 접속
    print('접속됨')
    print(server_socket.getsockname())

    threading.Thread(target=receive).start()
    threading.Thread(target=send).start()

    while True:
        main_display.fill(white)

        keyCheck()

        pol_x = 18 * math.cos(math.pi * 2 * SIGHT / 360) + my_x
        pol_y = 18 * math.sin(math.pi * 2 * SIGHT / 360) + my_y
        pygame.draw.circle(main_display, black, (pol_x, pol_y), 4)
        pygame.draw.circle(main_display, black, (my_x, my_y), 12)

        others_sight_x = 18 * math.cos(math.pi * 2 * othersSight / 360) + othersX
        others_sight_y = 18 * math.sin(math.pi * 2 * othersSight / 360) + othersY
        pygame.draw.circle(main_display, red, (others_sight_x, others_sight_y), 4)
        pygame.draw.circle(main_display, red, (othersX, othersY), 12)

        pygame.display.update()  # 화면을 업데이트한다
        clock.tick(fps)  # 화면 표시 회수 설정만큼 루프의 간격을 둔다
