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
blue = (0, 0, 255)
fps = 200

pygame.init()  # 초기화

pygame.display.set_caption('Two Balls')
main_display = pygame.display.set_mode((width, height), 0, 32)
clock = pygame.time.Clock()  # 시간 설정

PIXEL_PER_METER = (10.0 / 0.2)  # 10 pixel 20 cm
RUN_SPEED_KMPH = 0.6  # Km / Hour
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = int(RUN_SPEED_MPS * PIXEL_PER_METER)

FRICTION = int(RUN_SPEED_MPS / 3 * PIXEL_PER_METER * 30)

my_x_velo = 0
my_y_velo = 0
current_time = time.time()
my_x = 300
my_y = 200
othersX = 0
othersY = 0
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
othersBulletX = 0
othersBulletY = 0
my_hit = False
others_hit = False
frame_time = 1


def receive():
    global othersX, othersY, othersSight, othersBulletX, othersBulletY
    while True:
        client_location = client_socket.recv(SIZE)  # 클라이언트가 보낸 메시지 반환
        # print('받은거 ' + client_location.decode())
        AllRex = r'^(.+)[ \t](.+)[ \t](.+)[ \t](.+)'
        RAll = re.compile(AllRex)
        MAll = RAll.search(client_location.decode())
        othersX = int(MAll.group(1))
        othersY = int(MAll.group(2))
        othersBulletX = int(MAll.group(3))
        othersBulletY = int(MAll.group(4))
        # pygame.draw.circle(main_display, red, (othersX, othersY), 10)


def send():
    while True:
        x = "%03d" % my_x
        y = "%03d" % my_y
        bullet_x = "%03d" % fired_bullet_x
        bullet_y = "%03d" % fired_bullet_y
        location = f'{x} {y} {bullet_x} {bullet_y}'
        # print('보내는거 ' + location)
        client_socket.sendall(location.encode())
        time.sleep(0.005)


def connect_as_server():
    server_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_soc.bind(ADDR)  # 주소 바인딩
    print('클라이언트를 기다리는 중')
    server_soc.listen()  # 클라이언트의 요청을 받을 준비
    client_soc, client_addr = server_soc.accept()
    print('준비완료')
    return client_soc


def keyCheck():
    global my_x, my_y, my_x_velo, my_y_velo, current_time, SIGHT, bullet_fired, frame_time
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    keys_press = pygame.key.get_pressed()
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
    # if frame_time != 0:
    #     print(int(10000 / int(frame_time * 10000)))

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


def rebirth():
    global my_x, my_y
    my_x = width / 2
    my_y = height / 2


def crash_detect():
    global my_hit, others_hit
    my_hit = others_hit = False
    if my_x - 10 < othersBulletX < my_x + 10 and my_y - 10 < othersBulletY < my_y + 10:
        my_hit = True
        rebirth()


client_socket = connect_as_server()
threading.Thread(target=receive).start()
threading.Thread(target=send).start()

while True:
    main_display.fill(white)
    crash_detect()
    keyCheck()
    draw_my_bullet()
    draw_my_ball()
    draw_others_ball()

    pygame.display.update()  # 화면을 업데이트한다
    clock.tick(fps)  # 화면 표시 회수 설정만큼 루프의 간격을 둔다
