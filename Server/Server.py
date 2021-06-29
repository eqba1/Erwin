import argparse as arg 
# import threading
import Model.User as user
import Log.logger as logger 
from SocketServer import SocketServer
import Colorer

def argumentPars():
    """ 
    The Argument Parser of command-line interfaces for Server. 
    """ 
    parser = arg.ArgumentParser(prog='server', add_help=True)
    parser.add_argument("-ip", help="Set Server IP Address (default: 127.0.0.1)", metavar='ip', type=str)
    parser.add_argument("-p", help="Set Server Port Number (default: 30008)", metavar='[1-65535]', type=str)
    args = parser.parse_args()

    if(args.ip == None and args.p != None):
        return args.p, "127.0.0.1"
    elif(args.p == None and args.ip != None):
        return 30008, args.ip
    elif(args.p == None and args.ip == None):
        return 30008, "127.0.0.1"

    return args.p, args.ip

if __name__ == "__main__":

    port, ip = argumentPars()
    logger.warn("Server is Running on IP: {}, Port: {}".format(ip , port))

    server = SocketServer(ip=ip, port=port)
    user.add('Server', 'secret!')
    server.start()

    try:
        while True:
            continue

    except KeyboardInterrupt:
        print('\nWait...')
        server.stop()
        server.join()
        if server.soc:
            server.soc.close()
        print('End.')
