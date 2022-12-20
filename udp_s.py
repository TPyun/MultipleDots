import socket
import numpy
import cv2
import socket_address

ADDR = socket_address.ADDR

msgFromServer       = "Hello UDP Client"
bytesToSend         = str.encode(msgFromServer)

# 데이터그램 소켓을 생성
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# 주소와 IP로 Bind
UDPServerSocket.bind(ADDR)

print("UDP server up and listening")

s = [b'\xff' * 46080 for x in range(20)]

fourcc = cv2.VideoWriter_fourcc(*'DIVX')
out = cv2.VideoWriter('output.avi', fourcc, 25.0, (640, 480))

while True:
    picture = b''

    data, addr = UDPServerSocket.recvfrom(46081)
    s[data[0]] = data[1:46081]

    if data[0] == 19:
        for i in range(20):
            picture += s[i]

        frame = numpy.fromstring(picture, dtype=numpy.uint8)
        frame = frame.reshape(480, 640, 3)
        cv2.imshow("frame", frame)
        out.write(frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break