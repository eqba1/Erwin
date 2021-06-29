from threading import Thread
import threading
import select
import socket
import logging as log
import argparse as arg 
import sys
from protoc import Server_pb2
from google.protobuf.message import DecodeError

import GClient.Colorer

format = "%(asctime)s: %(message)s"
log.basicConfig(format=format, level=log.INFO, datefmt="%H:%M:%S")


def argumentPars():
    parser = arg.ArgumentParser(add_help=True)
    parser.add_argument("-sip", help="Server IP Address (default: 127.0.0.1)",metavar='ip', type=str)
    parser.add_argument("-sp", help="Server Port Number (default: 30008)",metavar='[1-65535]', type=str)
    args = parser.parse_args()

    if(args.sip == None and args.sp != None):
        return args.sp, "127.0.0.1"
    elif(args.sp == None and args.sip != None):
        return 30008, args.sip
    elif(args.sp == None and args.sip == None):
        return 30008, "127.0.0.1"

    return args.sp, args.sip


class Client(Thread):
    """
        Caption
    """
    def __init__(self, ip="127.0.0.1", port=30008 ): # user, pass
        Thread.__init__(self)
        self.ip = ip
        self.port = port

        # TCP / IPv4
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Socket Option
        self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.recv_thread = Recv(self.soc)

        self.__BUFFER_SIZE = 4096

        try:
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

            while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                if self.recv_thread.isStopped():
                    self.stop()
                    break
                line = sys.stdin.readline()
                if line:
                    self.soc.sendall(line[:-1].encode())
                else: # an empty line means stdin has been closed
                    print('eof')
                    exit(0)
            
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
                            log.info("From Server: %s", msg)
                        else :
                            log.info("From <(%s)> %s!", name,  msg)
        self.close()
 
    def messageCallback(self, data):
        incoming_data = Server_pb2.Client()
        try:
            # ParseFromString(data): parses a message from the given string.
            incoming_data.ParseFromString(data)
        except DecodeError:
            print(2) # TODO ?

        return incoming_data.name, incoming_data.port, incoming_data.msg

    # stop
    def stop(self):
        self.__stop = True
 
    def isStopped(self) -> bool:
        return self.__stop
    # close 
    def close(self):
        if self.soc:
            self.soc.close()
            self.soc = -1


if __name__ == '__main__':
    port, ip = argumentPars()
    log.info("Client IP:[%s], Port:[%s]", ip, port)
    
    client = Client(ip=ip, port=port)
    client.start()
    try:
        while True:
            
            if client.recv_thread.isStopped():
                print("Server is stopped")
                print('\nWait...')
                client.stop()
                client.recv_thread.join(2)
                client.join(2)
                print('End.')   
                break
            continue
    except KeyboardInterrupt:
        print('\nWait...')
        client.stop()
        client.recv_thread.join(2)
        client.join(2)
        print('End.')