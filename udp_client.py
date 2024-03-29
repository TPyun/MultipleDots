import pygame  # pygame 모듈의 임포트
import sys  # 외장 모듈
from pygame.locals import *  # QUIT 등의 pygame 상수들을 로드한다.
import time
import threading
import socket
import socket_address
import math
import json

"""
socket_address.py

SERVER_IP = 'Server External IP'
SERVER_PORT = Server port_number
SIZE = Size of sending data
SERVER_ADDR = (SERVER_IP, SERVER_PORT)

"""

SERVER_IP = socket_address.SERVER_IP
SERVER_PORT = socket_address.SERVER_PORT
SERVER_ADDR = socket_address.SERVER_ADDR

PLAYER_INFO_LEN = 23
PLAYERS_LIST_LEN = 512
ID_LEN = 5

width = 600  # 상수 설정
height = 400
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
fps = 120

PIXEL_PER_METER = (10.0 / 0.2)  # 10 pixel 20 cm
RUN_SPEED_KMPH = 0.6  # Km / Hour
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = int(RUN_SPEED_MPS * PIXEL_PER_METER)
FRICTION = int(RUN_SPEED_MPS / 3 * PIXEL_PER_METER * 30)

frame_time = 0
current_time = time.time()
my_x = 300
my_y = 200
my_x_velo = 0
my_y_velo = 0

sight = 270
WAY_TO_SEE = 400
othersSight = 0
bullet_fired = False
shoot = False
fired_sight = 0

fired_bullet_x = 0
fired_bullet_y = 0
fired_my_x_velo = 0
fired_my_y_velo = 0

connected = False
try_connect = False

quit_event = threading.Event()
players_info = {}
MY_ID = 0
POS_X = 0
POS_Y = 1
BULLET_POS_X = 2
BULLET_POS_Y = 3
HP = 4


def key_check():
    global my_x, my_y, my_x_velo, my_y_velo, current_time, sight, bullet_fired, frame_time

    for event in pygame.event.get():
        if event.type == QUIT:
            quit_event.set()
            pygame.quit()
            sys.exit()

    if keys_press[pygame.K_LEFT]:
        my_x_velo -= (RUN_SPEED_PPS * frame_time * 100)
    if keys_press[pygame.K_RIGHT]:
        my_x_velo += (RUN_SPEED_PPS * frame_time * 100)
    if keys_press[pygame.K_UP]:
        my_y_velo -= (RUN_SPEED_PPS * frame_time * 100)
    if keys_press[pygame.K_DOWN]:
        my_y_velo += (RUN_SPEED_PPS * frame_time * 100)

    if my_x_velo > 0:
        my_x_velo -= (FRICTION * frame_time)
    elif my_x_velo < 0:
        my_x_velo += (FRICTION * frame_time)
    if my_y_velo > 0:
        my_y_velo -= (FRICTION * frame_time)
    elif my_y_velo < 0:
        my_y_velo += (FRICTION * frame_time)
    # print(my_x_velo, RUN_SPEED_PPS * frame_time * 100)

    if 0 < pow(my_x_velo, 2) < 1:
        my_x_velo = 0
    if 0 < pow(my_y_velo, 2) < 1:
        my_y_velo = 0

    max_vel = 150
    min_vel = -150

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
        sight -= WAY_TO_SEE * frame_time
    if keys_press[pygame.K_d]:
        sight += WAY_TO_SEE * frame_time

    degree = sight / 360

    if degree < 0:
        sight += 360
    elif degree > 1:
        sight -= 360

    if keys_press[pygame.K_SPACE]:
        bullet_fired = True


def draw_others():
    for key, value in players_info.items():
        if key != MY_ID:
            x = value[POS_X]
            y = value[POS_Y]
            bullet_x = value[BULLET_POS_X]
            bullet_y = value[BULLET_POS_Y]
            pygame.draw.circle(main_display, red, (bullet_x, bullet_y), 4)
            pygame.draw.circle(main_display, red, (x, y), 12)


def draw_me():
    global fired_sight, fired_bullet_x, fired_bullet_y, fired_my_x_velo, fired_my_y_velo, bullet_fired
    try:
        pygame.draw.circle(main_display, black, (my_x, my_y), 12)

        # draw my bullet
        if not bullet_fired:
            degree = math.pi * 2 * sight / 360
            bullet_x = 18 * math.cos(degree) + my_x
            bullet_y = 18 * math.sin(degree) + my_y
            pygame.draw.circle(main_display, black, (bullet_x, bullet_y), 4)
            fired_bullet_x = bullet_x
            fired_bullet_y = bullet_y
            fired_my_x_velo = my_x_velo
            fired_my_y_velo = my_y_velo
            fired_sight = sight
        else:
            degree = math.pi * 2 * fired_sight / 360
            bullet_x_speed = math.cos(degree) * 500
            bullet_y_speed = math.sin(degree) * 500

            fired_bullet_x += (fired_my_x_velo + bullet_x_speed) * frame_time
            fired_bullet_y += (fired_my_y_velo + bullet_y_speed) * frame_time
            pygame.draw.circle(main_display, black, (fired_bullet_x, fired_bullet_y), 4)
            if fired_bullet_x < 0 or fired_bullet_x > width or fired_bullet_y < 0 or fired_bullet_y > height:
                bullet_fired = False

    except Exception as e:
        print("draw me 중에 예외 " + str(e))


def send_and_recv():
    global try_connect, players_info, MY_ID, connected
    connected = True

    while True:
        if quit_event.is_set():
            return
        try:
            # send
            my_info = [int(my_x), int(my_y), int(fired_bullet_x), int(fired_bullet_y)]
            send_info = json.dumps(my_info)
            # print(len(str(send_info.encode())))
            udp_socket.sendto(send_info.encode(), SERVER_ADDR)

            # recv
            encoded_recv = udp_socket.recvfrom(1024)
            encoded_recv_info = encoded_recv[0]
            address = encoded_recv[1]
            recv_info = encoded_recv_info.decode()
            recv_info_port = json.loads(recv_info.replace("'", "\""))
            recv_info = recv_info_port[0]
            MY_ID = str(recv_info_port[1])
            # print(recv_info_port)
            players_info = recv_info

        except Exception as e:
            print("send recv 중에 예외 발생" + str(e))
            try_connect = False
            connected = False
            return


pygame.init()  # 초기화
pygame.display.set_caption('MultipleDots')
main_display = pygame.display.set_mode((width, height), 0, 32)
clock = pygame.time.Clock()  # 시간 설정

players_info[MY_ID] = [-100, -100, -100, -100, 100]

udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

send_recv_thread = threading.Thread(target=send_and_recv)
send_recv_thread.daemon = True
send_recv_thread.start()

while True:
    if quit_event.is_set():
        break
    keys_press = pygame.key.get_pressed()

    # if server_socket and keys_press[pygame.K_x] and connected is True:
    #     server_socket.close()
    #     connected = False
    #     try_connect = False
    #     print("connecting false")

    main_display.fill(white)
    key_check()

    draw_me()
    if connected:
        draw_others()

    pygame.display.update()  # 화면을 업데이트한다
    clock.tick(fps)  # 화면 표시 회수 설정만큼 루프의 간격을 둔다


SERVER_ADDR = socket_address.SERVER_ADDR
