from flask import Flask
from flask_socketio import SocketIO, emit, send
from threading import Lock
#import os
from threading import Thread
import threading
import select
import socket
import logging as log


from protoc import Server_pb2
from google.protobuf.message import DecodeError
import Colorer


app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
thread = None
thread_lock = Lock()


format = "%(asctime)s: %(message)s"
log.basicConfig(format=format, level=log.INFO, datefmt="%H:%M:%S")

received_msg = []


class Client_thread(Thread):
    def __init__(self, ip="127.0.0.1", port=30008):
        # If the subclass overrides the constructor, it must make sure to invoke
        # the base class constructor (Thread.__init__()) before doing anything else to the thread.
        Thread.__init__(self)

        # server ip and port
        self.ip = ip
        self.port = port

        log.warn("port: " + str(port))

        # create socket with type of TCP and IPv4 family 
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        #  socket.setsockopt(level, optname, value: buffer or int)
        self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.recv_thread = Recv(self.soc)

        # buffer size
        self.__BUFFER_SIZE = 4096

        try:
            # connect to server
            self.soc.connect((ip, int(port)))
            self.recv_thread.start()
        except ConnectionRefusedError:
            log.error("Server is not available")
            exit(0)

    def close(self):
        if self.soc:
            self.soc.close()
            self.soc = -1

    def run(self):
        self.__stop = False
        while not self.__stop:            
            # Sending message
            if len(received_msg) == 1:
                val = received_msg[len(received_msg) - 1]["msg"]
                del received_msg[0]
                self.soc.sendall(val.encode())   
                log.warn("message is sent")

        self.close()
 
    def stop(self):
        self.__stop = True

class Recv(Thread):
    def __init__(self, soc):
        Thread.__init__(self)
        self.soc = soc
        self.__BUFFER_SIZE = 4096

    def run(self):
        self.__stop = False
        while not self.__stop:
                try:
                    ready, _, _ = select.select([self.soc,], [self.soc,], [], 5)
                except select.error:
                    self.stop()
                    return
                except ValueError:
                    break

                if len(ready) > 0:
                    incoming_data = b''
                    try:
                        incoming_data = self.soc.recv(self.__BUFFER_SIZE) # TODO #3
                    except ConnectionResetError:
                        log.error("Connection Reset Error")

                    # Check if socket has been closed
                    if incoming_data == b'':
                        log.info("Server disconnected.")
                        self.stop()

                    else:
                        name, _, msg = self.messageCallback(incoming_data)
                        if name == "Server":
                            socketio.emit('my response',
                            {'ip': str(name), 'content': msg, 'fromOthers': True})
                            log.info("From Server: %s", msg)
                        else :
                            socketio.emit('my response', 
                            {'ip': str(name), 'content': msg, 'fromOthers': True})
                            log.info("From <(%s)> %s!", name, msg)
        self.close()
 
    def messageCallback(self, data):
        incoming_data = Server_pb2.Client()
        try:
            incoming_data.ParseFromString(data)
        except DecodeError:
            print(2)
        return incoming_data.name, incoming_data.port, incoming_data.msg

    def stop(self):
        self.__stop = True
 
    def isStopped(self) -> bool:
        return self.__stop
    
    def close(self):
        if self.soc:
            self.soc.close()
            self.soc = -1




