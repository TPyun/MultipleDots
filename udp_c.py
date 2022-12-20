import socket
import cv2
import socket_address

SERVER_ADDR = socket_address.SERVER_ADDR

# 클라이언트 쪽에서 UDP 소켓 생성
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)


capture = cv2.VideoCapture(0)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 100)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 100)

while True:
    ret, frame = capture.read()
    d = frame.flatten()
    s = d.tostring()

    for i in range(20):
        UDPClientSocket.sendto(bytes([i]) + s[i*46080:(i+1)*46080], SERVER_ADDR)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
