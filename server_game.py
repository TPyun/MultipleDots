import pygame  # pygame 모듈의 임포트
import sys  # 외장 모듈
from pygame.locals import *  # QUIT 등의 pygame 상수들을 로드한다.
import time
import threading
import multiprocessing
import socket
import socket_address
import math
import json

"""
socket_address.py

IP = 'Server Internal IP'
PORT = Server port_number
SIZE = Size of sending data
ADDR = (IP, PORT)

"""

IP = socket_address.IP
PORT = socket_address.SERVER_PORT
SIZE = socket_address.SIZE
ADDR = socket_address.ADDR

print(PORT, IP)
width = 600  # 상수 설정
height = 400
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
blue = (0, 0, 255)
fps = 200

pygame.init()  # 초기화

pygame.display.set_caption('2Dots')
main_display = pygame.display.set_mode((width, height), 0, 32)
clock = pygame.time.Clock()  # 시간 설정

PIXEL_PER_METER = (10.0 / 0.2)  # 10 pixel 20 cm
RUN_SPEED_KMPH = 0.6  # Km / Hour
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = int(RUN_SPEED_MPS * PIXEL_PER_METER)

FRICTION = int(RUN_SPEED_MPS / 3 * PIXEL_PER_METER * 30)


class PlayerInfo:
    def __init__(self):
        self.pos = [0, 0]
        self.velo = [0, 0]
        self.rot = 0
        self.bullet_pos = [0, 0]
        self.bullet_fired = False
        self.shoot = False


current_time = time.time()
my_x = 300
my_y = 200
my_x_velo = 0
my_y_velo = 0

othersX = 0
othersY = 500
othersBulletX = 0
othersBulletY = 500

SIGHT = 270
WAY_TO_SEE = 400
othersSight = 0
bullet_fired = False
shoot = False
fired_sight = 0

fired_bullet_x = 0
fired_bullet_y = 0
fired_my_x_velo = 0
fired_my_y_velo = 0

my_hit = False
others_hit = False
frame_time = 1
quit_event = threading.Event()

players_info = {}


def keyCheck():
    global my_x, my_y, my_x_velo, my_y_velo, current_time, SIGHT, bullet_fired, frame_time
    keys_press = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == QUIT:
            print("quit")
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
        SIGHT -= WAY_TO_SEE * frame_time
    if keys_press[pygame.K_d]:
        SIGHT += WAY_TO_SEE * frame_time

    degree = SIGHT / 360

    if degree < 0:
        SIGHT += 360
    elif degree > 1:
        SIGHT -= 360

    if keys_press[pygame.K_SPACE]:
        bullet_fired = True


def draw_my_ball():
    pygame.draw.circle(main_display, black, (my_x, my_y), 12)


def draw_others_ball():
    pygame.draw.circle(main_display, red, (othersBulletX, othersBulletY), 4)
    pygame.draw.circle(main_display, red, (othersX, othersY), 12)


def draw_my_bullet():
    global fired_sight, fired_bullet_x, fired_bullet_y, fired_my_x_velo, fired_my_y_velo, bullet_fired
    if not bullet_fired:
        degree = math.pi * 2 * SIGHT / 360
        bullet_x = 18 * math.cos(degree) + my_x
        bullet_y = 18 * math.sin(degree) + my_y
        pygame.draw.circle(main_display, black, (bullet_x, bullet_y), 4)

        fired_bullet_x = bullet_x
        fired_bullet_y = bullet_y
        fired_my_x_velo = my_x_velo
        fired_my_y_velo = my_y_velo
        fired_sight = SIGHT
    else:
        degree = math.pi * 2 * fired_sight / 360
        bullet_x_speed = math.cos(degree) * 500
        bullet_y_speed = math.sin(degree) * 500

        fired_bullet_x += (fired_my_x_velo + bullet_x_speed) * frame_time
        fired_bullet_y += (fired_my_y_velo + bullet_y_speed) * frame_time
        pygame.draw.circle(main_display, black, (fired_bullet_x, fired_bullet_y), 4)
        if fired_bullet_x < 0 or fired_bullet_x > width or fired_bullet_y < 0 or fired_bullet_y > height:
            bullet_fired = False


def respawn():
    global my_x, my_y
    my_x = width / 2
    my_y = height / 2


def crash_detect():
    global my_hit, others_hit
    my_hit = others_hit = False
    if my_x - 10 < othersBulletX < my_x + 10 and my_y - 10 < othersBulletY < my_y + 10:
        my_hit = True
        respawn()


def listen():
    global server_soc
    print('listen')
    server_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_soc.bind(ADDR)  # 주소 바인딩
    server_soc.listen()  # 클라이언트의 요청을 받을 준비


def accept_client():
    while True:
        print("accept 진입")
        if server_soc:
            try:
                client_socket, client_addr = server_soc.accept()

                print(client_socket.getsockname())
                client_ip = client_addr[0]
                client_port = client_addr[1]

                print(client_ip, client_port)

                players_info[client_port] = []   # 플레이어를 dict에 추가
                print('준비완료')
                threading.Thread(target=send_and_recv, args=(client_socket, client_port)).start()
                print("thread 실행 시킴")
            except Exception as e:
                print("accept 실패" + str(e))


def send_and_recv(client_socket, client_port):
    global othersX, othersY, othersSight, othersBulletX, othersBulletY
    while True:
        if quit_event.is_set():
            return
        try:
            # send client port
            client_socket.sendall(str(client_port).encode())

            # send
            players_info_json = json.dumps(players_info)
            # print("send: " + players_info_json)
            send_info = players_info_json.encode()
            print(sys.getsizeof(send_info))
            client_socket.sendall(send_info)

            # recv
            for key, value in players_info.items():
                if key == client_port:
                    recv_info_json = client_socket.recv(512).decode()

                    # print(type(recv_info_json))
                    recv_info = json.loads(recv_info_json.replace("'", "\""))
                    # print(type(recv_info_json), type(recv_info))
                    players_info[key] = recv_info
        except Exception as e:
            print("error occurred during send recv" + str(e))
            return


def add_me():
    players_info[0] = [my_x, my_y, fired_bullet_x, fired_bullet_y]


players_info[0] = []
server_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen()
threading.Thread(target=accept_client).start()

while True:
    main_display.fill(white)

    keyCheck()
    draw_my_bullet()
    draw_my_ball()
    add_me()

    pygame.display.update()  # 화면을 업데이트한다
    clock.tick(fps)  # 화면 표시 회수 설정만큼 루프의 간격을 둔다


