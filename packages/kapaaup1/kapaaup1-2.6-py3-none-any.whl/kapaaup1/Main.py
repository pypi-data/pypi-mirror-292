import cv2
import baiduasr
import time
import socket
import threading
from FaceRecognition import Face

socket_client = ''

step_while=0
step_flag=0

def TCPClient_Vision():
    global socket_client,step_flag
    socket_client = socket.socket()
    #socket_client.connect(('127.0.0.1',2001))
    socket_client.connect(('192.168.2.12',2001))
    while 1:
        data = socket_client.recv(1024).decode()
        print('djj get')
        print(data)
        time.sleep(0.1)
        step_flag = 0
        if(data == 'plc_yy_ok'):
            time.sleep(10)
            step_flag = 1
if __name__ == '__main__':
    th1 = threading.Thread(target=TCPClient_Vision)
    th1.setDaemon(1)
    th1.start()
    time.sleep(0.1)
    print("开始进行语音识别。")
    while True:
        input("请按下回车后下发语音指令：")
        msg = ''
        baiduasr.record()
        data = baiduasr.asr_updata()
        t = data.split(',')
        print(t)
        for i in range(len(t)):
            if '启动' in t[i]:
                msg='start'
                print(msg)
                socket_client.send(msg.encode())
                print("开始运行")
                name,confidence = Face()
                confidence = "{0}".format(round(confidence))
                print("您的名字是：",name)
                print("人脸匹配指数",confidence)
                faceimg = cv2.imread('./image.jpg')
                cv2.imshow('image',faceimg)
                cv2.waitKey(3000)
                cv2.destroyAllWindows()
                msg = 'face,'+str(confidence)
                socket_client.send(msg.encode())
            elif '二维码' in t[i]:
                msg = 'yy_plc_ewm'
                print(msg)
                socket_client.send(msg.encode())
            elif '数字' in t[i]:
                msg = 'yy_plc_sz'
                print(msg)
                socket_client.send(msg.encode())
            elif '空白' in t[i]:
                msg = 'yy_plc_kb'
                print(msg)
                socket_client.send(msg.encode())
            elif '人员' in t[i]:
                msg = 'yy_plc_ry'
                print(msg)
                socket_client.send(msg.encode())
            elif '物资' in t[i]:
                msg = 'yy_plc_ewm'
                print('物资1')
                socket_client.send(msg.encode())
                while step_flag==0:
                    step_while = step_while
                step_flag = 0
                msg = 'yy_plc_sz'
                print('物资2')
                socket_client.send(msg.encode())
                while step_flag==0:
                    step_while = step_while
                step_flag = 0
                msg = 'yy_plc_kb'
                print('物资3')
                socket_client.send(msg.encode())
                while step_flag==0:
                    step_while = step_while
                step_flag = 0
                msg = 'yy_plc_ry'
                print('物资4')
                socket_client.send(msg.encode())
                while step_flag==0:
                    step_while = step_while
                step_flag = 0




                