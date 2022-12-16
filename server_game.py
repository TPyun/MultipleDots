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

IP = 'Server Internal IP'
PORT = Server port_number
SIZE = Size of sending data
ADDR = (IP, PORT)

"""

IP = socket_address.IP
PORT = socket_address.SERVER_PORT
SIZE = socket_address.SIZE
ADDR = socket_address.ADDR
BUFF_LEN = 1024

print(PORT, IP)
width = 600  # 상수 설정
height = 400
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
blue = (0, 0, 255)
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
fired_my_x_velo = 0
fired_my_y_velo = 0
sight = 270
fired_sight = 0
my_hp = 100

WAY_TO_SEE = 400
othersSight = 0
bullet_fired = False
shoot = False
fired_bullet_x = 0
fired_bullet_y = 0

quit_event = threading.Event()
players_info = {}
MY_ID = 0
POS_X = 0
POS_Y = 1
BULLET_POS_X = 2
BULLET_POS_Y = 3
HP = 4


def keyCheck():
    global my_x, my_y, my_x_velo, my_y_velo, current_time, sight, bullet_fired, frame_time
    keys_press = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == QUIT:
            print("quit")
            quit_event.set()
            pygame.quit()
            sys.exit()
    if keys_press[pygame.K_l]:
        print(players_info)

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


def draw_clients():
    for key, value in players_info.items():
        if key != 0 and value and value[HP] > 0:
            x = value[POS_X]
            y = value[POS_Y]
            bullet_x = value[BULLET_POS_X]
            bullet_y = value[BULLET_POS_Y]
            pygame.draw.circle(main_display, red, (bullet_x, bullet_y), 4)
            pygame.draw.circle(main_display, red, (x, y), 12)


def draw_me():
    global fired_sight, fired_bullet_x, fired_bullet_y, fired_my_x_velo, fired_my_y_velo, bullet_fired

    if players_info[MY_ID][HP] > 0:
        # draw my character
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


def check_hp():
    global my_x, my_y
    try:
        if players_info[MY_ID][HP] <= 0:
            my_x = width / 2
            my_y = height / 2
    except Exception as e:
        print("check hp 실패 " + str(e))


def collide_detect():
    try:
        for player, player_info in players_info.items():
            if player_info[HP] > 0:
                player_x = player_info[POS_X]
                player_y = player_info[POS_Y]
                for other_player, other_player_info in players_info.items():
                    if other_player != player and other_player_info[HP] > 0:
                        bullet_x = other_player_info[BULLET_POS_X]
                        bullet_y = other_player_info[BULLET_POS_Y]
                        if player_x - 10 < bullet_x < player_x + 10 and player_y - 10 < bullet_y < player_y + 10:
                            if player_info[HP] > 0:
                                player_info[HP] -= 100
    except Exception as e:
        print("collide detect fail " + str(e))


def listen():
    global server_soc
    listen_success = False
    while not listen_success:
        try:
            server_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_soc.bind(ADDR)  # 주소 바인딩
            server_soc.listen()  # 클라이언트의 요청을 받을 준비
            listen_success = True
            print('listen')
        except Exception as e:
            print("listen 하지 못함" + str(e))
            time.sleep(10)
            listen()


def accept_client():
    while True:
        print("accept 진입")

        players_info_json = json.dumps(players_info)
        send_info = players_info_json.encode()
        print("현재 players_info 전송 size: " + str(sys.getsizeof(send_info)))
        if server_soc:
            try:
                client_socket, client_addr = server_soc.accept()

                print(client_socket.getsockname())
                client_ip = client_addr[0]
                client_port = client_addr[1]

                print("client addr " + client_ip, client_port)

                players_info[client_port] = [-100, -100, -100, -100, 100]   # 플레이어를 dict에 추가
                print('준비완료')
                threading.Thread(target=send_and_recv, args=(client_socket, client_port)).start()
                print("thread 실행 시킴")
            except Exception as e:
                print("accept 실패" + str(e))


def send_and_recv(client_socket, client_port):
    # send client port
    client_socket.sendall(str(client_port).encode())
    print("send port to client")
    print(len(str(client_port).encode()))

    while True:
        if quit_event.is_set():
            return
        try:
            # send
            players_info_json = json.dumps(players_info)
            send_info = players_info_json.encode()
            client_socket.sendall(send_info)
            print(len(str(send_info)))
            # print("send info to client")

            # recv
            recv_info_json = client_socket.recv(BUFF_LEN).decode()
            recv_info = json.loads(recv_info_json.replace("'", "\""))
            player_hp = players_info[client_port][HP]
            recv_info.append(player_hp)
            players_info[client_port] = recv_info
            # print("recv info to client")

        except Exception as e:
            print("error occurred during send recv " + str(e))
            players_info.pop(client_port)
            return


def add_me():
    global my_hp
    try:
        my_hp = players_info[MY_ID][HP]
    except Exception as e:
        print("add me exception " + str(e))
    players_info[MY_ID] = [my_x, my_y, fired_bullet_x, fired_bullet_y, my_hp]


pygame.init()  # 초기화
pygame.display.set_caption('MultipleDots')
main_display = pygame.display.set_mode((width, height), 0, 32)
clock = pygame.time.Clock()  # 시간 설정

players_info[MY_ID] = [0, 0, 0, 0, 100]
server_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_soc.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, BUFF_LEN)

listen()
accept_thread = threading.Thread(target=accept_client)
accept_thread.daemon = True
accept_thread.start()

while True:
    main_display.fill(white)

    keyCheck()
    draw_me()
    if len(players_info) > 1:
        add_me()
        check_hp()
        collide_detect()
        draw_clients()

    pygame.display.update()  # 화면을 업데이트한다
    clock.tick(fps)  # 화면 표시 회수 설정만큼 루프의 간격을 둔다
