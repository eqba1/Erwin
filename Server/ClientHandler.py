import socket
import select
#import time
from threading import Thread
import Log.logger as logger
from protoc import Server_pb2
import hashlib

# Database 
import Model.User as user

# global list
clients = []
client_threads = []

class ClientHandler(Thread):
    def __init__(self, connection, addr):
        Thread.__init__(self)

        connection.sendall(bytes(self.messageCallbackServer("Welcome to my chatroom.", "Server", 30005).SerializeToString()))

        self.addr = addr
        self.connection = connection
        self.username = addr[0]

    def run(self):
        self.__stop = False
        self.check = False

        while not self.__stop:

            if self.connection:
                # Check if the client is still connected and if data is available:
                if(self.check == False):
                    self.check = self.Authentication(self.connection)

                if self.check == False:
                    for i in range(len(clients)):
                        if clients[i][0] == self.addr:
                            del clients[i] 
                    self.stop()

                try:
                    # ready for input                     
                    ready, _, _ = select.select([self.connection,], [self.connection,], [], 5)

                except select.error as err:
                    print(err)
                    self.stop()
                    return
 
                if len(ready) > 0:
                    
                    incoming_data = b''

                    try:
                        # Receive data from the socket. buffer size is 4KB
                        incoming_data = self.connection.recv(4096) # TODO #2
                    except ConnectionResetError:
                        logger.error("Connection Reset Error")

                    # Check if socket has been closed
                    if incoming_data == b'':
                        logger.warn("Client {} left us...".format(str(self.addr)))
                        
                        # remote disconnected user
                        for i in range(len(clients)):
                            if clients[i][0] == self.addr:
                                del clients[i] 
                                break
                            
                        self.stop()

                    else:
                        # logged in Server
                        logger.info("Received [{}] from Client [{}]".format(incoming_data.decode(), str(self.username)))

                        # Send Nobody in Chat Room Message
                        if len(clients) == 1:
                            self.notify()
                        
                        # Send incoming data for all client
                        for c in clients:
                            if c[0] != self.addr:
                                c[1].sendall(bytes(self.messageCallback(incoming_data).SerializeToString()))
            else:
                print("No client is connected, SocketServer can't receive data")
                self.stop()

        self.close()

    def Authentication(self, connection):

        # Send Welcome Message
        connection.send(bytes(self.messageCallbackServer("Enter Username", "Server", 30005).SerializeToString()))
        name = self.messageCallback(connection.recv(4096))

        connection.send(bytes(self.messageCallbackServer("Enter Password", "Server", 30005).SerializeToString()))
        password = self.messageCallback(connection.recv(4096))

        password = hashlib.sha256(str.encode(password.msg)).hexdigest() # Password hash using SHA256

        try:
            username = user.find(name.msg)
            # if username is empety create new user 
            if (username == []):
                user.add(name.msg, password)
                self.username = name.msg
                connection.send(self.messageCallbackServer("Registeration Successful", "Server", 30005).SerializeToString())
                validation = True
            # else username exist check it in database
            else:
                if(username[0][2] == password):
                    validation = True
                    self.username = username[0][1]
                    connection.send(self.messageCallbackServer("Connection Sucessful", "Server", 30005).SerializeToString())
                    print('{} Connected'.format(name))

                else:
                    connection.send(self.messageCallbackServer("Login Failed, Restart the Program and Try Agin", "Server", 30005).SerializeToString())
                    print('{} Connection denied'.format(name.msg))
                    validation = False
                    # remote disconnected user
                    
        except select.error as err:
            print(err)

        return validation

    # Decode Message 
    def messageCallback(self, data):
        message = Server_pb2.Client()
        message.msg = data
        message.name = self.username
        message.port = int(self.addr[1])
        return message  

    # Encode Message
    def messageCallbackServer(self, data, ip, port):
        message = Server_pb2.Client()
        message.msg = data
        message.name = ip
        message.port = int(port)
        return message

    # stop thread
    def stop(self):
        self.__stop = True

    # close connection 
    def close(self):
        if self.connection:
            self.connection.close()

    def notify(self):
        clients[0][1].sendall(bytes(self.messageCallbackServer("Nobody is in chatroom.", "Server", 30005).SerializeToString())) 
