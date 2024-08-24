import asyncio
import base64
import json
import threading
import time
from typing import Dict, Callable

from socket_client import SocketClient
import snowflake_utils
from socket_client import get_local_ip
from enum import Enum


class ServiceType(Enum):
    GRPC = "grpc"
    HTTP = "http"
    GATEWAY = "gateway"
    DUBBO = "dubbo"


class messageType(Enum):
    INVOKE = "rpcProtocolInvoke"
    CONNECT = "clientConnect"
    DISCONNECT = "clientDisconnect"


class gwClient:

    def __init__(self, host, port):
        self.traceId = None
        self.appId = None
        self.method = None
        self.clientName = None
        self.serviceName = None
        self.ipAddress = get_local_ip()
        self.timeout = 30
        self.className = "java.lang.String"
        self.snowflakeClient = snowflake_utils.Snowflake(1, 1)
        self.applicationId = str(self.getSnowFlake())
        self.invokeParams = []
        self.finalRequest = dict()
        self.requestBody = dict()
        self.gatewayRequest = dict()
        self.serviceType = ServiceType.GRPC
        self.version = 'release-1.0.0'
        self.messageType = "rpcProtocolInvoke"
        self.socket_client = SocketClient(host, port)
        self.loop = asyncio.get_event_loop()
        self.running = True
        self.socket_client.connect()
        self.fnCallback = None
        # .CallbackType = Callable[[str], None]
        self.callbacks: Dict[str, Callable[[str], None]] = {}

    def __str__(self):
        return (f"gwClient(ipAddress={self.ipAddress}, serviceName={self.serviceName}, clientName={self.clientName},"
                f"method={self.method}, appId={self.appId})")

    def setIP(self, ipAddress):
        self.ipAddress = ipAddress
        return self

    def setVersion(self, version):
        self.version = version
        return self

    def setService(self, serviceName):
        self.serviceName = serviceName
        return self

    def setApplicationId(self, param):
        self.applicationId = param
        return self

    def setClient(self, clientName):
        self.clientName = clientName
        return self

    def setAppId(self, appId):
        self.appId = appId
        return self

    def setMethod(self, method):
        self.method = method
        return self

    def setTimeout(self, timeout):
        self.timeout = timeout
        return self

    def setServiceType(self, serviceType:ServiceType):
        self.serviceType = serviceType
        return self

    def dubbo(self):
        self.serviceType = ServiceType.DUBBO
        return self
    def gateway(self):
        self.serviceType = ServiceType.GATEWAY
        return self
    def http(self):
        self.serviceType = ServiceType.HTTP
        return self
    def rpc(self):
        self.serviceType = ServiceType.GRPC
        return self

    def setMessageType(self, messageType):
        self.messageType = messageType
        return self

    def getSnowFlake(self):
        return self.snowflakeClient.generate_id()

    def addInvokeRequestParam(self, paramName, paramValue):
        self.invokeParams.append(dict(name=paramName,
                                      className=self.className,
                                      jsonData=paramValue))
        return self

    def addInvokeRequestPostParam(self, paramValue):
        self.invokeParams.append(dict(name='HTTP_BODY',
                                      className=self.className,
                                      jsonData=json.dumps(paramValue)))
        return self

    def setGatewayRequest(self):
        self.traceId = self.getSnowFlake()
        self.callbacks[self.traceId] = self.fnCallback
        self.gatewayRequest = dict(clientIpAddress=self.ipAddress,
                                   serviceName=self.serviceName,
                                   clientName=self.clientName,
                                   methodId=self.method,
                                   appId=self.appId,
                                   version=self.version,
                                   applicationId=self.applicationId,
                                   timeout=self.timeout,
                                   serviceType=self.serviceType.name,
                                   invokeParams=self.invokeParams,
                                   id=self.traceId)
        return self

    def setRequestBody(self):
        if self.messageType in ['clientConnect', 'clientDisconnect']:
            self.requestBody = dict(id=self.applicationId)
        else:
            self.requestBody = dict(traceId=self.traceId, gatewayRequest=self.gatewayRequest)
        return self

    def setSendRequest(self):
        self.finalRequest = dict(type=self.messageType, message=json.dumps(self.requestBody))
        return self

    def sendRequest(self):
        self.setGatewayRequest()
        self.setRequestBody()
        self.setSendRequest()
        self.socket_client.send_data(json.dumps(self.finalRequest))

    def call(self):
        self.setMethod(method=self.method if self.method else 'call').setMessageType('rpcProtocolInvoke').sendRequest()
        # 接收数据
        while True:
            data = self.socket_client.receive_data()
            print(f"Received rpcProtocolInvoke from server: {data}")
            return data

    def asyncCall(self, fnCallback: Callable):
        self.fnCallback = fnCallback
        self.setMethod(method=self.method if self.method else 'asyncCall').setMessageType(
            'rpcProtocolInvoke').sendRequest()

    def clientConnect(self):
        threading.Thread(target=self.run_event_loop, daemon=True).start()
        self.setMessageType('clientConnect').sendRequest()

    def clientDisconnect(self):
        self.running = False
        self.setMessageType('clientDisconnect').sendRequest()

    def run_event_loop(self):
        try:
            self.loop.run_until_complete(self.receive_messages())
        except Exception as e:
            print(f"Error in event loop: {e}")
        finally:
            self.socket_client.close()

    async def receive_messages(self):
        while self.running:
            try:
                data = self.socket_client.receive_data()
                if data['type'] == 'invokeCallback':
                    traceId = json.loads(data['message'])['traceId']
                    if traceId in self.callbacks:
                        # 调用对应的回调函数处理响应
                        self.callbacks[traceId](data)
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

def image_to_base64(image_path):
    with open(image_path, 'rb') as image_file:
        image_data = image_file.read()
        base64_encoded = base64.b64encode(image_data)
        base64_string = base64_encoded.decode('utf-8')
        return base64_string


def callBack(message):
    print("CallBack", message)
