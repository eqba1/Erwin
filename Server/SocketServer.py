import Log.logger as logger
from threading import Thread
#import threading
import socket
from ClientHandler import ClientHandler, clients, client_threads

from protoc import Server_pb2

class SocketServer(Thread):

    """
    A subclass of Thread overriding the run() method.
    Setup the socket configuration for Server
    """

    def __init__(self, ip = "127.0.0.1", port=30008):
        # If the subclass overrides the constructor, it must make sure to invoke
        # the base class constructor (Thread.__init__()) before doing anything else to the thread.
        Thread.__init__(self)

        # create socket with type of TCP and IPv4 family 
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        #  socket.setsockopt(level, optname, value: buffer or int)
        self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.ip = ip
        self.port = port

        try:
            # Bind the socket to address
            self.soc.bind((ip, int(port)))
        except OSError:
            logger.error("Something goes wrong.")
            logger.warn("Try another IP or Port number.")
            exit(0)

        # Enable a server to accept connections
        self.soc.listen()

    # close the connection
    def close(self):
        for t in client_threads:
            t.stop()
            # Wait until the thread terminates
            t.join() 
        if self.soc:
            self.soc.close()
            
    # Method representing the thread’s activity.
    def run(self):
        self.__stop = False
        while not self.__stop:
            # Set a timeout on blocking socket operations.
            # The value argument can be a nonnegative floating point number expressing seconds
            self.soc.settimeout(1)

            try:
                # Accept a connection
                connection, addr = self.soc.accept()
                logger.warn("Client {} joined.".format(str(addr)))
                
                clients.append([addr, connection])
                
                print(len(clients))
                    
                # Send New User joined the Group
                for c in clients:
                    if c[0] != addr:
                        c[1].sendall(bytes(self.messageCallbackServer("New User joined the group.", "Server", 30005).SerializeToString())) 
                
            # timeout 
            except socket.timeout:
                connection = None # TODO #1
            
            # if have connection
            if connection:
                # Create a thread for new client
                client_thread = ClientHandler(connection, addr)
                client_threads.append(client_thread)
                client_thread.start()

        self.close()

    def stop(self):
        self.__stop = True

    # Create Message
    def messageCallbackServer(self, data, ip, port):
        message = Server_pb2.Client()
        message.msg = data
        message.name = ip
        message.port = int(port)
        return message
