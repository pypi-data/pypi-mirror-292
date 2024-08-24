import asyncio
import json
import socket
import logging as log
from queue import Queue


class SocketClient:
    def __init__(self, ip, port):
        self.client_socket = None
        self.ip = ip
        self.port = port
        self.timeout = 120
        self.rpcProtocolInvokeQueue = Queue()
        self.invokeCallbackQueue = Queue()
        self.is_busy = False
        self.loop = asyncio.get_event_loop()
        self.async_tasks = []
        self.total_data = bytes()

    def connect(self):
        while not self.client_socket:
            try:
                # 连接服务端
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024)
                self.client_socket.connect((self.ip, self.port))
                log.info("Connected to the server.")
            except (self.client_socket.timeout, ConnectionRefusedError) as e:
                log.exception(f"Connection failed: {e}")
                return False
            return True

    def heart_beat(self, data):
        log.info(f"Received heartbeat from server: {data}")
        heat_beat_data = json.loads(data)
        msg = json.loads(heat_beat_data['message'])
        msg['isBusy'] = self.is_busy
        heat_beat_data['message'] = json.dumps(msg)
        return_data = json.dumps(heat_beat_data)
        # 发送数据
        self.client_socket.sendall(return_data.encode('utf-8'))

    def send_data(self, data):
        if self.client_socket:
            try:
                # 发送数据
                log.info('send data: {}'.format(data))
                print('send data: {}'.format(data))
                self.client_socket.sendall(data.encode('utf-8'))
            except socket.timeout as e:
                log.exception(f"Send data failed: {e}")
                return False
            return True
        else:
            log.error('Socket not connected')
            raise RuntimeError("Socket not connected. Call connect() first.")

    def receive_data(self):

        if self.client_socket:
            try:
                # 接收数据
                while True:
                    data = self.client_socket.recv(1024)
                    self.total_data += data
                    if len(data) < 1024:
                        break
                receive_data = self.total_data.decode('utf-8')
                print('Receive data: {}'.format(receive_data))
                json_data = json.loads(receive_data)

                if json_data['type'] == "heartbeat":
                    self.heart_beat(receive_data)
                else:
                    return json_data

            except TimeoutError as e:
                log.exception(f"Receive heartbeat failed: {e}")
        else:
            log.error('Socket not connected')
            raise RuntimeError("Socket not connected. Call connect() first.")



    def close(self):
        if self.client_socket:
            self.client_socket.close()


def get_local_ip():
    res = socket.gethostbyname(socket.gethostname())
    if res.startswith("172"):
        return res
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # 尝试连接Google的公共DNS服务器
        # 使用这个地址是因为它不会真的发送任何数据，只是用来获取本地IP
        s.connect(('8.8.8.8', 1))
        # 获取socket的本地地址
        ip = s.getsockname()[0]
        return ip
    except:
        ip = '0.0.0.0'
        return ip
    finally:
        s.close()
