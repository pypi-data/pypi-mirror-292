from vmipy.vmichannel import WebSocketChannel
import threading
import queue
import time
import json

class DevicePingMessage:
    def __init__(self,
                 interval=30,
                 ssh="",
                 jupyter="",
                 cpu=0,
                 memory=0,
                 disk=0,
                 macAddress="",
                 ip="",
                 running=0) -> None:
        self.interval = interval
        self.ssh = ssh
        self.jupyter = jupyter
        self.cpu = cpu
        self.memory = memory
        self.disk = disk
        self.macAddress = macAddress
        self.ip = ip
        self.running = running
    
    def toJson(self):
        return {
            "interval": self.interval,
            "ssh": self.ssh,
            "jupyter": self.jupyter,
            "cpu": self.cpu,
            "memory": self.memory,
            "disk": self.disk,
            "macAddress": self.macAddress,
            "ip": self.ip,
            "running": self.running
        }


class WSDeviceProtocolGen:
    @classmethod
    def GenD2CMessage(cls, deviceType, deviceId, payload):
        topic = "d2c/{0}/{1}/property".format(deviceType, deviceId)
        return {
            "jsonrpc": "2.0",
            "method": "internal.call",
            "params": {
                "topic": topic,
                "payload": payload
            }
        }
    @classmethod
    def GenD2CPingMessage(cls, deviceType, deviceId, pingMsg):
        topic = "d2cping/{0}/{1}".format(deviceType, deviceId)
        return {
            "jsonrpc": "2.0",
            "method": "internal.call",
            "params": {
                "topic": topic,
                "payload": pingMsg
            }
        }
    
class WSDevice:
    def __init__(self,serverIp, deviceType, deviceId):
        self._deviceType = deviceType
        self._deviceId = deviceId
        self._serverIp = serverIp
        self._wsUrl = "ws://{0}/ws/edge/iot?devicetype={1}&deviceid={2}".format(self._serverIp, self._deviceType, self._deviceId)
        self._wsChannel = WebSocketChannel(url=self._wsUrl)
        self._wsChannel.on_connect = self._onConnect
        self._wsChannel.on_disconnect = self._onDisconnected
        self._d2cThread = None
        self._pingThread = None
        self._connectEvent = threading.Event()
        self._connectEvent.clear()
        self._queue = queue.Queue()
        self._pingMsg = DevicePingMessage()
    
    def _onConnect(self, ws):
        self._connectEvent.set()

    def _onDisconnected(self, ws, close_code, close_msg):
        self._connectEvent.clear()

    def putD2cMessage(self, payload):
        self._queue.put(payload)

    def _sendPing(self):
        while True:
            if self._connectEvent.is_set() is False:
                time.sleep(3)
                continue
            pingMsg = WSDeviceProtocolGen.GenD2CPingMessage(self._deviceType, self._deviceId, self._pingMsg.toJson())
            self._wsChannel.Send(json.dumps(pingMsg))
            time.sleep(25)
    
    def _sendD2cMsg(self):
        while True:
            _ret = self._queue.get()
            if _ret is None:
                continue
            propDta = WSDeviceProtocolGen.GenD2CMessage(self._deviceType, self._deviceId, _ret)
            self._wsChannel.Send(json.dumps(propDta))
            

    def RunForever(self):
        self._pingThread = threading.Thread(target=self._sendPing, args=())
        self._pingThread.daemon = True
        self._pingThread.start()

        self._d2cThread = threading.Thread(target=self._sendD2cMsg, args=())
        self._d2cThread.daemon = True
        self._d2cThread.start()

        self._wsChannel.Run()